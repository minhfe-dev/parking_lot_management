"""
Vietnamese License Plate OCR
═════════════════════════════
Dùng EasyOCR. Nếu có PyTorch + CUDA, Reader chạy trên GPU (tự phát hiện);
đặt biến môi trường EASYOCR_GPU=0 để ép CPU, EASYOCR_GPU=1 để ép GPU.

Pipeline:
  1. Detect & crop vùng biển số (OpenCV) nếu ảnh lớn
  2. Tiền xử lý ảnh → 4 biến thể
  3. Gọi easyocr.read_text() cho từng biến thể
  4. Correction ký tự theo vị trí VN
  5. Scoring → trả về kết quả tốt nhất
"""

import os
import re
import logging
from dataclasses import dataclass
from typing import Optional

import cv2
import numpy as np
import easyocr

logger = logging.getLogger(__name__)
_reader = None
_reader_gpu_flag = None


def _env_wants_gpu() -> Optional[bool]:
    v = os.environ.get("EASYOCR_GPU", "").strip().lower()
    if v in ("1", "true", "yes", "on"):
        return True
    if v in ("0", "false", "no", "off"):
        return False
    return None


def _cuda_available() -> bool:
    try:
        import torch

        return bool(torch.cuda.is_available())
    except Exception:
        return False


def _use_gpu() -> bool:
    forced = _env_wants_gpu()
    if forced is not None:
        return forced
    return _cuda_available()


def _get_reader():
    global _reader, _reader_gpu_flag
    want_gpu = _use_gpu()
    if _reader is None or _reader_gpu_flag != want_gpu:
        _reader = easyocr.Reader(["en"], gpu=want_gpu)
        _reader_gpu_flag = want_gpu
        logger.info("EasyOCR Reader khởi tạo (gpu=%s)", want_gpu)
    return _reader

# ══════════════════════════════════════════════
# Constants
# ══════════════════════════════════════════════
EXPECTED_PLATE_LENGTH    = 8
MIN_PLATE_LENGTH         = 5
MAX_PLATE_LENGTH         = 10
PLATE_ASPECT_MIN         = 1.5
PLATE_ASPECT_MAX         = 6.5
PLATE_AREA_MIN           = 600
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


# Bước 1 — Detect & crop vùng biển số
def _is_plate_shaped(x, y, w, h) -> bool:
    if w * h < PLATE_AREA_MIN:
        return False
    aspect = w / max(h, 1)
    return PLATE_ASPECT_MIN <= aspect <= PLATE_ASPECT_MAX


def _pad_crop(img: np.ndarray, x, y, w, h, pad: int = 8) -> np.ndarray:
    H, W = img.shape[:2]
    return img[max(0, y-pad):min(H, y+h+pad),
               max(0, x-pad):min(W, x+w+pad)]


def _dedupe_boxes(boxes: list[tuple], iou_thresh: float = 0.6) -> list[tuple]:
    """
    Loại box trùng lặp theo IoU để OCR nhanh hơn trên CPU.
    """
    if not boxes:
        return []

    def iou(a, b):
        ax1, ay1, aw, ah, _ = a
        bx1, by1, bw, bh, _ = b
        ax2, ay2 = ax1 + aw, ay1 + ah
        bx2, by2 = bx1 + bw, by1 + bh

        ix1, iy1 = max(ax1, bx1), max(ay1, by1)
        ix2, iy2 = min(ax2, bx2), min(ay2, by2)
        if ix2 <= ix1 or iy2 <= iy1:
            return 0.0
        inter = (ix2 - ix1) * (iy2 - iy1)
        union = aw * ah + bw * bh - inter
        return inter / max(union, 1)

    boxes = sorted(boxes, key=lambda c: c[4], reverse=True)
    kept = []
    for cand in boxes:
        if all(iou(cand, k) < iou_thresh for k in kept):
            kept.append(cand)
    return kept


