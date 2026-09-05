# -*- coding: utf-8 -*-
"""Генератор BPMN-схем и PDF-брошюры «4 ИСПЫТАНИЯ ДРОНА. Процессное управление (BPMN)».

Схемы рисуются средствами matplotlib (без бинарного Graphviz `dot`),
брошюра собирается на reportlab (шрифт DejaVu из данных matplotlib).
Выходные файлы кладутся в ./out.

Запуск:  python gen_brochure.py
"""
import os, base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Polygon, FancyArrowPatch
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
os.makedirs(OUT, exist_ok=True)

# ---- цвета (в тон тренажёру) -------------------------------------------------
C = dict(
    cyan='#4fc3f7', yellow='#ffd23e', green='#3ddc84', red='#ff5a5f',
    purple='#9c88ff', ink='#0d1420', dim='#78909c',
    task_fc='#eef4fb', task_ec='#2f6fb2',
    start_fc='#e8f5e9', start_ec='#2e7d32',
    end_fc='#ffebee', end_ec='#c62828',
    gw_fc='#fff8e1', gw_ec='#b8860b',
    err_fc='#fdf2f2', err_ec='#c62828',
    note_fc='#f4f8fd', note_ec='#90a4ae',
)

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def canvas(w=10.5, h=8.0):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis('off')
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    return fig, ax


def rbox(ax, x, y, w, h, fc, ec, r=3, lw=1.6, ls='-', z=3):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                 boxstyle=f"round,pad=0,rounding_size={r}",
                 fc=fc, ec=ec, lw=lw, linestyle=ls, zorder=z))


def txt(ax, x, y, s, fs=8.6, fc='#14202e', weight='normal', ha='center', va='center', z=6):
    ax.text(x, y, s, fontsize=fs, color=fc, fontweight=weight,
            ha=ha, va=va, zorder=z, linespacing=1.22)


def task(ax, x, y, w, h, label, sub=False, fc=C['task_fc'], ec=C['task_ec'], fs=8.4):
    rbox(ax, x, y, w, h, fc, ec, r=min(4, h * 0.16))
    txt(ax, x, y, label, fs=fs)
    if sub:
        bx, by, bh = x + w / 2 - 5.5, y - h / 2 + 4.5, 5.0
        rbox(ax, bx, by, bh, bh, '#ffffff', ec, r=1.8)
        txt(ax, bx, by, '+', fs=8, fc=ec, weight='bold')


def event(ax, x, y, rr, label=None, kind='start', fs=8):
    fc = C['start_fc'] if kind == 'start' else C['end_fc'] if kind == 'end' else '#ffffff'
    ec = C['start_ec'] if kind == 'start' else C['end_ec'] if kind == 'end' else C['task_ec']
    lw = 1.8 if kind != 'end' else 2.6
    ax.add_patch(Circle((x, y), rr, fc=fc, ec=ec, lw=lw, zorder=3))
    if kind == 'end':
        ax.add_patch(Circle((x, y), rr * 0.58, fc=fc, ec=ec, lw=lw, zorder=3))
    if label:
        txt(ax, x, y, label, fs=fs, fc='#10202e' if kind != 'end' else '#8e0000', weight='bold')


def gateway(ax, x, y, s, xmark=True, label=None, fs=8.4):
    ax.add_patch(Polygon([(x, y + s), (x + s, y), (x, y - s), (x - s, y)],
                         closed=True, fc=C['gw_fc'], ec=C['gw_ec'], lw=2.0, zorder=3))
    if xmark:
        ax.plot([x - s * 0.4, x + s * 0.4], [y, y], color=C['gw_ec'], lw=2.1, zorder=4)
        ax.plot([x, x], [y - s * 0.4, y + s * 0.4], color=C['gw_ec'], lw=2.1, zorder=4)
    else:
        ax.plot([x - s * 0.42, x + s * 0.42], [y, y], color=C['gw_ec'], lw=2.1, zorder=4)
        ax.plot([x, x], [y - s * 0.42, y + s * 0.42], color=C['gw_ec'], lw=2.1, zorder=4)
    if label:
        txt(ax, x, y + s + 3.4, label, fs=fs, fc='#5d4037', weight='bold')


def flow(ax, p1, p2, label=None, color='#37474f', lw=1.6, ls='-', rad=0.0, fs=7.6,
         lab_off=(0, 1.8)):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle='-|>', mutation_scale=13,
                 lw=lw, color=color, linestyle=ls,
                 connectionstyle=f'arc3,rad={rad}', zorder=2))
    if label:
        mx = (p1[0] + p2[0]) / 2 + lab_off[0]
        my = (p1[1] + p2[1]) / 2 + lab_off[1]
        txt(ax, mx, my, label, fs=fs, fc=color, weight='bold')


def note(ax, x, y, w, h, text, fs=7.6, fc=C['note_fc'], ec=C['note_ec']):
    rbox(ax, x, y, w, h, fc, ec, r=4)
    txt(ax, x, y, text, fs=fs, fc='#33465c')


