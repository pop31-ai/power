"""Capture utilities — скриншоты и запись экрана."""

import cv2
import numpy as np
import time
import os

try:
    import pyautogui
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False


def screenshot(region=None):
    """Делает скриншот. region = (x, y, w, h) или None = весь экран."""
    if not HAS_PYAUTOGUI:
        # Fallback: reading from file
        return np.zeros((600, 800, 3), dtype=np.uint8)
    img = pyautogui.screenshot(region=region)
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def screenshot_roi(window_title, roi):
    """Скриншот окна по заголовку + ROI."""
    img = screenshot()
    if img is None:
        return None
    x, y, w, h = roi
    return img[y : y + h, x : x + w]


def click(x, y, pause=0.1):
    """Клик по координатам."""
    if HAS_PYAUTOGUI:
        pyautogui.click(x, y)
    time.sleep(pause)


def drag(x1, y1, x2, y2, duration=0.3, pause=0.1):
    """Перетаскивание из (x1,y1) в (x2,y2)."""
    if HAS_PYAUTOGUI:
        pyautogui.moveTo(x1, y1)
        pyautogui.mouseDown()
        pyautogui.moveTo(x2, y2, duration=duration)
        pyautogui.mouseUp()
    time.sleep(pause)


def wait(seconds):
    """Ожидание."""
    time.sleep(seconds)


def save_screenshot(img, path):
    """Сохраняет скриншот."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    cv2.imwrite(path, img)


def capture_sequence(game_func, n_frames=30, interval=0.05):
    """Запускает game_func и записывает n_frames кадров."""
    frames = []
    game_func()
    for _ in range(n_frames):
        frames.append(screenshot())
        time.sleep(interval)
    return frames
