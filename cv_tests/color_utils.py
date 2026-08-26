"""Color utilities — HSV детекция объектов по цвету."""

import cv2
import numpy as np


def find_by_color(img, hsv_lower, hsv_upper, min_area=50):
    """Находит контуры объектов по HSV-диапазону."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array(hsv_lower), np.array(hsv_upper))
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return [c for c in contours if cv2.contourArea(c) > min_area]


def count_objects_by_color(img, hsv_lower, hsv_upper, min_area=50):
    """Считает количество объектов заданного цвета."""
    return len(find_by_color(img, hsv_lower, hsv_upper, min_area))


# === Predefined color ranges (HSV) ===

# Cosmic Bubbles — purple/black hole
BLACK_HOLE_HSV = ([120, 50, 50], [160, 255, 255])

# Rig Master — green (Г-блоки)
BLOCK_G_HSV = ([35, 100, 100], [85, 255, 255])

# Rig Master — blue (В-блоки)
BLOCK_V_HSV = ([100, 100, 100], [130, 255, 255])

# Rig Master — anchor A (green)
ANCHOR_A_HSV = ([35, 100, 100], [85, 255, 255])

# Rig Master — anchor B (red)
ANCHOR_B_HSV = ([0, 100, 100], [10, 255, 255])

# Shatter Zone — bubble (various bright colors)
BUBBLE_HSV = ([0, 100, 100], [180, 255, 255])

# Shatter Zone — block colors (bright)
BLOCK_HSV = ([0, 80, 100], [180, 255, 255])