def lane(ax, x0, y0, x1, y1, name, fc='#ffffff'):
    rbox(ax, (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, fc, C['note_ec'], r=0, lw=1.0, ls='--', z=1)
    rbox(ax, x0 + 4.5, (y0 + y1) / 2, 9, y1 - y0 - 0.6, '#eceff1', C['note_ec'], r=0, lw=1.0, z=2)
    txt(ax, x0 + 4.5, (y0 + y1) / 2, name, fs=7.4, fc='#455a64', weight='bold')


def save(fig, name):
    p = os.path.join(OUT, name)
    fig.savefig(p, dpi=190, facecolor='white')
    plt.close(fig)
    print('схема:', name)
    return p


# =============================================================================
#  ЛЕГЕНДА BPMN
# =============================================================================
def draw_legend():
    fig, ax = canvas(12, 4.6)
    ax.text(50, 97, 'НОТАЦИЯ BPMN: как читать схемы испытаний', ha='center',
            fontsize=14, fontweight='bold', color=C['ink'])
    cells = [
        ('Старт', 'event', -20), ('Задача', 'task', -20), ('Подпроцесс', 'task_sub', -20),
        ('Шлюз ИЛИ (X)', 'gw', -20), ('Событие ошибки', 'err', -20), ('Конец', 'end', 0),
    ]
    x0, ytop = 8, 68
    cw, ch = 15.5, 44
    for i, (name, kind, dy) in enumerate(cells):
        cx = x0 + i * (cw + 1.4)
        cy = ytop - ch / 2 - 4
        rbox(ax, cx, ytop, cw, ch, '#fbfdff', C['note_ec'], r=3)
        txt(ax, cx, ytop - 3.5, name, fs=8.4, fc='#0d1420', weight='bold')
        yy = cy + 8
        if kind == 'event':
            event(ax, cx, yy, 6.5, None, 'start')
        elif kind == 'end':
            event(ax, cx, yy, 6.5, None, 'end')
        elif kind == 'task':
            task(ax, cx, yy, 11, 8, 'Задача')
        elif kind == 'task_sub':
            task(ax, cx, yy, 11, 8, 'Задача', sub=True)
        elif kind == 'gw':
            gateway(ax, cx, yy, 7, xmark=True)
            txt(ax, cx, yy - 14, 'вопрос?', fs=7.2, fc='#5d4037')
        elif kind == 'err':
            event(ax, cx, yy, 6.5, '!', 'err', fs=7.5)
        txt(ax, cx, yy - 16.5, {'event': 'инициирует\nпроцесс', 'end': 'завершает\nпроцесс',
             'task': 'шаг без разбиения', 'task_sub': 'шаг со своим\nпроцессом',
             'gw': 'развилка\nмаршрута', 'err': 'аварийная\nситуация'}[kind],
            fs=6.8, fc='#546e7a')
    flow(ax, (6, 16), (12, 16), 'поток управления (стрелка «дальше»)', fs=7.4,
         lab_off=(0, -2.2))
    rbox(ax, 50, 8, 74, 9, C['note_fc'], C['note_ec'], r=4)
    txt(ax, 50, 8, 'Пунктирная рамка — пул/дорожка (исполнитель): ПИЛОТ · СИСТЕМА УПРАВЛЕНИЯ · ДРОН (ФИЗИКА). '
        'Подписи у стрелок — условия перехода (как в коде тренажёра).', fs=7.4, fc='#33465c')
    return save(fig, '0_legenda.png')


# =============================================================================
#  ИСПЫТАНИЕ 1 — ВЗЛЁТ И ЗАВИСАНИЕ
# =============================================================================
def draw_m0():
    fig, ax = canvas(11, 8.2)
    ax.text(50, 100.2, 'ИСПЫТАНИЕ 1 · ВЗЛЁТ И ЗАВИСАНИЕ', ha='center',
            fontsize=13.5, fontweight='bold', color=C['ink'])

    event(ax, 50, 91, 6.5)
    flow(ax, (50, 84), (50, 90.5))
    task(ax, 50, 80, 38, 9, 'Вооружить моторы\n[B]', fs=8.2)
    flow(ax, (50, 75.5), (50, 76.5))
    task(ax, 50, 71, 38, 9, 'Взлёт: газ → ~50%', fs=8.2)
    flow(ax, (50, 66.5), (50, 68.5))
    gateway(ax, 50, 62, 7.5, label='H ≥ 2 м ?')
    flow(ax, (50, 54.5), (50, 57), rad=0.0)
    task(ax, 50, 48, 46, 11, 'Удержание высоты 4 м\n(3.2 … 4.8 м), таймер 4 с', fs=8.2)
    flow(ax, (50, 42.5), (50, 44.5))
    gateway(ax, 50, 38, 7.5, label='4 с удержано ?')
    flow(ax, (50, 32.5), (50, 35))
    task(ax, 50, 26, 46, 11, 'Мягкая посадка\n(H < 0.2 м, |Vy| < 1.2), таймер 2 с', fs=8.2)
    flow(ax, (50, 18.5), (50, 20.5))
    gateway(ax, 50, 14, 7.5, label='Посадка успешна ?')
    flow(ax, (50, 6.5), (50, 9), ls='-', rad=0)
    event(ax, 50, 5, 5, None, 'end')
    txt(ax, 50, 1.6, 'МОЛОДЕЦ!', fs=8.6, fc='#8e0000', weight='bold')

    # ветка «нет»
    flow(ax, (44.5, 14), (20, 14), label='нет — снижай\nгаз плавнее', color='#c0392b',
         fs=7.4, rad=0, lab_off=(-13, 1.5))
    flow(ax, (20, 14), (20, 57), color='#c0392b', rad=0)
    flow(ax, (20, 57), (24, 62), color='#c0392b', rad=0.0)

    # две петли «нет» у шлюзов высоты
    flow(ax, (44.5, 38), (14, 38), label='нет', color='#c0392b', fs=7, rad=0)
    flow(ax, (14, 38), (14, 72), color='#c0392b', rad=0)
    flow(ax, (14, 72), (29, 71), color='#c0392b', rad=0)

    # ошибки слева-сверху
    event(ax, 12, 88, 6.0, '!', 'err', fs=7.5)
    txt(ax, 12, 81, 'КРУШЕНИЕ О ЗЕМЛЮ\n(hardHit, y≤0.05)', fs=7.0, fc='#8e0000', weight='bold')
    event(ax, 12, 75, 6.0, '!', 'err', fs=7.5)
    txt(ax, 12, 68, 'ПЕРЕВОРОТ\n(наклон > 0.8)', fs=7.0, fc='#8e0000', weight='bold')

    note(ax, 73, 85, 44, 13,
         'Автовысота (H):\nthr = 0.5 + 0.42·er − 0.3·vy\ner = H_жел − y (0.3 …)',
         fs=7.2)
    note(ax, 73, 68, 44, 14,
         'Для посадки газ ограничен:\n0.08 … 0.3 при y < 0.09 м\n«Мягко» = |Vy| < 1.2 м/с',
         fs=7.2)
    note(ax, 73, 50, 44, 12,
         'Таймаут миссии — 420 с\n(иначе «ТАЙМ-АУТ»)', fs=7.2)
    return save(fig, 'm0_vzlet_i_zavisanie.png')


# =============================================================================
#  ИСПЫТАНИЕ 2 — КОЛЬЦА
# =============================================================================
def draw_m1():
    fig, ax = canvas(11.5, 8.4)
    ax.text(50, 100.4, 'ИСПЫТАНИЕ 2 · ПРОЛЁТ ЧЕРЕЗ КОЛЬЦА (АВТО / CV-АВТО)', ha='center',
            fontsize=13.5, fontweight='bold', color=C['ink'])

    event(ax, 50, 90, 6.5)
    flow(ax, (50, 83.5), (50, 90))
    task(ax, 50, 78, 36, 9, 'Взлёт: H ≥ 2 м', fs=8.2)
    flow(ax, (50, 73.5), (50, 72.5))
    task(ax, 50, 66, 56, 12, 'Выбор активного кольца\n(1 → 2 → 3; маяк-конус над кольцом)', fs=8.0, sub=True)
    flow(ax, (50, 60), (50, 56.5))
    gateway(ax, 50, 52, 7.5, label='Кольцо есть ?')
    flow(ax, (50, 44.5), (50, 46.5))
    task(ax, 50, 37, 58, 14, 'Заход: слежение за осью кольца\n'
         'курс yE = atan2(nz,nx) + 0.55·e − ψ · yaw = 0.65·yE', fs=7.6, sub=True)
    flow(ax, (50, 30), (50, 30.5))
    gateway(ax, 50, 24, 8, label='Пролёт ворот ?')
    txt(ax, 33, 12.5, 'условие: perp<0.9 И rad<2.0', fs=7.1, fc='#33507c', weight='bold')
    flow(ax, (50, 16.2), (50, 9.5))
    event(ax, 50, 4.5, 5, None, 'end')
    txt(ax, 50, 1.2, 'МОЛОДЕЦ', fs=8.4, fc='#8e0000', weight='bold')

    # петли
    flow(ax, (43, 52), (5, 52), label='нет', color='#c0392b', fs=7.4, rad=0, lab_off=(0, 1.5))
    flow(ax, (5, 52), (5, 82), color='#c0392b', rad=0)
    flow(ax, (5, 82), (32, 78), color='#c0392b', rad=0)

    flow(ax, (43, 24), (79, 24), label='да (пролёт) → следующее', color='#2e7d32',
         fs=7.2, rad=0, lab_off=(0, -2.0))
    flow(ax, (79, 24), (79, 70), color='#2e7d32', rad=0.06)
    flow(ax, (79, 70), (74, 66), color='#2e7d32', rad=0)

    flow(ax, (57, 24), (79, 18), label='касание: perp<0.85, 2<rad<2.5',
         color='#c62828', fs=7.0, rad=0.15)
    event(ax, 86, 15, 6.5, '!', 'err', fs=7.5)
    txt(ax, 86, 8.5, 'КАСАНИЕ\nКОЛЬЦА', fs=7.4, fc='#8e0000', weight='bold')

    flow(ax, (55, 24), (70, 30), label='мимо → заново заход', color='#b8860b', fs=7.0, rad=0.2)

    note(ax, 12, 60, 34, 30,
         'Управление line-track (АВТО):\n'
         '• латеральная ошибка e = ex·az − ez·ax\n'
         '• crab: 0.55·e (−1…1)\n'
         '• near = 1 − |dA|/12;  base = 3.0 − 2.2·near\n'
         '• vfd = base·cos(yE)\n'
         '• pitch = 0.5·(vfd−vf),  roll = 0.8·(vld−vl)\n'
         '• высота: рамп ~1.1 м/с к H_жел',
         fs=7.0)
    note(ax, 12, 32, 34, 24,
         'CV-режим (камера «вперёд»):\n'
         '• ось кольца и центр — в теле дрона\n'
         '  через q_inv (X вперёд, Z вправо)\n'
         '• угол цели atan2(cv.z, cv.x)\n'
         '• ретикула-перекрестие в HUD\n'
         '(управление идентично line-track)',
         fs=7.0)
    note(ax, 12, 8, 34, 16,
         'Зона: |pos| > 95 м → «ПОКИДАЕТЕ ЗОНУ»\nТаймаут — 420 с',
         fs=7.0)
    return save(fig, 'm1_koltsa.png')


# =============================================================================
#  ИСПЫТАНИЕ 3 — ПОСАДКА
# =============================================================================
def draw_m2():
    fig, ax = canvas(11, 8.2)
    ax.text(50, 100.2, 'ИСПЫТАНИЕ 3 · МЯГКАЯ ПОСАДКА', ha='center',
            fontsize=13.5, fontweight='bold', color=C['ink'])

    event(ax, 50, 91, 6.5)
    flow(ax, (50, 84.5), (50, 91))
    task(ax, 50, 79, 38, 10, 'Взлёт на 5 м', fs=8.2)
    flow(ax, (50, 74), (50, 75.5))
    gateway(ax, 50, 68, 7.5, label='Над центром ?')
    txt(ax, 50, 77, 'высота 5 м', fs=7.2, fc='#33507c')
    flow(ax, (50, 60.5), (50, 62.5))
    task(ax, 50, 55, 42, 10, 'Завис: d < 2 м, таймер 3 с', fs=8.2)
    flow(ax, (50, 50), (50, 51))
    task(ax, 50, 44, 44, 11, 'Снижение над подиумом\n(плавный газ, контроль наклонов)', fs=8.0)
    flow(ax, (50, 38.5), (50, 39.5))
    gateway(ax, 50, 33, 7.5, label='Посадка успешна ?')
    txt(ax, 50, 42.5, 'H<0.22 · |Vy|<1.0 · d<2.2', fs=7.2, fc='#33507c')
    flow(ax, (50, 25.5), (50, 27.5))
    event(ax, 50, 21, 5.5, None, 'end')
    txt(ax, 50, 17.5, 'МОЛОДЕЦ', fs=8.4, fc='#8e0000', weight='bold')

    # петли
    flow(ax, (43.5, 68), (20, 68), label='нет', color='#c0392b', fs=7.4, rad=0)
    flow(ax, (20, 68), (20, 82), color='#c0392b', rad=0)
    flow(ax, (20, 82), (31, 79), color='#c0392b', rad=0)

    flow(ax, (43.5, 33), (20, 33), label='ещё снижаемся', color='#c0392b', fs=7.2, rad=0)
    flow(ax, (20, 33), (20, 49.5), color='#c0392b', rad=0)
    flow(ax, (20, 49.5), (28, 44), color='#c0392b', rad=0)

    # зоны ошибок справа
    event(ax, 84, 50, 6.2, '!', 'err', fs=7.5)
    txt(ax, 84, 43, 'ЖЁСТКИЙ УДАР\nVy ≤ −1.0 при приземлении', fs=7.2, fc='#8e0000', weight='bold')
    event(ax, 84, 34, 6.2, '!', 'err', fs=7.5)
    txt(ax, 84, 27, 'СЪЕЗД С ПОДИУМА\n(посадка вне круга d<2.2)', fs=7.2, fc='#8e0000', weight='bold')

    note(ax, 73, 72, 42, 22,
         'Зона подиума: radius 2.2 м\nЗона посадки = круг (zonePad)\n'
         'Малейший наклон → касание\nкорпусом (наклон > 0.8) = «ПЕРЕВОРОТ»',
         fs=7.2)
    note(ax, 12, 8, 34, 18,
         'Совет:\nснижайте газ плавно, дайте\nдрону «просесть» — не гасите\nрезко на высоте',
         fs=7.2)
    return save(fig, 'm2_pochadka.png')


# =============================================================================
#  ИСПЫТАНИЕ 4 — СЛАЛОМ
# =============================================================================
def draw_m3():
    fig, ax = canvas(11.5, 8.4)
    ax.text(50, 100.4, 'ИСПЫТАНИЕ 4 · СЛАЛОМ (шахматный маршрут)', ha='center',
            fontsize=13.5, fontweight='bold', color=C['ink'])

    event(ax, 50, 90, 6.5)
    flow(ax, (50, 83.5), (50, 90))
    task(ax, 50, 78, 36, 9, 'Взлёт: H ≥ 2 м', fs=8.2)
    flow(ax, (50, 73.5), (50, 72.5))
    task(ax, 50, 66, 52, 12, 'Выбор кольца\nA → B → C → D (индексация по заданию)', fs=8.0, sub=True)
    flow(ax, (50, 60), (50, 56.5))
    gateway(ax, 50, 52, 7.5, label='Кольцо есть ?')
    flow(ax, (50, 44.5), (50, 46.5))
    task(ax, 50, 37, 58, 14, 'Заход: слежение + обход препятствий\n'
         '(курс на ось, боковое vld·0.9, crab 0.55·e)', fs=7.6, sub=True)
    flow(ax, (50, 30), (50, 30.5))
    gateway(ax, 50, 24, 8, label='Пролёт ворот ?')
    txt(ax, 33, 12.5, 'условие: perp<0.9 И rad<2.0', fs=7.1, fc='#33507c', weight='bold')
    flow(ax, (50, 16.2), (50, 9.5))
    event(ax, 50, 4.5, 5, None, 'end')
    txt(ax, 50, 1.2, 'МОЛОДЕЦ', fs=8.4, fc='#8e0000', weight='bold')

    # петли
    flow(ax, (43, 52), (5, 52), label='нет', color='#c0392b', fs=7.4, rad=0, lab_off=(0, 1.5))
    flow(ax, (5, 52), (5, 82), color='#c0392b', rad=0)
    flow(ax, (5, 82), (32, 78), color='#c0392b', rad=0)

    flow(ax, (43, 24), (79, 24), label='да → следующее кольцо', color='#2e7d32',
         fs=7.2, rad=0, lab_off=(0, -2.0))
    flow(ax, (79, 24), (79, 70), color='#2e7d32', rad=0.06)
    flow(ax, (79, 70), (74, 66), color='#2e7d32', rad=0)

    flow(ax, (57, 24), (79, 17), label='касание кольца', color='#c62828', fs=7.0, rad=0.15)
    event(ax, 86, 14, 6.5, '!', 'err', fs=7.5)
    txt(ax, 86, 7.5, 'КАСАНИЕ\nКОЛЬЦА', fs=7.4, fc='#8e0000', weight='bold')

    flow(ax, (55, 24), (70, 31), label='мимо → заново', color='#b8860b', fs=7.0, rad=0.2)

    note(ax, 12, 58, 34, 34,
         'Препятствия (сферы):\n'
         '• (24, 1.6, 6)   r = 1.6\n'
         '• (30, 1.2, −6)  r = 1.8\n'
         '• (2,  1.5, 16)  r = 2.0\n'
         'Коллизии проверяются каждый кадр\n'
         '→ «СТОЛКНОВЕНИЕ С ПРЕПЯТСТВИЕМ»',
         fs=7.0)
    note(ax, 12, 26, 34, 24,
         'Шахматный маршрут: влево-вправо-вверх\n'
         'комбинирует тангаж, крен, газ и рыск.\n'
         'Кольца: A(18,3,0) B(14,4,18)\n'
         'C(40,6,18) D(−6,2,18)',
         fs=7.0)
    note(ax, 12, 6, 34, 14,
         'В CV-режиме цель — ось кольца «из кадра»,\n'
         'управление идентично АВТО (line-track).',
         fs=7.0)
    return save(fig, 'm3_slalom.png')


# =============================================================================
#  СИСТЕМНАЯ СХЕМА (режимы и контуры) — пул с дорожками
# =============================================================================
def draw_system():
    fig, ax = canvas(12.5, 9.2)
    ax.text(50, 101.6, 'СИСТЕМНАЯ СХЕМА · УПРАВЛЕНИЕ ДРОНОМ (пул с дорожками)', ha='center',
            fontsize=13.5, fontweight='bold', color=C['ink'])

    # ПУЛ + дорожки
    rbox(ax, 50, 54, 96, 97, '#f4f7fb', '#7e8e9d', r=0, lw=1.6, z=1)
    ax.text(2.2, 54, 'ПРОЦЕСС «ПОЛЁТ ПО ИСПЫТАНИЮ»', rotation=90,
            fontsize=7.4, color='#0d47a1', fontweight='bold', ha='center', va='center', zorder=6)
    lane(ax, 0, 74, 100, 97, 'ПИЛОТ')
    lane(ax, 0, 40, 100, 74, 'СИСТЕМА УПРАВЛЕНИЯ')
    lane(ax, 0, 7, 100, 40, 'ДРОН (ФИЗИКА)')

    # дорожка ПИЛОТ
    event(ax, 7, 90, 5.5)
    task(ax, 20, 90, 24, 10, 'Выбор испытания\n(0–3 / программа)', fs=7.8)
    flow(ax, (29, 90), (34, 90))
    gateway(ax, 42, 90, 6.5, label='Миссия запущена ?')
    flow(ax, (35.5, 90), (36, 90), label='нет → назад', color='#c0392b', fs=7, rad=0.3, lab_off=(0, 2))
    flow(ax, (48, 90), (50, 90))
    task(ax, 58, 90, 20, 10, 'Задачи испытания\ncheckMission()', fs=7.8, sub=True)
    # победа
    flow(ax, (68, 85), (68, 83))
    event(ax, 68, 79, 5.5, None, 'end')
    txt(ax, 68, 73.5, 'МОЛОДЕЦ (win)', fs=7.4, fc='#8e0000', weight='bold')
    # авария
    flow(ax, (68, 85), (82, 85), rad=0)
    flow(ax, (82, 85), (82, 79), rad=0)
    event(ax, 86, 76, 6.5, '!', 'err', fs=7.5)
    txt(ax, 94, 79, 'АВАРИЯ (crash/lost)', fs=7.2, fc='#8e0000', weight='bold')

    # переход в систему управления
    flow(ax, (58, 84.5), (58, 74.2), rad=0)
    flow(ax, (58, 74.2), (50, 68), rad=0)

    gateway(ax, 50, 64, 6.5, label='Режим полёта ?')
    txt(ax, 50, 72.5, 'переключатель V / кнопка', fs=6.8, fc='#5d4037')

    flow(ax, (44.5, 64), (32, 56), label='РУЧНОЙ', color='#37474f', fs=7.2, rad=0)
    flow(ax, (50, 57.5), (50, 56), rad=0)
    flow(ax, (55.5, 64), (68, 56), label='АВТО (PILOT=1)', color='#37474f', fs=7.2, rad=0)

    task(ax, 32, 52, 20, 10, 'Стики пилота\npollSticks()', fs=7.8)
    task(ax, 50, 52, 20, 10, 'Line-track ИИ\naioPilotSticks()', fs=7.8, sub=True)
    task(ax, 68, 52, 20, 10, 'CV-камера\nкадр→ретикула', fs=7.8, sub=True)

    tx = [32, 50, 68]
    for i in range(3):
        flow(ax, (tx[i], 47), (tx[i], 48.5))

    task(ax, 50, 44, 34, 9.5, 'Миксер: throttle / yaw / pitch / roll', fs=8.0, sub=True)
    flow(ax, (50, 38.7), (50, 40.5))

    # дорожка ДРОН
    task(ax, 50, 33, 40, 12, 'physicsStep(): двухуровневый ПДД\n'
         'углы → ω → моменты → тяга винтов', fs=7.8, sub=True)
    flow(ax, (50, 27), (50, 27.5))
    gateway(ax, 50, 20, 6.5, label='Состояние в норме ?')
    txt(ax, 50, 27.8, 'проверки checkFalls() / checkGateNow()', fs=6.8, fc='#33507c')

    flow(ax, (45.5, 20), (20, 20), label='фейл', color='#c62828', fs=7.2, rad=0)
    flow(ax, (20, 20), (20, 16), color='#c62828', rad=0)
    flow(ax, (20, 16), (12, 16), color='#c62828', rad=0)
    event(ax, 12, 12, 6.0, '!', 'err', fs=7.5)
    txt(ax, 12, 5.2, 'crash / lost', fs=7.2, fc='#8e0000', weight='bold')

    flow(ax, (55.5, 20), (88, 20), label='ок, задача дальше', color='#2e7d32', fs=7.0, rad=0, lab_off=(0, -1.8))
    flow(ax, (88, 20), (88, 88), color='#2e7d32', rad=0.08)
    flow(ax, (88, 88), (76, 90.5), color='#2e7d32', rad=0)

    note(ax, 77, 52, 42, 26,
         'Автопилот (АВТО и CV) — тот же «line-track»:\n'
         '• курс yE = atan2(nz,nx) + 0.55·e − ψ\n'
         '• yaw = 0.65·yE;  pitch = 0.5·(vfd−vf)\n'
         '• roll = 0.8·(vld−vl);  vld = qG·0.9\n'
         '• рамп высоты ~1.1 м/с к H_жел',
         fs=7.0)
    note(ax, 77, 30, 42, 16,
         'Реакции на ветер: X → слабый / шторм\n'
         'форсаж наклона МАХTILT при шторме',
         fs=7.0)
    return save(fig, '5_system.png')


# =============================================================================
#  СВОДНАЯ СХЕМА 2x2 (Pillow)
# =============================================================================
def make_svod():
    titles = [
        ('m0_vzlet_i_zavisanie.png', '1 · ВЗЛЁТ И ЗАВИСАНИЕ'),
        ('m1_koltsa.png', '2 · ПРОЛЁТ ЧЕРЕЗ КОЛЬЦА'),
        ('m2_pochadka.png', '3 · МЯГКАЯ ПОСАДКА'),
        ('m3_slalom.png', '4 · СЛАЛОМ'),
    ]
    box_w, box_h, pad, head = 2000, 1180, 36, 92
    W = box_w * 2 + pad * 3
    H = box_h * 2 + head * 2 + pad * 3 + 90
    img = Image.new('RGB', (W, H), '#ffffff')
    d = ImageDraw.Draw(img)
    fpath = os.path.join(matplotlib.get_data_path(), 'fonts', 'ttf', 'DejaVuSans-Bold.ttf')
    fbig = ImageFont.truetype(fpath, 92)
    d.text((pad + 4, pad), '4 ИСПЫТАНИЯ ДРОНА · СВОДНАЯ СХЕМА ПРОХОЖДЕНИЯ', font=fbig,
           fill='#0d1420')
    for i, (name, t) in enumerate(titles):
        col, row = i % 2, i // 2
        x0 = pad + col * (box_w + pad)
        y0 = pad + 130 + row * (box_h + head + pad)
        d.rectangle([x0, y0, x0 + box_w, y0 + head - 20], fill='#eef4fb',
                    outline='#2f6fb2', width=4)
        d.text((x0 + 16, y0 + 12), t, font=fbig, fill='#0d47a1')
        src = Image.open(os.path.join(OUT, name))
        ratio = min((box_w - 20) / src.width, (box_h - 20) / src.height)
        nw, nh = int(src.width * ratio), int(src.height * ratio)
        src = src.resize((nw, nh), Image.LANCZOS)
        img.paste(src, (x0 + (box_w - nw) // 2, y0 + head + (box_h - nh) // 2))
    p = os.path.join(OUT, 'svod.png')
    img.save(p)
    print('схема: svod.png')
    return p


# =============================================================================
#  БРОШЮРА: PDF + HTML  (собираем из общего списка контента)
# =============================================================================
PDF_MAXW = 176  # мм

T1 = [
    ('h1', 'ИСПЫТАНИЕ 1 · ВЗЛЁТ И ЗАВИСАНИЕ'),
    ('p', 'Цель — научиться стартовать, стабилизировать высоту и мягко садиться. '
          'Задачи: вооружить моторы (B), поднять газ ≈50 %, удерживать 4 метра «в коридоре» 3.2–4.8 м '
          'не менее 4 секунд, затем снизиться с вертикальной скоростью |Vy|&lt;1.2 м/с.'),
    ('img', 'm0_vzlet_i_zavisanie.png'),
    ('tbl', {'h': ['Этап', 'Условие перехода', 'Режим'],
             'r': [
                 ['Вооружить моторы', 'S.armed (клавиша B)', 'любой'],
                 ['Взлёт', 'H ≥ 2 м', 'ручной / АВТО / CV'],
                 ['Удержание 4 м', '3.2…4.8 м, таймер 4 с', 'ручной / АВТО'],
                 ['Мягкая посадка', 'H<0.2 м и |Vy|<1.2, таймер 2 с', 'ручной / АВТО'],
             ]}),
    ('p', '<b>Контрольное время (АВТО и CV): ≈ 16 с.</b>  '
          'Частая ошибка — «уронить» газ до нуля: при 0 газ дрон падает камнем. '
          'Садитесь плавным убыванием газа, доводите до касания при |Vy|&lt;1.2 м/с.'),
]

T2 = [
    ('h1', 'ИСПЫТАНИЕ 2 · ПРОЛЁТ ЧЕРЕЗ КОЛЬЦА'),
    ('p', 'Маршрут — петля из трёх колец: синее (16,6,0), зелёное (32,6,10), красное (50,8,−4), '
          'с поворотами плоскости. Пролёт засчитывается, когда центр дрона оказался в «толуще» кольца: '
          'расстояние вдоль нормали perp &lt; 0.9 м и радиус от центра в плоскости кольца rad &lt; 2.0 м. '
          'Касание (perp&lt;0.85, 2&lt;rad&lt;2.5) — крушение.'),
    ('img', 'm1_koltsa.png'),
    ('tbl', {'h': ['Задача', 'Условие', 'Кто исполняет'],
             'r': [
                 ['Взлёт', 'H ≥ 2 м', 'пилот / АВТО'],
                 ['Кольцо #1 синее', 'gates[0].passed', 'полёт'],
                 ['Кольцо #2 зелёное', 'gates[1].passed', 'полёт'],
                 ['Кольцо #3 красное', 'gates[2].passed', 'полёт'],
             ]}),
    ('p', '<b>Контрольное время:</b> АВТО ≈ 51.6 с, CV-АВТО ≈ 59.6 с.  '
          'Автопилот следит за <u>линией оси</u> кольца (не просто летит на центр): '
          'курс yE = atan2(nz,nx) + 0.55·e − ψ, где e — поперечная ошибка, ψ — рыскание. '
          'В CV-режиме ось и центр берутся «из кадра камеры» через обратный кватернион.'),
]

T3 = [
    ('h1', 'ИСПЫТАНИЕ 3 · МЯГКАЯ ПОСАДКА'),
    ('p', 'Проверка точного позиционирования. Взлёт на 5 м, зависание над центром подиума '
          '(d &lt; 2 м, таймер 3 с) и посадка строго в круг: H &lt; 0.22 м, |Vy| &lt; 1.0 м/с, '
          'смещение от центра &lt; 2.2 м (зона подиума).'),
    ('img', 'm2_pochadka.png'),
    ('tbl', {'h': ['Этап', 'Условие', 'Режим'],
             'r': [
                 ['Взлёт на 5 м', 'H ≥ 5 м', 'ручной / АВТО'],
                 ['Над центром', 'd &lt; 2 м, таймер 3 с', 'ручной / АВТО'],
                 ['Посадка на подиум', 'H&lt;0.22, |Vy|&lt;1.0, d&lt;2.2, 2 с', 'ручной / АВТО'],
             ]}),
    ('p', '<b>Контрольное время: ≈ 18.9 с.</b>  Хитрость — наклон корпуса при движении даёт '
          'горизонтальный снос: над центром «гасите» крен и тангаж (наклоны &lt; 25°), '
          'иначе приземление смещается.'),
]

T4 = [
    ('h1', 'ИСПЫТАНИЕ 4 · СЛАЛОМ'),
    ('p', 'Шахматный маршрут влево-вправо-вверх: A(18,3,0) → B(14,4,18) → C(40,6,18) → D(−6,2,18). '
          'Дополнительно на трассе три шара-препятствия (r 1.6 / 1.8 / 2.0 м), столкновение с ними — crash.'),
    ('img', 'm3_slalom.png'),
    ('tbl', {'h': ['Задача', 'Условие', 'Примечание'],
             'r': [
                 ['Взлёт', 'H ≥ 2 м', ''],
                 ['Кольцо A', 'gates[0].passed', 'Выс. 3 м, на запад'],
                 ['Кольцо B', 'gates[1].passed', 'Выс. 4 м, на восток + север'],
                 ['Кольцо C', 'gates[2].passed', 'Выс. 6 м, центр'],
                 ['Кольцо D', 'gates[3].passed', 'Выс. 2 м, на запад'],
             ]}),
    ('p', '<b>Контрольное время:</b> АВТО ≈ 74.7 с, CV-АВТО ≈ 76.4 с.  '
          'Препятствия проверяются каждый кадр: |d|&lt;r → «СТОЛКНОВЕНИЕ». '
          'Перед крутым виражом закладывайте поворот заранее — дрон имеет инерцию.'),
]

P0 = [
    ('h1', '4 ИСПЫТАНИЯ ДРОНА'),
    ('h2', 'Процессное управление квадрокоптером · BPMN-схемы'),
    ('p', 'Это — брошюра по автономному (процессному) управлению дроном в симуляторе '
          '3D-ТРЕНАЖЁР ДРОНА. Одинаковая логика работает и в симуляторе, и закладывается '
          'в обвязку настоящего PX/ArduPilot-полётника: «задачи испытания» — это дискретный '
          'процесс (BPMN), «пилотирование» — непрерывные контуры управления.'),
    ('p', 'Три способа пройти любое испытание: <b>РУЧНОЙ</b> (стики), <b>АВТО</b> (PILOT=1, '
          'линейное слежение за осью кольца) и <b>CV-АВТО</b> (PILOT=2, те же формулы, но угол '
          'цели берётся из «кадра камеры»). Переключение — клавиша V или кнопка в шапке симулятора.'),
    ('img', 'svod.png'),
]

P1 = [
    ('h1', 'КАК ЧИТАТЬ СХЕМЫ (нотация BPMN)'),
    ('p', 'Схемы ниже — это BPMN-процессы: события (старт/конец/ошибка) — круги, задачи — '
          'прямоугольники со скруглением, шлюзы-развилки — ромбы, потоки — стрелки. '
          'Подписи у стрелок — точные условия перехода из кода симулятора.'),
    ('img', '0_legenda.png'),
    ('tbl', {'h': ['Элемент процесса', 'Реализация в коде (index.html)'],
             'r': [
                 ['Старт / вооружение', 'S.armed, клавиша B'],
                 ['Задачи испытания', 'MISSIONS[i].tasks → checkMission()'],
                 ['Пролёт ворот', 'checkGates(): perp&lt;0.9 &amp;&amp; rad&lt;2.0'],
                 ['Контроль падения', 'checkFalls(): жёсткий удар, переворот, зона, батарея'],
                 ['Выбор режима', 'PILOT: 0 ручной / 1 АВТО / 2 CV; V'],
                 ['Автопилот', 'aiPilotSticks(): line-track (АВТО и CV)'],
                 ['Программы', 'runProgram(), progTasks(), mActive=4'],
                 ['Рекомендации', 'renderRecs()'],
                 ['Рекорды/история', 'recordRun() / logResult()'],
                 ['Победа', 'winGame() → МОЛОДЕЦ'],
                 ['Авария', 'crash / lost → логирование'],
             ]}),
]

P2 = [
    ('h1', 'СИСТЕМНАЯ СХЕМА · РЕЖИМЫ И КОНТУРЫ'),
    ('p', 'Пул с тремя дорожками: ПИЛОТ → СИСТЕМА УПРАВЛЕНИЯ → ДРОН (ФИЗИКА). '
          'Непрерывный контур регулятора работает «внутри» задачи: физика шагает с частотой '
          '240 Гц, контроллер двухуровневый — внешний (крен/тангаж ПД) и внутренний (скорость '
          'вращения). Стики (или ИИ) задают целевые углы, физика гоняет их в моменты и тягу винтов.'),
    ('img', '5_system.png'),
    ('tbl', {'h': ['Аварийное условие', 'Код условия'],
             'r': [
                 ['Крушение о землю', 'hardHit &amp;&amp; y ≤ 0.05'],
                 ['Переворот при касании', 'y&lt;0.25 &amp;&amp; наклон &gt; 0.8'],
                 ['Вылет за зону', 'hypot(x,z) &gt; 95 м'],
                 ['Столкновение с препятствием', '|d| &lt; r сферы'],
                 ['Разряд батареи', 'batt ≤ 0'],
                 ['Потеря управления (крен)', '|φ| &gt; 1.35 рад (≈77°)'],
                 ['Касание кольца', 'perp&lt;0.85 &amp;&amp; 2&lt;rad&lt;2.5'],
                 ['Таймаут миссии', '&gt; 420 с'],
             ]}),
]

P3 = [
    ('h1', 'ПРИЛОЖЕНИЕ · ЧТО ТАМ В СИМУЛЯТОРЕ'),
    ('p', 'Версия брошюры соответствует коду index.html тренажёра. Контрольные времена сняты '
          'на автоматических прогонах (физика 240 Гц, 60 кадров/с).'),
    ('tbl', {'h': ['Раздел', 'Время при АВТО', 'Время при CV'],
             'r': [
                 ['1 · Взлёт и зависание', '16.4 с', '16.4 с'],
                 ['2 · Пролёт через кольца', '51.6 с', '59.6 с'],
                 ['3 · Мягкая посадка', '18.9 с', '18.9 с'],
                 ['4 · Слалом', '74.7 с', '76.4 с'],
             ]}),
    ('p', 'Программы (конструктор заданий) также проходимы АВТО: «Круг» ≈ 90 с, '
          '«Квадрат» ≈ 63 с, «Спираль» ≈ 92 с. При слабом ветре автопилот справляется, '
          'при штормовом — у аппарата не хватает запаса (об этом честно предупреждают '
          '«Рекомендации» в тренажёре).'),
]


def build_pdf():
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.lib.enums import TA_CENTER
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                    PageBreak, Table, TableStyle, KeepTogether)

    MPL_TTF = os.path.join(matplotlib.get_data_path(), 'fonts', 'ttf')
    pdfmetrics.registerFont(TTFont('DJV', os.path.join(MPL_TTF, 'DejaVuSans.ttf')))
    pdfmetrics.registerFont(TTFont('DJV-B', os.path.join(MPL_TTF, 'DejaVuSans-Bold.ttf')))
    pdfmetrics.registerFont(TTFont('DJV-O', os.path.join(MPL_TTF, 'DejaVuSans-Oblique.ttf')))
    pdfmetrics.registerFont(TTFont('DJV-BO', os.path.join(MPL_TTF, 'DejaVuSans-BoldOblique.ttf')))
    pdfmetrics.registerFontFamily('DJV', normal='DJV', bold='DJV-B',
                                  italic='DJV-O', boldItalic='DJV-BO')

    st_h1 = ParagraphStyle('h1', fontName='DJV-B', fontSize=16, leading=20,
                           textColor=colors.HexColor('#0d47a1'), spaceBefore=2, spaceAfter=8)
    st_h2 = ParagraphStyle('h2', fontName='DJV-B', fontSize=11.5, leading=15,
                           textColor=colors.HexColor('#455a64'), spaceBefore=0, spaceAfter=6)
    st_p = ParagraphStyle('p', fontName='DJV', fontSize=9.3, leading=13.4,
                          textColor=colors.HexColor('#1b2a3a'), spaceAfter=6)
    st_td = ParagraphStyle('td', fontName='DJV', fontSize=8.3, leading=10.6,
                           textColor=colors.HexColor('#1b2a3a'))
    st_th = ParagraphStyle('th', fontName='DJV-B', fontSize=8.3, leading=10.6,
                           textColor=colors.white)

    pdf_path = os.path.join(OUT, 'Брошюра_4_испытания_дрона_BPMN.pdf')
    doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                            leftMargin=17 * mm, rightMargin=17 * mm,
                            topMargin=15 * mm, bottomMargin=15 * mm,
                            title='4 испытания дрона · BPMN',
                            author='drone-trainer')

    story = []
    sections = [('ПРОЦЕССНОЕ УПРАВЛЕНИЕ · ОБЗОР', P0),
                ('БЫСТРЫЙ СТАРТ: НОТАЦИЯ И КОД', P1),
                ('ИСПЫТАНИЕ 1 — ВЗЛЁТ И ЗАВИСАНИЕ', T1),
                ('ИСПЫТАНИЕ 2 — ПРОЛЁТ ЧЕРЕЗ КОЛЬЦА', T2),
                ('ИСПЫТАНИЕ 3 — МЯГКАЯ ПОСАДКА', T3),
                ('ИСПЫТАНИЕ 4 — СЛАЛОМ', T4),
                ('СИСТЕМНАЯ СХЕМА · АВАРИЙНАЯ МАТРИЦА', P2),
                ('ПРИЛОЖЕНИЕ · КОНТРОЛЬНЫЕ ВРЕМЕНА', P3)]

    for title, items in sections:
        story.append(Paragraph('— ' + title, st_h2))
        story.append(Spacer(1, 4))
        for it in items:
            kind = it[0]
            if kind == 'h1':
                story.append(Paragraph(it[1], st_h1))
            elif kind == 'h2':
                story.append(Paragraph(it[1], st_h2))
            elif kind == 'p':
                story.append(Paragraph(it[1], st_p))
            elif kind == 'img':
                src = os.path.join(OUT, it[1])
                im = Image(src)
                iw, ih = im.imageWidth, im.imageHeight
                w = min(148 * mm, PDF_MAXW * mm)
                h = w * ih / iw
                im.drawWidth, im.drawHeight = w, min(h, 208 * mm)
                story.append(Spacer(1, 3))
                story.append(im)
                story.append(Spacer(1, 6))
            elif kind == 'tbl':
                data = it[1]
                rows = [[Paragraph(x, st_th) for x in data['h']]]
                for r_ in data['r']:
                    rows.append([Paragraph(c, st_td) for c in r_])
                t = Table(rows, hAlign='CENTER', colWidths=None)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2f6fb2')),
                    ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#b0bec5')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f2f6fb')]),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ]))
                story.append(Spacer(1, 2))
                story.append(t)
                story.append(Spacer(1, 8))
        story.append(PageBreak())

    doc.build(story)
    print('PDF:', pdf_path)
    return pdf_path


def build_html():
    """Лёгкая самодостаточная HTML-версия (картинки в base64)."""
    def b64(name):
        with open(os.path.join(OUT, name), 'rb') as f:
            return 'data:image/png;base64,' + base64.b64encode(f.read()).decode()

    css = """
    body{font-family:'Segoe UI',Arial,sans-serif;background:#eef2f7;color:#1b2a3a;margin:0;padding:24px;}
    .wrap{max-width:960px;margin:0 auto;background:#fff;border-radius:14px;box-shadow:0 10px 40px rgba(0,0,0,.12);padding:36px 44px;}
    h1{color:#0d47a1;font-size:26px;margin:26px 0 6px;}
    h2{color:#455a64;font-size:15px;margin:4px 0 10px;font-weight:700;}
    p{font-size:14px;line-height:1.55;color:#333;margin:10px 0;}
    img{max-width:100%;border:1px solid #dbe3ec;border-radius:8px;margin:10px 0;}
    table{border-collapse:collapse;width:100%;margin:12px 0;font-size:13px;}
    th{background:#2f6fb2;color:#fff;padding:7px;text-align:left;}
    td{border:1px solid #dbe3ec;padding:6px 8px;}
    tr:nth-child(even) td{background:#f4f8fd;}
    .sec{color:#78909c;font-size:13px;letter-spacing:1px;margin-top:34px;border-bottom:2px solid #2f6fb2;padding-bottom:4px;}
    """
    secs = [('ПРОЦЕССНОЕ УПРАВЛЕНИЕ · ОБЗОР', P0),
            ('БЫСТРЫЙ СТАРТ: НОТАЦИЯ И КОД', P1),
            ('ИСПЫТАНИЕ 1 — ВЗЛЁТ И ЗАВИСАНИЕ', T1),
            ('ИСПЫТАНИЕ 2 — ПРОЛЁТ ЧЕРЕЗ КОЛЬЦА', T2),
            ('ИСПЫТАНИЕ 3 — МЯГКАЯ ПОСАДКА', T3),
            ('ИСПЫТАНИЕ 4 — СЛАЛОМ', T4),
            ('СИСТЕМНАЯ СХЕМА · АВАРИЙНАЯ МАТРИЦА', P2),
            ('ПРИЛОЖЕНИЕ · КОНТРОЛЬНЫЕ ВРЕМЕНА', P3)]
    body = [f'<style>{css}</style><div class="wrap">']
    for title, items in secs:
        body.append(f'<div class="sec">{title}</div>')
        for it in items:
            kind = it[0]
            if kind == 'h1':
                body.append(f'<h1>{it[1]}</h1>')
            elif kind == 'h2':
                body.append(f'<h2>{it[1]}</h2>')
            elif kind == 'p':
                body.append(f'<p>{it[1]}</p>')
            elif kind == 'img':
                body.append(f'<img src="{b64(it[1])}" alt="{it[1]}">')
            elif kind == 'tbl':
                d = it[1]
                body.append('<table><tr>' + ''.join(f'<th>{h}</th>' for h in d['h']) + '</tr>')
                for r_ in d['r']:
                    body.append('<tr>' + ''.join(f'<td>{c}</td>' for c in r_) + '</tr>')
                body.append('</table>')
    body.append('</div>')
    p = os.path.join(OUT, 'broshura.html')
    with open(p, 'w', encoding='utf-8') as f:
        f.write('<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8">'
                '<title>4 испытания дрона · BPMN</title></head><body>' + ''.join(body) + '</body></html>')
    print('HTML:', p)
    return p


# =============================================================================
if __name__ == '__main__':
    draw_legend()
    draw_m0()
    draw_m1()
    draw_m2()
    draw_m3()
    draw_system()
    make_svod()
    build_pdf()
    build_html()
    print('ГОТОВО. Схемы и брошюра в папке:', OUT)