"""
Vietnamese License Plate OCR
═════════════════════════════
Dùng easyocr.read_text() làm OCR engine.

Pipeline:
  1. Detect & crop vùng biển số (OpenCV) nếu ảnh lớn
  2. Tiền xử lý ảnh → 4 biến thể
  3. Gọi easyocr.read_text() cho từng biến thể
  4. Correction ký tự theo vị trí VN
  5. Scoring → trả về kết quả tốt nhất
"""

import re
import logging
from dataclasses import dataclass

import cv2
import numpy as np
import easyocr

logger = logging.getLogger(__name__)
_reader = None


def _get_reader():
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(["en"], gpu=False)
    return _reader

# ══════════════════════════════════════════════
# Constants
# ══════════════════════════════════════════════
EXPECTED_PLATE_LENGTH    = 8
MIN_PLATE_LENGTH         = 5
PLATE_ASPECT_MIN         = 1.5
PLATE_ASPECT_MAX         = 6.5
PLATE_AREA_MIN           = 800
FULL_IMAGE_HEIGHT_THRESH = 200   # px — cao hơn này → coi là ảnh cả xe

VALID_PROVINCE_CODES = {
    "11","12","14","15","17","18","19",
    "20","21","22","23","24","25","26",
    "29","30","31","32","33","34","35","36","37","38",
    "40","41","42","43","47","48","49",
    "51","52","53","54","55","56","57","58","59",
    "60","61","62","63","64","65","66","67","68","69",
    "70","71","72","73","74","75","76","77","78","79",
    "81","82","83","84","85","86","88","89",
    "90","92","93","94","95","97","98","99",
}

DIGIT_CORRECTIONS = str.maketrans({
    "O":"0","o":"0","I":"1","l":"1","i":"1",
    "Z":"2","S":"5","B":"8","G":"6","T":"7",
})
LETTER_CORRECTIONS = str.maketrans({
    "0":"O","1":"I","5":"S","8":"B","6":"G",
})

VN_PATTERNS = [
    re.compile(r"^(\d{2})([A-Z])(\d{4,5})$"),    # xe con
    re.compile(r"^(\d{2})([A-Z]\d)(\d{4})$"),     # xe máy
    re.compile(r"^(\d{2})([A-Z]{2})(\d{4})$"),    # xe điện
]


# ══════════════════════════════════════════════
# Bước 1 — Detect & crop vùng biển số
# ══════════════════════════════════════════════
def _is_plate_shaped(x, y, w, h) -> bool:
    if w * h < PLATE_AREA_MIN:
        return False
    aspect = w / max(h, 1)
    return PLATE_ASPECT_MIN <= aspect <= PLATE_ASPECT_MAX


def _pad_crop(img: np.ndarray, x, y, w, h, pad: int = 8) -> np.ndarray:
    H, W = img.shape[:2]
    return img[max(0, y-pad):min(H, y+h+pad),
               max(0, x-pad):min(W, x+w+pad)]


