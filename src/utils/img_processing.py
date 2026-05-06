import cv2
import re
import easyocr

_reader = None

def preprocess(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    return gray


def _get_reader():
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(["en"], gpu=False)
    return _reader


def _normalize_plate(text):
    cleaned = re.sub(r"[^A-Za-z0-9]", "", text.upper())
    if len(cleaned) < 6:
        return ""
    return cleaned


def extract_plate(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return ""

    gray = preprocess(img)
    results = _get_reader().readtext(gray, detail=0)
    if not results:
        return ""

    candidates = []
    for text in results:
        plate = _normalize_plate(text)
        if plate:
            candidates.append(plate)

    if not candidates:
        return ""

    candidates.sort(key=lambda p: abs(len(p) - 8))
    return candidates[0]