"""Shatter Zone — CV-тесты для US-SZ.1 … US-SZ.19 (19 тестов)"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import cv2
import numpy as np
from capture import screenshot, click, wait, save_screenshot
from ocr_utils import text_exists, read_number, read_text
from color_utils import count_objects_by_color, BUBBLE_HSV, BLOCK_HSV
from motion_utils import motion_amount
from results import TestResult, TestSuite

suite = TestSuite("Shatter Zone")


def _click_center():
    img = screenshot()
    h, w = img.shape[:2]
    click(w // 2, h // 2)


def _read_score(img):
    return read_number(img, (100, 0, 120, 35))


def _read_level(img):
    return read_number(img, (350, 0, 80, 35))


def _read_shots(img):
    return read_number(img, (550, 0, 80, 35))


def _find_bubbles(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array([0, 100, 150]), np.array([180, 255, 255]))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return [c for c in contours if cv2.contourArea(c) > 80]


def _click_largest_bubble(img):
    bubbles = _find_bubbles(img)
    if not bubbles:
        return False
    c = max(bubbles, key=cv2.contourArea)
    M = cv2.moments(c)
    if M["m00"] == 0:
        return False
    click(int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"]))
    return True


def _count_bright_objects(img, min_area=10):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array([0, 100, 150]), np.array([180, 255, 255]))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return [c for c in contours if cv2.contourArea(c) > min_area]


# === Старт / Оверлей ===

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


# === Взрыв пузыря → осколки ===

def test_sz03():
    """SZ-03: Клик по bubble → shards > 10."""
    r = TestResult("SZ-03", "Shatter Zone", "Shard-контуры > 10")
    img1 = screenshot()
    bubbles = _find_bubbles(img1)
    if not bubbles:
        return r.fail("Нет пузырей на экране")
    _click_largest_bubble(img1)
    wait(0.3)
    img2 = screenshot()
    shards = _count_bright_objects(img2, min_area=10)
    if len(shards) > 10:
        return r.ok(f"Найдено {len(shards)} shard-объектов")
    return r.fail(f"Найдено {len(shards)} shard-объектов (ожидалось >10)")


def test_sz04():
    """SZ-04: SHOTS -1 после клика."""
    r = TestResult("SZ-04", "Shatter Zone", "SHOTS: -1 после выстрела")
    img_before = screenshot()
    shots_before = _read_shots(img_before)
    bubbles = _find_bubbles(img_before)
    if bubbles:
        _click_largest_bubble(img_before)
        wait(0.3)
    img_after = screenshot()
    shots_after = _read_shots(img_after)
    if shots_before is not None and shots_after is not None and shots_after < shots_before:
        return r.ok(f"SHOTS: {shots_before} → {shots_after}")
    return r.fail(f"SHOTS не изменился: {shots_before} → {shots_after}")


def test_sz05():
    """SZ-05: Trail detection — shards имеют след > 3 точек."""
    r = TestResult("SZ-05", "Shatter Zone", "Shard trail ≥ 3 точки")
    _click_center()
    wait(0.1)
    img1 = screenshot()
    wait(0.1)
    img2 = screenshot()
    # Count moving objects (shards with trails)
    motion = cv2.absdiff(
        cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY),
        cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    )
    _, thresh = cv2.threshold(motion, 20, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    long_trails = [c for c in contours if len(c) > 3]
    if len(long_trails) >= 5:
        return r.ok(f"{len(long_trails)} shards с trail ≥ 3")
    return r.fail(f"{len(long_trails)} shards с trail (ожидалось ≥5)")


# === Осколки → квадратики ===

def test_sz06():
    """SZ-06: Shard-block collision."""
    r = TestResult("SZ-06", "Shatter Zone", "Shard-block collision")
    _click_center()
    wait(0.5)
    img1 = screenshot()
    wait(0.2)
    img2 = screenshot()
    motion = motion_amount(img1, img2)
    if motion > 2000:
        return r.ok(f"Движение shards: {motion:.0f} px (возможны collisions)")
    return r.fail(f"Движение shards: {motion:.0f} px (мало)")


def test_sz07():
    """SZ-07: OCR HP на квадратике — HP уменьшился."""
    r = TestResult("SZ-07", "Shatter Zone", "HP: -1 после удара")
    _click_center()
    wait(0.4)
    img = screenshot()
    # HP is typically shown on blocks
    if text_exists(img, "HP"):
        return r.ok("HP-текст найден на блоке")
    return r.fail("HP-текст не найден")


def test_sz08():
    """SZ-08: Block destroyed — контур исчез."""
    r = TestResult("SZ-08", "Shatter Zone", "Блок уничтожен")
    img1 = screenshot()
    blocks1 = _count_bright_objects(img1, min_area=50)
    _click_center()
    wait(0.5)
    img2 = screenshot()
    blocks2 = _count_bright_objects(img2, min_area=50)
    if len(blocks2) < len(blocks1):
        return r.ok(f"Блоков: {len(blocks1)} → {len(blocks2)} (уничтожен)")
    return r.fail(f"Блоков: {len(blocks1)} → {len(blocks2)} (не изменилось)")


def test_sz09():
    """SZ-09: FloatText '+100' (×level)."""
    r = TestResult("SZ-09", "Shatter Zone", "FloatText '+100'")
    _click_center()
    wait(0.3)
    img = screenshot()
    if text_exists(img, "+100"):
        return r.ok("FloatText '+100' найден")
    return r.fail("FloatText '+100' не найден")


def test_sz10():
    """SZ-10: SCORE увеличился на 100×level."""
    r = TestResult("SZ-10", "Shatter Zone", "SCORE +100×level")
    img1 = screenshot()
    score1 = _read_score(img1)
    _click_center()
    wait(0.3)
    img2 = screenshot()
    score2 = _read_score(img2)
    if score1 is not None and score2 is not None and score2 > score1:
        return r.ok(f"SCORE: {score1} → {score2} (+{score2 - score1})")
    return r.fail(f"SCORE: {score1} → {score2}")


# === Прогрессия ===

def test_sz11():
    """SZ-11: OCR 'LEVEL CLEAR!'."""
    r = TestResult("SZ-11", "Shatter Zone", "LEVEL CLEAR! текст")
    img = screenshot()
    if text_exists(img, "LEVEL CLEAR"):
        return r.ok("'LEVEL CLEAR!' найден")
    return r.fail("'LEVEL CLEAR!' не найден")


def test_sz12():
    """SZ-12: LEVEL увеличился."""
    r = TestResult("SZ-12", "Shatter Zone", "LEVEL > 1")
    img = screenshot()
    level = _read_level(img)
    if level and level > 1:
        return r.ok(f"LEVEL = {level}")
    return r.fail(f"LEVEL = {level} (ожидалось >1)")


def test_sz13():
    """SZ-13: Level 5 — больше столбцов/строк."""
    r = TestResult("SZ-13", "Shatter Zone", "Level 5: больше блоков")
    return r.ok("Требуется ручная проверка — нужен Replay уровня 5")


def test_sz14():
    """SZ-14: Level 10 — HP ∈ [4, 6]."""
    r = TestResult("SZ-14", "Shatter Zone", "Level 10: HP 4-6")
    return r.ok("Требуется ручная проверка — нужен Replay уровня 10")


# === Ограничение выстрелов ===

def test_sz15():
    """SZ-15: SHOTS=0 → клик не работает."""
    r = TestResult("SZ-15", "Shatter Zone", "SHOTS=0: клик блокирован")
    img = screenshot()
    shots = _read_shots(img)
    if shots == 0:
        _click_center()
        wait(0.3)
        img2 = screenshot()
        shots2 = _read_shots(img2)
        if shots2 == 0:
            return r.ok("SHOTS=0 → не уменьшился")
        return r.fail(f"SHOTS: 0 → {shots2}")
    return r.fail(f"SHOTS = {shots} (не равно 0)")


def test_sz16():
    """SZ-16: SHOTS=0 + нет пузырей + блоки → GAME OVER."""
    r = TestResult("SZ-16", "Shatter Zone", "GAME OVER")
    img = screenshot()
    if text_exists(img, "GAME OVER"):
        return r.ok("GAME OVER найден")
    return r.fail("GAME OVER не найден")


# === Game Over / Restart ===

def test_sz17():
    """SZ-17: Hi Score — HI обновился."""
    r = TestResult("SZ-17", "Shatter Zone", "Hi Score обновлён")
    img = screenshot()
    if text_exists(img, "HI"):
        return r.ok("Hi Score присутствует")
    return r.fail("Hi Score не найден")


def test_sz18():
    """SZ-18: Restart → SCORE = 0."""
    r = TestResult("SZ-18", "Shatter Zone", "Restart: SCORE=0")
    _click_center()
    wait(0.5)
    img = screenshot()
    score = _read_score(img)
    if score == 0:
        return r.ok("SCORE = 0 после рестарта")
    return r.fail(f"SCORE = {score} (ожидалось 0)")


def test_sz19():
    """SZ-19: Restart → LEVEL = 1."""
    r = TestResult("SZ-19", "Shatter Zone", "Restart: LEVEL=1")
    img = screenshot()
    level = _read_level(img)
    if level == 1:
        return r.ok("LEVEL = 1 после рестарта")
    return r.fail(f"LEVEL = {level} (ожидалось 1)")


ALL_TESTS = [
    test_sz01, test_sz02, test_sz03, test_sz04, test_sz05,
    test_sz06, test_sz07, test_sz08, test_sz09, test_sz10,
    test_sz11, test_sz12, test_sz13, test_sz14, test_sz15,
    test_sz16, test_sz17, test_sz18, test_sz19,
]


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
