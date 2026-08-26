"""OCR utilities — обёртка над pytesseract для чтения текста со скриншотов."""

import cv2
import numpy as np

try:
    import pytesseract
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False


def read_text(img, roi=None, config="--psm 7"):
    """Читает текст из изображения (или ROI)."""
    if not HAS_TESSERACT:
        return ""
    if roi:
        x, y, w, h = roi
        img = img[y : y + h, x : x + w]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return pytesseract.image_to_string(thresh, config=config).strip()


def read_number(img, roi=None):
    """Читает число из изображения."""
    text = read_text(img, roi, config="--psm 7 -c tessedit_char_whitelist=0123456789")
    try:
        return int("".join(c for c in text if c.isdigit()))
    except ValueError:
        return None


def find_text_region(img, target, roi=None):
    """Ищет текст на скриншоте, возвращает bounding box или None."""
    if not HAS_TESSERACT:
        return None
    if roi:
        x, y, w, h = roi
        img = img[y : y + h, x : x + w]
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    for i, text in enumerate(data["text"]):
        if target.lower() in text.lower():
            bx = data["left"][i]
            by = data["top"][i]
            bw = data["width"][i]
            bh = data["height"][i]
            if roi:
                bx += roi[0]
                by += roi[1]
            return (bx, by, bw, bh)
    return None


def text_exists(img, target, roi=None):
    """Проверяет существует ли текст на скриншоте."""
    return find_text_region(img, target, roi) is not None


def read_all_hud(img, y_range=(0, 60)):
    """Читает все HUD элементы в верхней полосе."""
    x1, y1, x2, y2 = (0, y_range[0], img.shape[1], y_range[1])
    roi = (x1, y1, x2 - x1, y2 - y1)
    return read_text(img, roi, config="--psm 6")
