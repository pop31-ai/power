"""Motion utilities — детекция движения между кадрами."""

import cv2
import numpy as np


def detect_motion(frame1, frame2, threshold=25, min_area=100):
    """Сравнивает два кадра, возвращает контуры движущихся объектов."""
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(gray1, gray2)
    _, thresh = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)
    kernel = np.ones((5, 5), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return [c for c in contours if cv2.contourArea(c) > min_area]


def motion_amount(frame1, frame2):
    """Возвращает общую площадь движения в пикселях."""
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(gray1, gray2)
    return float(np.sum(diff > 25))


def detect_shake(frames, window=5):
    """Детектит тряску экрана: max смещение за window кадров."""
    if len(frames) < window:
        return 0, 0
    gray = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in frames[-window:]]
    max_dx, max_dy = 0, 0
    for i in range(1, len(gray)):
        # Use template matching to find shift
        result = cv2.matchTemplate(gray[i - 1], gray[i], cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        # Calculate shift from center
        h, w = gray[i].shape
        dx = max_loc[0] - w // 2
        dy = max_loc[1] - h // 2
        max_dx = max(max_dx, abs(dx))
        max_dy = max(max_dy, abs(dy))
    return max_dx, max_dy


def measure_speed(frame1, frame2, contour):
    """Ищет контур на frame2, возвращает скорость (px/кадр)."""
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    x, y, w, h = cv2.boundingRect(contour)
    template = gray1[y : y + h, x : x + w]
    if template.size == 0:
        return 0, 0
    result = cv2.matchTemplate(gray2, template, cv2.TM_CCOEFF_NORMED)
    _, _, _, max_loc = cv2.minMaxLoc(result)
    dx = max_loc[0] - x
    dy = max_loc[1] - y
    return dx, dy
