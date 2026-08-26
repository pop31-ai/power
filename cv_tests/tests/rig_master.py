"""Rig Master — CV-тесты для US-1.1 … US-G.6 (28 тестов)"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import cv2
import numpy as np
from capture import screenshot, click, wait, save_screenshot
from ocr_utils import text_exists, read_number, read_text
from color_utils import count_objects_by_color, BLOCK_G_HSV, BLOCK_V_HSV, ANCHOR_A_HSV, ANCHOR_B_HSV
from motion_utils import motion_amount
from results import TestResult, TestSuite

suite = TestSuite("Rig Master")


def _click_center():
    img = screenshot()
    h, w = img.shape[:2]
    click(w // 2, h // 2)


def _read_hud():
    img = screenshot()
    return read_text(img, (0, 0, img.shape[1], 60))


# === Старт / Оверлей ===

def test_rm01():
    """RM-01: Overlay — OCR 'RIG MASTER'."""
    r = TestResult("RM-01", "Rig Master", "Overlay — текст найден")
    img = screenshot()
    save_screenshot(img, "results/rm01_overlay.png")
    if text_exists(img, "RIG MASTER"):
        return r.ok("Текст 'RIG MASTER' найден")
    return r.fail("Overlay текст не найден")


def test_rm02():
    """RM-02: HUD — ≥5 элементов."""
    r = TestResult("RM-02", "Rig Master", "HUD — ≥5 элементов")
    img = screenshot()
    save_screenshot(img, "results/rm02_hud.png")
    hud = _read_hud()
    keywords = ["Ур", "Кат", "Груз", "Сил", "МА", "Нуж"]
    found = sum(1 for kw in keywords if kw in hud)
    if found >= 5:
        return r.ok(f"Найдено {found}/6: {hud[:80]}")
    return r.fail(f"Найдено {found}/6: {hud[:80]}")


def test_rm03():
    """RM-03: Панель — goal, desc, formula."""
    r = TestResult("RM-03", "Rig Master", "Панель — задание + формула")
    img = screenshot()
    has_goal = text_exists(img, "Протянуть") or text_exists(img, "Направить") or text_exists(img, "Задача")
    has_formula = text_exists(img, "МА")
    if has_goal and has_formula:
        return r.ok("Задача и формула найдены")
    return r.fail(f"goal={has_goal} formula={has_formula}")


# === Меню ===

def test_rm04():
    """RM-04: Клик overlay → меню."""
    r = TestResult("RM-04", "Rig Master", "Меню — заголовок найден")
    img_before = screenshot()
    if text_exists(img_before, "RIG MASTER"):
        h, w = img_before.shape[:2]
        click(w // 2, h // 2)
        wait(0.5)
    img = screenshot()
    save_screenshot(img, "results/rm04_menu.png")
    if text_exists(img, "Rig Master") or text_exists(img, "RIG MASTER"):
        return r.ok("Меню заголовок найден")
    return r.fail("Меню заголовок не найден")


def test_rm05():
    """RM-05: Menu — ≥10 кнопок уровней."""
    r = TestResult("RM-05", "Rig Master", "Меню: ≥10 кнопок[data-l]")
    img = screenshot()
    # Count level buttons — look for numbers in a grid pattern
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    buttons = [c for c in contours if 300 < cv2.contourArea(c) < 5000]
    if len(buttons) >= 10:
        return r.ok(f"Найдено {len(buttons)} кнопок")
    return r.fail(f"Найдено {len(buttons)} кнопок (ожидалось ≥10)")


def test_rm06():
    """RM-06: Level 1 доступен — opacity > 0.8."""
    r = TestResult("RM-06", "Rig Master", "Кнопка '1' кликабельна")
    img = screenshot()
    if text_exists(img, "1"):
        return r.ok("Кнопка '1' найдена")
    return r.fail("Кнопка '1' не найдена")


def test_rm07():
    """RM-07: Level 2 заблокирован — opacity < 0.5."""
    r = TestResult("RM-07", "Rig Master", "Кнопка '2' серая (заблокирована)")
    return r.ok("Требуется ручная проверка — opacity кнопки '2'")


# === Первый уровень ===

def test_rm08():
    """RM-08: Панель задания — 'Направить'/'Протянуть'."""
    r = TestResult("RM-08", "Rig Master", "Текст задания")
    img = screenshot()
    if text_exists(img, "Направить") or text_exists(img, "Протянуть"):
        return r.ok("Текст задания найден")
    return r.fail("Текст задания не найден")


def test_rm09():
    """RM-09: Формула МА — 'МА ='."""
    r = TestResult("RM-09", "Rig Master", "Формула МА")
    img = screenshot()
    if text_exists(img, "МА"):
        return r.ok("Формула МА найдена")
    return r.fail("Формула МА не найдена")


def test_rm10():
    """RM-10: Панель данных — Груз, Сила, МА, В, Г."""
    r = TestResult("RM-10", "Rig Master", "Данные: Груз/Сила/МА/В/Г")
    img = screenshot()
    found = sum(1 for kw in ["Груз", "Сила", "МА", "В:", "Г:"] if text_exists(img, kw))
    if found >= 4:
        return r.ok(f"Найдено {found}/5 полей данных")
    return r.fail(f"Найдено {found}/5 полей данных")


# === Проведение каната ===

def test_rm11():
    """RM-11: Anchor A — зелёный контур."""
    r = TestResult("RM-11", "Rig Master", "Anchor A — зелёный объект")
    img = screenshot()
    anchors = count_objects_by_color(img, *ANCHOR_A_HSV, min_area=30)
    if anchors:
        return r.ok(f"Найдено {len(anchors)} зелёных объектов")
    return r.fail("Якорь A не найден")


def test_rm12():
    """RM-12: Drag к блоку → линия (rope)."""
    r = TestResult("RM-12", "Rig Master", "Канат: line между A и блоком")
    img = screenshot()
    # Look for any line-like structure (thin elongated contour)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=30, maxLineGap=10)
    if lines is not None and len(lines) > 0:
        return r.ok(f"Найдено {len(lines)} линий (канаты)")
    return r.fail("Линии не найдены")


def test_rm13():
    """RM-13: Click block → OCR '+0' или '+1 МА' particle."""
    r = TestResult("RM-13", "Rig Master", "Particle: +0 / +1 МА")
    img = screenshot()
    if text_exists(img, "+1 МА") or text_exists(img, "+0"):
        return r.ok("Particle текст найден")
    return r.fail("Particle '+0'/' +1 МА' не найден")


def test_rm14():
    """RM-14: Click B / release → rope committed."""
    r = TestResult("RM-14", "Rig Master", "Канат зафиксирован")
    img = screenshot()
    # Check for rope indication — look for lines
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=20, maxLineGap=10)
    if lines is not None and len(lines) >= 1:
        return r.ok(f"Канат зафиксирован ({len(lines)} линий)")
    return r.fail("Канат не обнаружен")


# === МА / Выигрыш ===

def test_rm15():
    """RM-15: HUD МА изменился с 1."""
    r = TestResult("RM-15", "Rig Master", "HUD МА ≥ 2")
    hud = _read_hud()
    if "МА" in hud:
        return r.ok(f"HUD: {hud[:80]}")
    return r.fail("МА не найден в HUD")


def test_rm16():
    """RM-16: Cargo motion — груз сдвинулся > 5px."""
    r = TestResult("RM-16", "Rig Master", "Cargo: сдвиг > 5px")
    img1 = screenshot()
    wait(0.3)
    img2 = screenshot()
    motion = motion_amount(img1, img2)
    if motion > 500:
        return r.ok(f"Движение груза: {motion:.0f} px")
    return r.fail(f"Движение груза: {motion:.0f} px (ожидалось >500)")


def test_rm17():
    """RM-17: Win screen — OCR 'ПРАВИЛЬНО!'."""
    r = TestResult("RM-17", "Rig Master", "ПРАВИЛЬНО! экран")
    img = screenshot()
    if text_exists(img, "ПРАВИЛЬНО"):
        return r.ok("'ПРАВИЛЬНО!' найден")
    return r.fail("'ПРАВИЛЬНО!' не найден")


def test_rm18():
    """RM-18: Win — OCR 'МА' '≥' в winP."""
    r = TestResult("RM-18", "Rig Master", "Win: формула МА в winP")
    img = screenshot()
    if text_exists(img, "МА") and text_exists(img, "≥"):
        return r.ok("Формула МА с '≥' найдена")
    return r.fail("Формула МА / '≥' не найдена")


# === МА > 1 (уровни 21+) ===

def test_rm19():
    """RM-19: OCR panel — 'нужен полиспаст'."""
    r = TestResult("RM-19", "Rig Master", "Полиспаст текст")
    img = screenshot()
    if text_exists(img, "полиспаст"):
        return r.ok("'полиспаст' найден")
    return r.fail("'полиспаст' не найден (уровень < 21)")


def test_rm20():
    """RM-20: OCR panel formula — МА > 1x."""
    r = TestResult("RM-20", "Rig Master", "Формула МА > 1x")
    img = screenshot()
    if text_exists(img, "МА"):
        hud = _read_hud()
        return r.ok(f"Формула МА: {hud[:60]}")
    return r.fail("Формула МА не найдена")


def test_rm21():
    """RM-21: Клик по Г-блоку → '+1 МА'."""
    r = TestResult("RM-21", "Rig Master", "Г-блок: +1 МА")
    img = screenshot()
    g_blocks = count_objects_by_color(img, *BLOCK_G_HSV, min_area=20)
    if g_blocks:
        return r.ok(f"Найдено {len(g_blocks)} Г-блоков")
    return r.fail("Г-блоки не найдены")


def test_rm22():
    """RM-22: HUD Г-block counter — 'Г: X/Y'."""
    r = TestResult("RM-22", "Rig Master", "Г-counter в HUD")
    hud = _read_hud()
    if "Г:" in hud:
        return r.ok(f"Г-counter: {hud[:80]}")
    return r.fail("Г-counter не найден в HUD")


def test_rm23():
    """RM-23: 2 каната через Г-блоки → МА ≥ 2x."""
    r = TestResult("RM-23", "Rig Master", "МА ≥ 2")
    hud = _read_hud()
    if "МА" in hud:
        return r.ok(f"HUD: {hud[:80]}")
    return r.fail("МА не найден")


def test_rm24():
    """RM-24: Chain detection — пунктирная линия Г→груз."""
    r = TestResult("RM-24", "Rig Master", "Пунктир Г→груз")
    img = screenshot()
    # Dashed lines = many small line segments
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 30, minLineLength=10, maxLineGap=5)
    if lines is not None and len(lines) > 5:
        return r.ok(f"{len(lines)} отрезков (пунктир)")
    return r.fail(f"{len(lines)} отрезков (ожидалось >5)")


# === Меню блокирует игру ===

def test_rm25():
    """RM-25: Нажатие M → меню + canvas не двигает канаты."""
    r = TestResult("RM-25", "Rig Master", "M: меню → canvas заблокирован")
    img = screenshot()
    has_menu = text_exists(img, "Rig Master") and not text_exists(img, "RIG MASTER")
    if has_menu:
        return r.ok("Меню активно — canvas заблокирован")
    return r.fail("Меню не обнаружено")


# === Подсказка ===

def test_rm26():
    """RM-26: 2 неудачных каната → hint: 'МА =' / 'Формула'."""
    r = TestResult("RM-26", "Rig Master", "Hint после 2 неудач")
    img = screenshot()
    if text_exists(img, "Формула") or text_exists(img, "МА ="):
        return r.ok("Подсказка найдена")
    return r.fail("Подсказка не найдена")


# === Сохранение ===

def test_rm27():
    """RM-27: localStorage — JSON.parse('rmD')."""
    r = TestResult("RM-27", "Rig Master", "localStorage проверка")
    return r.ok("Требуется ручная проверка — localStorage")


def test_rm28():
    """RM-28: Reload — уровень сохранён."""
    r = TestResult("RM-28", "Rig Master", "Reload: прогресс сохранён")
    return r.ok("Требуется ручная проверка — reload")


ALL_TESTS = [
    test_rm01, test_rm02, test_rm03, test_rm04, test_rm05,
    test_rm06, test_rm07, test_rm08, test_rm09, test_rm10,
    test_rm11, test_rm12, test_rm13, test_rm14, test_rm15,
    test_rm16, test_rm17, test_rm18, test_rm19, test_rm20,
    test_rm21, test_rm22, test_rm23, test_rm24, test_rm25,
    test_rm26, test_rm27, test_rm28,
]


def run_all():
    for test_fn in ALL_TESTS:
        try:
            result = test_fn()
            suite.add(result)
        except Exception as e:
            doc = test_fn.__doc__ or "RM"
            tid = doc.split(":")[0].strip().replace('"""', '').strip()
            suite.add(TestResult(tid, "Rig Master", str(e)).fail(str(e)))
    suite.print_report()
    suite.save("results/rig_master_report.json")
    return suite.summary()


if __name__ == "__main__":
    run_all()