def _deskew(gray: np.ndarray) -> np.ndarray:
    """
    Sửa nghiêng nhẹ để tăng OCR cho ảnh chụp lệch.
    """
    edges = cv2.Canny(gray, 60, 180)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=40, minLineLength=40, maxLineGap=10)
    if lines is None:
        return gray

    angles = []
    for l in lines[:50]:
        x1, y1, x2, y2 = l[0]
        angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
        if -20 <= angle <= 20:
            angles.append(angle)
    if not angles:
        return gray

    median_angle = float(np.median(angles))
    if abs(median_angle) < 1.0:
        return gray

    h, w = gray.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), median_angle, 1.0)
    return cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


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

    found = _dedupe_boxes(found)
    crops = [_pad_crop(img, *c[:4]) for c in found[:6]]
    crops.append(img)  # fallback luôn thử ảnh gốc để tránh miss
    logger.debug("Detect %d vùng biển số", len(crops))
    return crops



# Bước 2 — Tiền xử lý ảnh
def _scale_target_height() -> int:
    """GPU: phóng to thêm một chút để tận dụng tốc độ inference."""
    return 128 if _use_gpu() else 96


def _scale_up(gray: np.ndarray, target_h: Optional[int] = None) -> np.ndarray:
    if target_h is None:
        target_h = _scale_target_height()
    h, w = gray.shape[:2]
    if h < target_h:
        scale = target_h / h
        gray  = cv2.resize(gray, (int(w*scale), target_h),
                           interpolation=cv2.INTER_CUBIC)
    return gray


def preprocess_variants(crop: np.ndarray) -> list[np.ndarray]:
    """Trả về nhiều biến thể để OCR vote tốt hơn trên CPU."""
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY) if len(crop.shape) == 3 else crop.copy()
    gray = _scale_up(gray)
    gray = _deskew(gray)

    clahe_obj = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    clahe     = clahe_obj.apply(gray)
    denoised  = cv2.fastNlMeansDenoising(clahe, h=12)
    sharpened = cv2.GaussianBlur(denoised, (0, 0), 1.2)
    sharpened = cv2.addWeighted(denoised, 1.7, sharpened, -0.7, 0)
    binary    = cv2.adaptiveThreshold(
        sharpened, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 31, 1,
    )
    otsu = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return [gray, clahe, denoised, sharpened, binary, cv2.bitwise_not(binary), otsu]


# Bước 3 — Correction & Scoring
def _correct(raw: str) -> str:
    """Sửa ký tự nhầm theo từng zone biển số VN."""
    cleaned = re.sub(r"[^A-Za-z0-9]", "", raw.upper())
    if len(cleaned) < MIN_PLATE_LENGTH:
        return ""
    if len(cleaned) > MAX_PLATE_LENGTH:
        # ưu tiên đoạn cuối vì serial thường nằm cuối và OCR hay dính tiền tố rác
        cleaned = cleaned[-MAX_PLATE_LENGTH:]

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


# Result
@dataclass
class PlateResult:
    formatted: str    # "51A-12345"
    corrected: str    # "51A12345"
    raw:       str    # text thô từ OCR
    score:     int


# Bước 4 — Parse kết quả read_text()
def _parse_readtext(results) -> list[tuple[str, float]]:
    """readtext() trả về list of (bbox, text, confidence)."""
    texts = []
    for item in results:
        if isinstance(item, (list, tuple)) and len(item) >= 3:
            txt = str(item[1])
            try:
                conf = float(item[2])
            except Exception:
                conf = 0.5
            texts.append((txt, conf))
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            texts.append((str(item[1]), 0.5))
        elif isinstance(item, str):
            texts.append((item, 0.5))
    return texts

# Public API
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
                    raw_results = _get_reader().readtext(
                        variant,
                        detail=1,
                        paragraph=False,
                        allowlist="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ.-",
                        decoder="beamsearch",
                    )
                except Exception:
                    logger.debug("readtext() lỗi", exc_info=True)
                    continue

                for text, conf in _parse_readtext(raw_results):
                    corrected = _correct(text)
                    if not corrected:
                        continue
                    # phối hợp score ngữ nghĩa + độ tin cậy OCR
                    s = _score(corrected) + int(max(0.0, min(1.0, conf)) * 10)
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


# CLI
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