def detect_plate_regions(img: np.ndarray) -> list[np.ndarray]:
    """
    Tìm vùng biển số bằng 2 phương pháp OpenCV, trả về top-5 crops.
    Nếu không detect được → trả về ảnh gốc để fallback.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    found: list[tuple] = []

    # Phương pháp 1: Sobel ngang → đóng morphology → contour
    sobel  = cv2.convertScaleAbs(cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3))
    _, th1 = cv2.threshold(sobel, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    k1     = cv2.getStructuringElement(cv2.MORPH_RECT, (17, 3))
    cl1    = cv2.morphologyEx(th1, cv2.MORPH_CLOSE, k1)
    for c in cv2.findContours(cl1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]:
        x, y, w, h = cv2.boundingRect(c)
        if _is_plate_shaped(x, y, w, h):
            found.append((x, y, w, h, w*h))

    # Phương pháp 2: Canny + dilate → contour
    blur   = cv2.GaussianBlur(gray, (5, 5), 0)
    canny  = cv2.Canny(blur, 50, 150)
    k2     = cv2.getStructuringElement(cv2.MORPH_RECT, (12, 4))
    cl2    = cv2.morphologyEx(canny, cv2.MORPH_CLOSE, k2)
    for c in cv2.findContours(cl2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]:
        x, y, w, h = cv2.boundingRect(c)
        if _is_plate_shaped(x, y, w, h):
            found.append((x, y, w, h, w*h))

    if not found:
        logger.debug("Không detect được biển số → fallback ảnh gốc")
        return [img]

    found.sort(key=lambda c: c[4], reverse=True)
    crops = [_pad_crop(img, *c[:4]) for c in found[:5]]
    logger.debug("Detect %d vùng biển số", len(crops))
    return crops


# ══════════════════════════════════════════════
# Bước 2 — Tiền xử lý ảnh
# ══════════════════════════════════════════════
def _scale_up(gray: np.ndarray, target_h: int = 80) -> np.ndarray:
    h, w = gray.shape[:2]
    if h < target_h:
        scale = target_h / h
        gray  = cv2.resize(gray, (int(w*scale), target_h),
                           interpolation=cv2.INTER_CUBIC)
    return gray


def preprocess_variants(crop: np.ndarray) -> list[np.ndarray]:
    """Trả về 4 biến thể để OCR vote."""
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY) if len(crop.shape) == 3 else crop.copy()
    gray = _scale_up(gray)

    clahe_obj = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    clahe     = clahe_obj.apply(gray)
    denoised  = cv2.fastNlMeansDenoising(clahe, h=15)
    binary    = cv2.adaptiveThreshold(
        denoised, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 31, 2,
    )
    return [gray, clahe, binary, cv2.bitwise_not(binary)]


# ══════════════════════════════════════════════
# Bước 3 — Correction & Scoring
# ══════════════════════════════════════════════
def _correct(raw: str) -> str:
    """Sửa ký tự nhầm theo từng zone biển số VN."""
    cleaned = re.sub(r"[^A-Za-z0-9]", "", raw.upper())
    if len(cleaned) < MIN_PLATE_LENGTH:
        return ""

    province = cleaned[:2].translate(DIGIT_CORRECTIONS)

    rest, series, idx = cleaned[2:], "", 0
    while idx < len(rest) and idx < 2:
        ch = rest[idx]
        corrected_ch = ch.translate(LETTER_CORRECTIONS) if ch.isdigit() else ch
        if not corrected_ch.isalpha():
            break
        series += corrected_ch
        idx    += 1
        if idx < len(rest) and rest[idx].isdigit():
            series += rest[idx]; idx += 1
            break

    serial = rest[idx:].translate(DIGIT_CORRECTIONS)
    return province + series + serial


def _format(plate: str) -> str:
    for pat in VN_PATTERNS:
        m = pat.match(plate)
        if m:
            province, series, serial = m.groups()
            return f"{province}{series}-{serial}"
    return plate


def _score(plate: str) -> int:
    s = re.sub(r"[^A-Z0-9]", "", plate.upper())
    score = 0
    if s[:2] in VALID_PROVINCE_CODES:
        score += 10
    for pat in VN_PATTERNS:
        if pat.match(s):
            score += 20; break
    score -= abs(len(s) - EXPECTED_PLATE_LENGTH)
    return score


# ══════════════════════════════════════════════
# Result
# ══════════════════════════════════════════════
@dataclass
class PlateResult:
    formatted: str    # "51A-12345"
    corrected: str    # "51A12345"
    raw:       str    # text thô từ OCR
    score:     int


# ══════════════════════════════════════════════
# Bước 4 — Parse kết quả read_text()
# ══════════════════════════════════════════════
def _parse_readtext(results) -> list[str]:
    """readtext() trả về list of (bbox, text, confidence)."""
    texts = []
    for item in results:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            texts.append(str(item[1]))
        elif isinstance(item, str):
            texts.append(item)
    return texts


# ══════════════════════════════════════════════
# Public API
# ══════════════════════════════════════════════
def extract_plate(image_path: str) -> PlateResult | None:
    """
    Đọc ảnh → detect biển số → OCR → correction → PlateResult tốt nhất.
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            logger.warning("Không đọc được ảnh: %s", image_path)
            return None

        is_full = img.shape[0] > FULL_IMAGE_HEIGHT_THRESH
        regions = detect_plate_regions(img) if is_full else [img]

        best: dict[str, PlateResult] = {}

        for crop in regions:
            for variant in preprocess_variants(crop):
                try:
                    raw_results = _get_reader().readtext(variant)
                except Exception:
                    logger.debug("readtext() lỗi", exc_info=True)
                    continue

                for text in _parse_readtext(raw_results):
                    corrected = _correct(text)
                    if not corrected:
                        continue
                    s      = _score(corrected)
                    result = PlateResult(
                        formatted=_format(corrected),
                        corrected=corrected,
                        raw=text,
                        score=s,
                    )
                    if corrected not in best or s > best[corrected].score:
                        best[corrected] = result

        if not best:
            logger.info("Không tìm được biển số trong: %s", image_path)
            return None

        winner = max(best.values(), key=lambda r: r.score)
        logger.info("Biển số: %s (score=%d)", winner.formatted, winner.score)
        return winner

    except Exception:
        logger.exception("Lỗi xử lý: %s", image_path)
        return None


def extract_plate_from_array(img: np.ndarray) -> PlateResult | None:
    """Nhận numpy array thay vì đường dẫn — tiện cho video/stream."""
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        tmp = f.name
    try:
        cv2.imwrite(tmp, img)
        return extract_plate(tmp)
    finally:
        os.unlink(tmp)


# ══════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s | %(message)s")

    if len(sys.argv) < 2:
        print("Dùng: python img_processing.py <đường_dẫn_ảnh>")
        sys.exit(1)

    result = extract_plate(sys.argv[1])
    if result:
        print(f"\n Biển số   : {result.formatted}")
        print(f"   Corrected : {result.corrected}")
        print(f"   Raw OCR   : {result.raw}")
        print(f"   Score     : {result.score}")
    else:
        print("\n Không nhận diện được biển số.")