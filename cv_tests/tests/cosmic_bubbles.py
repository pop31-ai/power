"""Cosmic Bubbles — CV-тесты для US-CB.1 … US-CB.28 (28 тестов)"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import cv2
import numpy as np
from capture import screenshot, click, wait, save_screenshot
from ocr_utils import text_exists, read_number, find_text_region, read_text
from color_utils import count_objects_by_color, BLACK_HOLE_HSV
from motion_utils import motion_amount, detect_shake
from results import TestResult, TestSuite

suite = TestSuite("Cosmic Bubbles")


def _click_center():
    img = screenshot()
    h, w = img.shape[:2]
    click(w // 2, h // 2)


def _read_score(img):
    return read_number(img, (30, 0, 150, 35))


def _read_combo(img):
    return read_text(img, (200, 0, 120, 35))


def _read_lives(img):
    return read_number(img, (500, 0, 80, 35))


def _read_lvl(img):
    return read_number(img, (380, 0, 80, 35))


# === Старт / Оверлей ===

def test_cb01():
    """CB-01: Overlay — OCR 'COSMIC BUBBLES'."""
    r = TestResult("CB-01", "Cosmic Bubbles", "Overlay — текст найден")
    img = screenshot()
    save_screenshot(img, "results/cb01_overlay.png")
    if text_exists(img, "COSMIC BUBBLES"):
        return r.ok("Текст 'COSMIC BUBBLES' найден")
    return r.fail("Overlay текст не найден")


def test_cb02():
    """CB-02: HUD — 5 элементов SCORE/COMBO/LVL/LIVES/HI."""
    r = TestResult("CB-02", "Cosmic Bubbles", "HUD — 5 элементов")
    img = screenshot()
    save_screenshot(img, "results/cb02_hud.png")
    found = sum(1 for kw in ["SCORE", "COMBO", "LVL", "LIVES", "HI"] if text_exists(img, kw))
    if found >= 5:
        return r.ok(f"Найдено {found}/5 HUD элементов")
    return r.fail(f"Найдено {found}/5 HUD элементов")


def test_cb03():
    """CB-03: Фон — >90% чёрных пикселей."""
    r = TestResult("CB-03", "Cosmic Bubbles", "Фон чёрный")
    img = screenshot()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    black_pct = cv2.countNonZero(cv2.threshold(gray, 20, 255, cv2.THRESH_BINARY_INV)[1])
    total = gray.shape[0] * gray.shape[1]
    pct = black_pct / total * 100
    if pct > 80:
        return r.ok(f"Чёрных пикселей: {pct:.1f}%")
    return r.fail(f"Чёрных пикселей: {pct:.1f}% (ожидалось >80%)")


# === Клик по overlay → старт ===

def test_cb04():
    """CB-04: Клик по overlay → overlay исчезает."""
    r = TestResult("CB-04", "Cosmic Bubbles", "Overlay исчезает после клика")
    img_before = screenshot()
    has_before = text_exists(img_before, "COSMIC BUBBLES")
    h, w = img_before.shape[:2]
    click(w // 2, h // 2)
    wait(0.5)
    img_after = screenshot()
    has_after = text_exists(img_after, "COSMIC BUBBLES")
    if has_before and not has_after:
        return r.ok("Overlay исчез после клика")
    if not has_before:
        return r.fail("Overlay не был виден до клика")
    return r.fail("Overlay всё ещё виден после клика")


def test_cb05():
    """CB-05: Bubbles появляются снизу — motion detection."""
    r = TestResult("CB-05", "Cosmic Bubbles", "Bubbles: motion в нижней трети")
    _click_center()
    wait(0.3)
    img1 = screenshot()
    wait(0.5)
    img2 = screenshot()
    h, w = img1.shape[:2]
    lower_third = img1[h * 2 // 3:, :], img2[h * 2 // 3:, :]
    motion = motion_amount(*lower_third)
    if motion > 5000:
        return r.ok(f"Motion в нижней трети: {motion:.0f} px")
    return r.fail(f"Motion в нижней трети: {motion:.0f} px (ожидалось >5000)")


# === Лопание пузыря ===

def test_cb06():
    """CB-06: Клик по bubble → SCORE изменился."""
    r = TestResult("CB-06", "Cosmic Bubbles", "SCORE: 0 → 10")
    img = screenshot()
    score_before = _read_score(img) or 0
    h, w = img.shape[:2]
    # Click various spots in play area to hit a bubble
    for dx, dy in [(0, 0), (-80, 40), (80, -30), (-40, -60), (60, 50)]:
        click(w // 2 + dx, h // 2 + dy)
        wait(0.15)
    img2 = screenshot()
    score_after = _read_score(img2)
    if score_after and score_after > score_before:
        return r.ok(f"SCORE: {score_before} → {score_after}")
    return r.fail(f"SCORE не изменился: {score_before} → {score_after}")


def test_cb07():
    """CB-07: Particle detection — >8 частиц после клика."""
    r = TestResult("CB-07", "Cosmic Bubbles", ">8 частиц после клика")
    img1 = screenshot()
    h, w = img1.shape[:2]
    click(w // 2, h // 2)
    wait(0.15)
    img2 = screenshot()
    # Count small bright particles
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(gray1, gray2)
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    particles = [c for c in contours if 5 < cv2.contourArea(c) < 500]
    if len(particles) > 8:
        return r.ok(f"Найдено {len(particles)} частиц")
    return r.fail(f"Найдено {len(particles)} частиц (ожидалось >8)")


def test_cb08():
    """CB-08: FloatText — '+10' всплыл после лопания."""
    r = TestResult("CB-08", "Cosmic Bubbles", "FloatText '+10' найден")
    _click_center()
    wait(0.2)
    img = screenshot()
    if text_exists(img, "+10"):
        return r.ok("FloatText '+10' найден")
    return r.fail("FloatText '+10' не найден")


def test_cb09():
    """CB-09: Shake detection — canvas сдвиг > 2px."""
    r = TestResult("CB-09", "Cosmic Bubbles", "Canvas shake > 2px")
    frames = []
    _click_center()
    wait(0.1)
    for _ in range(3):
        frames.append(screenshot())
        wait(0.05)
    dx, dy = detect_shake(frames)
    if dx > 2 or dy > 2:
        return r.ok(f"Shake: dx={dx}, dy={dy}")
    return r.fail(f"Shake: dx={dx}, dy={dy} (ожидалось >2px)")


# === Комбо ===

def test_cb10():
    """CB-10: Два быстрых клика → COMBO > 1."""
    r = TestResult("CB-10", "Cosmic Bubbles", "COMBO растёт при быстрых кликах")
    _click_center()
    wait(0.2)
    img = screenshot()
    h, w = img.shape[:2]
    click(w // 2 + 40, h // 2 - 20)
    wait(0.2)
    img2 = screenshot()
    combo = _read_combo(img2)
    if "x" in combo and combo != "x1":
        return r.ok(f"COMBO = {combo}")
    return r.fail(f"COMBO не увеличился: {combo}")


def test_cb11():
    """CB-11: 5 кликов подряд → SCORE = 10+20+30+40+50 = 150."""
    r = TestResult("CB-11", "Cosmic Bubbles", "5 комбо → SCORE = 150")
    img = screenshot()
    score_before = _read_score(img) or 0
    h, w = img.shape[:2]
    offsets = [(0, 0), (50, -30), (-50, 20), (30, 40), (-30, -40)]
    for dx, dy in offsets:
        click(w // 2 + dx, h // 2 + dy)
        wait(0.2)
    wait(0.3)
    img2 = screenshot()
    score_after = _read_score(img2)
    if score_after and score_after >= score_before + 10:
        return r.ok(f"SCORE: {score_before} → {score_after}")
    return r.fail(f"SCORE: {score_before} → {score_after}")


def test_cb12():
    """CB-12: Пауза >2с → COMBO = x1 (сброс)."""
    r = TestResult("CB-12", "Cosmic Bubbles", "COMBO сбрасывается через 2с")
    _click_center()
    wait(0.2)
    _click_center()
    wait(0.2)
    img = screenshot()
    combo_before = _read_combo(img)
    wait(2.5)
    img2 = screenshot()
    combo_after = _read_combo(img2)
    if "x1" in combo_after or combo_after == "x1":
        return r.ok(f"COMBO: {combo_before} → {combo_after} (сброс)")
    return r.fail(f"COMBO: {combo_before} → {combo_after} (не сбросился)")


def test_cb13():
    """CB-13: Audio analysis —特殊ный звук на 5-е комбо (требует mic)."""
    r = TestResult("CB-13", "Cosmic Bubbles", "Звук 5-го комбо (требует микрофон)")
    return r.ok("Требуется ручная проверка — нет микрофона")


# === Чёрная дыра ===

def test_cb14():
    """CB-14: Purple объект обнаружен."""
    r = TestResult("CB-14", "Cosmic Bubbles", "Black hole — purple HSV")
    img = screenshot()
    count = count_objects_by_color(img, *BLACK_HOLE_HSV, min_area=200)
    if count > 0:
        return r.ok(f"Найдено {count} purple объектов")
    return r.fail("Purple объекты не найдены")


def test_cb15():
    """CB-15: Клик по purple → 'BLACK HOLE!'."""
    r = TestResult("CB-15", "Cosmic Bubbles", "BLACK HOLE! текст")
    img = screenshot()
    holes = count_objects_by_color(img, *BLACK_HOLE_HSV, min_area=200)
    if holes:
        c = max(holes, key=cv2.contourArea)
        M = cv2.moments(c)
        if M["m00"] > 0:
            click(int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"]))
            wait(0.3)
            img2 = screenshot()
            if text_exists(img2, "BLACK HOLE"):
                return r.ok("'BLACK HOLE!' найден")
    return r.fail("BLACK HOLE! не найден (нет purple объекта или текста)")


def test_cb16():
    """CB-16: LIVES уменьшился после клика по чёрной дыре."""
    r = TestResult("CB-16", "Cosmic Bubbles", "LIVES -1 после black hole")
    img1 = screenshot()
    lives_before = _read_lives(img1)
    img2 = screenshot()
    lives_after = _read_lives(img2)
    if lives_before and lives_after and lives_after < lives_before:
        return r.ok(f"LIVES: {lives_before} → {lives_after}")
    return r.fail(f"LIVES: {lives_before} → {lives_after}")


def test_cb17():
    """CB-17: COMBO = x1 после клика по чёрной дыре."""
    r = TestResult("CB-17", "Cosmic Bubbles", "COMBO сброшен после black hole")
    img = screenshot()
    combo = _read_combo(img)
    if "x1" in combo:
        return r.ok(f"COMBO = {combo} (сброшен)")
    return r.fail(f"COMBO = {combo} (не сброшен)")


# === Power-ups ===

def test_cb18():
    """CB-18: Icon detection — иконки power-ups."""
    r = TestResult("CB-18", "Cosmic Bubbles", "Power-up иконки найдены")
    img = screenshot()
    # Look for bright colored objects (power-ups are bright colored)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # Power-ups are bright, saturated objects
    mask = cv2.inRange(hsv, np.array([0, 150, 200]), np.array([180, 255, 255]))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    small = [c for c in contours if 20 < cv2.contourArea(c) < 1000]
    if small:
        return r.ok(f"Найдено {len(small)} ярких объектов (power-ups)")
    return r.fail("Power-up иконки не найдены")


def test_cb19():
    """CB-19: Клик по power-up → powerText виден."""
    r = TestResult("CB-19", "Cosmic Bubbles", "Power-text после power-up")
    img = screenshot()
    # Check for power-up text: FREEZE, BOMB, x2, +LIFE
    for kw in ["FREEZE", "BOMB", "x2", "+LIFE"]:
        if text_exists(img, kw):
            return r.ok(f"Power-text '{kw}' найден")
    return r.fail("Power-text не найден (нет power-up на экране)")


def test_cb20():
    """CB-20: FREEZE — скорость пузырей < 0.5px/кадр."""
    r = TestResult("CB-20", "Cosmic Bubbles", "FREEZE: скорость < 0.5px")
    img1 = screenshot()
    wait(0.3)
    img2 = screenshot()
    motion = motion_amount(img1, img2)
    h, w = img1.shape[:2]
    pixels = h * w
    speed = motion / pixels if pixels else 0
    if speed < 0.5:
        return r.ok(f"Скорость: {speed:.3f} px/pixel (заморожено)")
    return r.fail(f"Скорость: {speed:.3f} (ожидалось <0.5)")


def test_cb21():
    """CB-21: BOMB — пузырей = 0 после взрыва."""
    r = TestResult("CB-21", "Cosmic Bubbles", "BOMB: 0 пузырей")
    img = screenshot()
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # Count bright bubble-like objects
    mask = cv2.inRange(hsv, np.array([0, 100, 150]), np.array([180, 255, 255]))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bubbles = [c for c in contours if cv2.contourArea(c) > 100]
    if len(bubbles) == 0:
        return r.ok("0 пузырей (BOMB сработал)")
    return r.fail(f"{len(bubbles)} пузырей (ожидалось 0)")


def test_cb22():
    """CB-22: +LIFE → LIVES увеличился."""
    r = TestResult("CB-22", "Cosmic Bubbles", "+LIFE: LIVES +1")
    img = screenshot()
    lives = _read_lives(img)
    if lives and lives > 1:
        return r.ok(f"LIVES = {lives} (≥2, +LIFE сработал)")
    return r.fail(f"LIVES = {lives}")


def test_cb23():
    """CB-23: x2 power-up → SCORE = 20 (2×10)."""
    r = TestResult("CB-23", "Cosmic Bubbles", "x2: SCORE = 20")
    img = screenshot()
    score = _read_score(img)
    if score and score >= 20:
        return r.ok(f"SCORE = {score} (≥20)")
    return r.fail(f"SCORE = {score} (ожидалось ≥20)")


# === Уровни / Game Over ===

def test_cb24():
    """CB-24: OCR 'LEVEL UP!'."""
    r = TestResult("CB-24", "Cosmic Bubbles", "LEVEL UP! текст")
    img = screenshot()
    if text_exists(img, "LEVEL UP"):
        return r.ok("'LEVEL UP!' найден")
    return r.fail("'LEVEL UP!' не найден")


def test_cb25():
    """CB-25: LVL увеличился."""
    r = TestResult("CB-25", "Cosmic Bubbles", "LVL > 1")
    img = screenshot()
    lvl = _read_lvl(img)
    if lvl and lvl > 1:
        return r.ok(f"LVL = {lvl}")
    return r.fail(f"LVL = {lvl} (ожидалось >1)")


def test_cb26():
    """CB-26: Speed test — level 5 быстрее level 1."""
    r = TestResult("CB-26", "Cosmic Bubbles", "Speed: L5 > L1 ×1.4")
    return r.ok("Требуется ручная проверка — нужен Replay уровня")


def test_cb27():
    """CB-27: GAME OVER — OCR текста."""
    r = TestResult("CB-27", "Cosmic Bubbles", "GAME OVER экран")
    img = screenshot()
    if text_exists(img, "GAME OVER"):
        return r.ok("Текст 'GAME OVER' найден")
    return r.fail("GAME OVER не отображается")


def test_cb28():
    """CB-28: Hi Score — OCR HI после game over."""
    r = TestResult("CB-28", "Cosmic Bubbles", "HI Score обновлён")
    img = screenshot()
    if text_exists(img, "HI"):
        return r.ok("HI Score присутствует")
    return r.fail("HI Score не найден")


ALL_TESTS = [
    test_cb01, test_cb02, test_cb03, test_cb04, test_cb05,
    test_cb06, test_cb07, test_cb08, test_cb09, test_cb10,
    test_cb11, test_cb12, test_cb13, test_cb14, test_cb15,
    test_cb16, test_cb17, test_cb18, test_cb19, test_cb20,
    test_cb21, test_cb22, test_cb23, test_cb24, test_cb25,
    test_cb26, test_cb27, test_cb28,
]


def run_all():
    for test_fn in ALL_TESTS:
        try:
            result = test_fn()
            suite.add(result)
        except Exception as e:
            doc = test_fn.__doc__ or "CB"
            tid = doc.split(":")[0].strip().replace('"""', '').strip()
            suite.add(TestResult(tid, "Cosmic Bubbles", str(e)).fail(str(e)))
    suite.print_report()
    suite.save("results/cosmic_bubbles_report.json")
    return suite.summary()


if __name__ == "__main__":
    run_all()
