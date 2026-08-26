"""Shatter Zone — CV-тесты для US-SZ.1 … US-SZ.19"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from capture import screenshot, click, wait, save_screenshot
from ocr_utils import text_exists, read_number, read_text
from color_utils import count_objects_by_color, BUBBLE_HSV, BLOCK_HSV
from motion_utils import motion_amount
from results import TestResult, TestSuite

suite = TestSuite("Shatter Zone")


def test_sz01():
    """SZ-01: Overlay — OCR 'SHATTER ZONE'."""
    r = TestResult("SZ-01", "Shatter Zone", "Overlay — текст найден")
    img = screenshot()
    save_screenshot(img, "results/sz01_overlay.png")
    if text_exists(img, "SHATTER ZONE"):
        return r.ok("Текст 'SHATTER ZONE' найден")
    return r.fail("Overlay текст не найден")


def test_sz02():
    """SZ-02: HUD — SCORE, LEVEL, SHOTS."""
    r = TestResult("SZ-02", "Shatter Zone", "HUD — 3 элемента")
    img = screenshot()
    save_screenshot(img, "results/sz02_hud.png")
    found = sum(1 for kw in ["SCORE", "LEVEL", "SHOTS"] if text_exists(img, kw))
    if found >= 3:
        return r.ok(f"Найдено {found}/3 HUD элементов")
    return r.fail(f"Найдено {found}/3 HUD элементов")


def test_sz03():
    """SZ-03: Клик по bubble → shards."""
    r = TestResult("SZ-03", "Shatter Zone", "Shard-контуры после клика")
    img1 = screenshot()
    import cv2
    h, w = img1.shape[:2]
    # Count bubble-colored objects
    bubbles = count_objects_by_color(img1, *BUBBLE_HSV, min_area=80)
    if not bubbles:
        return r.fail("Нет пузырей на экране")
    # Click the largest bubble
    largest = max(bubbles, key=cv2.contourArea)
    M = cv2.moments(largest)
    if M["m00"] == 0:
        return r.fail("Не удалось вычислить центр пузыря")
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])
    click(cx, cy)
    wait(0.3)
    img2 = screenshot()
    # Detect shards — many small bright objects
    shards = count_objects_by_color(img2, *BUBBLE_HSV, min_area=10)
    if shards > 10:
        return r.ok(f"Найдено {shards} shard-объектов")
    return r.fail(f"Найдено {shards} shard-объектов (ожидалось >10)")


def test_sz04():
    """SZ-04: SHOTS уменьшился после клика."""
    r = TestResult("SZ-04", "Shatter Zone", "SHOTS: -1 после выстрела")
    img_before = screenshot()
    shots_before = read_number(img_before, (450, 0, 100, 35))
    # Click a bubble
    bubbles = count_objects_by_color(img_before, *BUBBLE_HSV, min_area=80)
    if bubbles:
        import cv2
        largest = max(bubbles, key=cv2.contourArea)
        M = cv2.moments(largest)
        if M["m00"] > 0:
            click(int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"]))
            wait(0.3)
    img_after = screenshot()
    shots_after = read_number(img_after, (450, 0, 100, 35))
    if shots_before and shots_after and shots_after < shots_before:
        return r.ok(f"SHOTS: {shots_before} → {shots_after}")
    return r.fail(f"SHOTS не изменился: {shots_before} → {shots_after}")


def test_sz11():
    """SZ-11: LEVEL CLEAR! — OCR."""
    r = TestResult("SZ-11", "Shatter Zone", "LEVEL CLEAR! текст")
    img = screenshot()
    if text_exists(img, "LEVEL CLEAR"):
        return r.ok("'LEVEL CLEAR!' найден")
    return r.fail("'LEVEL CLEAR!' не найден (требуется прохождение уровня)")


def test_sz18():
    """SZ-18: Restart — SCORE = 0."""
    r = TestResult("SZ-18", "Shatter Zone", "Restart: SCORE=0")
    img = screenshot()
    score = read_number(img, (100, 0, 100, 35))
    if score == 0:
        return r.ok("SCORE = 0 после рестарта")
    return r.fail(f"SCORE = {score} (ожидалось 0)")


ALL_TESTS = [test_sz01, test_sz02, test_sz03, test_sz04, test_sz11, test_sz18]


def run_all():
    for test_fn in ALL_TESTS:
        try:
            result = test_fn()
            suite.add(result)
        except Exception as e:
            doc = test_fn.__doc__ or "SZ"
            tid = doc.split(":")[0].strip().replace('"""', '').strip()
            suite.add(TestResult(tid, "Shatter Zone", str(e)).fail(str(e)))
    suite.print_report()
    suite.save("results/shatter_zone_report.json")
    return suite.summary()


if __name__ == "__main__":
    run_all()
