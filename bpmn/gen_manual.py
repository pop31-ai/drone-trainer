# -*- coding: utf-8 -*-
"""Генератор PDF-инструкций тренажёра дрона: для десктопа и для планшета.

Иллюстрации рисуются через matplotlib (клавиатура, планшет со стиками,
карта маршрутов) — без бинарных зависимостей. PDF собирается на reportlab
(шрифт DejaVu из данных matplotlib). В конце каждой инструкции — страницы
«Заметки и эскизы» с сеткой для записей и рисунков.

Выходные файлы кладутся в ./out вместе с брошюрой gen_brochure.py.

Запуск:  python gen_manual.py
"""
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
os.makedirs(OUT, exist_ok=True)

# ---- цвета (в тон тренажёру) -------------------------------------------------
C = dict(
    cyan='#4fc3f7', yellow='#ffd23e', green='#3ddc84', red='#ff5a5f',
    purple='#9c88ff', ink='#0d1420', dim='#78909c',
)

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def canvas(w=10.5, h=8.0):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    return fig, ax


def rbox(ax, x, y, w, h, fc, ec, r=3, lw=1.4, z=3):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                 boxstyle='round,pad=0,rounding_size={}'.format(r),
                 fc=fc, ec=ec, lw=lw, zorder=z))


def txt(ax, x, y, s, fs=8.6, fc='#14202e', weight='normal', ha='center',
        va='center', z=6):
    ax.text(x, y, s, fontsize=fs, color=fc, fontweight=weight,
            ha=ha, va=va, zorder=z, linespacing=1.2)


def key(ax, x, y, w, h, label, sublabel='', fc='#eef4fb', ec='#2f6fb2'):
    rbox(ax, x, y, w, h, fc, ec, r=2.2)
    if sublabel:
        txt(ax, x, y + h * 0.18, label, fs=9.5, weight='bold')
        txt(ax, x, y - h * 0.22, sublabel, fs=6.4, fc='#546e7a')
    else:
        txt(ax, x, y, label, fs=9.5, weight='bold')


def save(fig, name):
    p = os.path.join(OUT, name)
    fig.savefig(p, dpi=200, facecolor='white')
    plt.close(fig)
    print('иллюстрация:', name)
    return p


# =============================================================================
#  1. КЛАВИАТУРА (десктоп)
# =============================================================================
def draw_kbd():
    fig, ax = canvas(12.2, 7.0)
    txt(ax, 50, 98, 'УПРАВЛЕНИЕ КЛАВИАТУРОЙ (раскладка тренажёра)', fs=16,
        weight='bold')
    txt(ax, 50, 93.5,
        'Горячие клавиши — цвет=функция: жёлтый «газ/высота», '
        'зелёный «движение», голубой «режимы/камера», красный «старт/рестарт»',
        fs=9, fc=C['dim'])

    rbox(ax, 50, 57, 96, 76, '#ffffff', '#c3cfdd', r=5, lw=1.6)

    fkeys = [
        ('B', 'моторы', C['yellow']), ('H', 'высота 4 м', C['yellow']),
        ('V', 'режим', C['cyan']), ('C', 'камера', C['cyan']),
        ('X', 'ветер', C['cyan']), ('P', 'пауза', C['purple']),
        ('N', 'наука', C['purple']), ('T', 'силы', C['purple']),
    ]
    fx = 11
    for label, sub, col in fkeys:
        fc = ('#fdf6e3' if col == C['yellow']
              else '#e8f4fd' if col == C['cyan']
              else '#f3efff')
        key(ax, fx, 84, 8.6, 11.5, label, sub, fc=fc)
        fx += 11.4

    key(ax, 20, 66, 7.4, 7.4, 'W', fc='#e8f8ee', ec='#2e7d32')
    key(ax, 12.6, 59, 7.4, 7.4, 'A', fc='#e8f8ee', ec='#2e7d32')
    key(ax, 20, 59, 7.4, 7.4, 'S', fc='#e8f8ee', ec='#2e7d32')
    key(ax, 27.4, 59, 7.4, 7.4, 'D', fc='#e8f8ee', ec='#2e7d32')
    txt(ax, 30, 50, 'тангаж вперёд/назад\nкрен влево/вправо', fs=7.6,
        fc='#2e7d32')

    key(ax, 56, 66, 7.4, 7.4, '▲', fc='#fdf6e3', ec='#b8860b')
    key(ax, 48.6, 59, 7.4, 7.4, '◄', fc='#fdf6e3', ec='#b8860b')
    key(ax, 56, 59, 7.4, 7.4, '▼', fc='#fdf6e3', ec='#b8860b')
    key(ax, 63.4, 59, 7.4, 7.4, '►', fc='#fdf6e3', ec='#b8860b')
    txt(ax, 64, 50, 'газ вверх/вниз ~50%\nрыск влево/вправо', fs=7.6,
        fc='#8a6d00')

    key(ax, 78, 59, 14, 9, 'Enter', 'старт / рестарт', fc='#fdeeee',
        ec='#c62828')
    key(ax, 78, 74, 14, 9, 'Space', 'выключить моторы', fc='#fdeeee',
        ec='#c62828')

    rbox(ax, 50, 18, 88, 24, '#f4f7fb', '#7e8e9d', r=4)
    txt(ax, 50, 27, 'Дополнительно: Bluetooth-геймпад', fs=9.5, weight='bold')
    txt(ax, 50, 21,
        'Левый стик: газ (верт.) и рыск (гор.).   Правый стик: тангаж (верт.) '
        'и крен (гор.).\nГаз — на ~50%: дрон зависает.  Всё остальное '
        'управляется с клавиатуры.',
        fs=8.2, fc='#455a64')
    return save(fig, 'ill_kbd.png')


# =============================================================================
#  2. ПЛАНШЕТ СО СТИКАМИ И КНОПКАМИ
# =============================================================================
def draw_tab():
    fig, ax = canvas(12.2, 7.0)
    txt(ax, 50, 98,
        'ЭКРАННОЕ УПРАВЛЕНИЕ НА ПЛАНШЕТЕ (гостевой режим, без входа)',
        fs=15, weight='bold')

    rbox(ax, 50, 50, 94, 88, '#0e1622', '#2a3547', r=7, lw=2, z=2)
    rbox(ax, 50, 50, 88, 82, '#131c2b', '#31405a', r=5, lw=1.2, z=3)

    def stick(cx, cy, lbl_v, lbl_h, col):
        ax.add_patch(Circle((cx, cy), 11.5, fc='#1b2536', ec='#4a5a76',
                            lw=1.6, zorder=4))
        ax.add_patch(Circle((cx, cy), 5.2, fc='#dfe9f7', ec='#8fa3bd',
                            lw=1.4, zorder=5))
        txt(ax, cx, cy + 1.2, '•', fs=11, fc='#3f4c63', weight='bold', z=6)
        txt(ax, cx, cy + 15, lbl_v, fs=8.4, fc='#c9d4e2', z=6)
        txt(ax, cx, cy - 15, lbl_h, fs=8.4, fc='#c9d4e2', z=6)
        ax.add_patch(FancyArrowPatch((cx - 12, cy + 12.5), (cx - 9.5, cy + 10),
                     arrowstyle='-|>', mutation_scale=9, color=col,
                     lw=1.6, zorder=4))
        ax.add_patch(FancyArrowPatch((cx + 9.5, cy - 10), (cx + 12, cy - 12.5),
                     arrowstyle='-|>', mutation_scale=9, color=col,
                     lw=1.6, zorder=4))

    stick(16, 20, 'ГАЗ ▲▼', 'РЫСК ◄►', C['yellow'])
    stick(84, 20, 'ТАНГАЖ ▲▼', 'КРЕН ◄►', C['green'])

    btns1 = [('B', 'моторы'), ('H', 'высота'), ('V', 'режим')]
    btns2 = [('C', 'камера'), ('X', 'ветер'), (' ⟳ ', 'старт')]
    for i, (lbl, sub) in enumerate(btns1):
        cx = 30 + i * 12.5
        ax.add_patch(Circle((cx, 68), 5.4, fc='#223250', ec='#7d93bd',
                            lw=1.6, zorder=5))
        txt(ax, cx, 69.4, lbl, fs=8.6, weight='bold', fc='#ffffff', z=6)
        txt(ax, cx, 61.5, sub, fs=7.2, fc='#9fb2c6', z=6)
    for i, (lbl, sub) in enumerate(btns2):
        cx = 30 + i * 12.5
        ax.add_patch(Circle((cx, 56), 5.4, fc='#223250', ec='#7d93bd',
                            lw=1.6, zorder=5))
        txt(ax, cx, 57.4, lbl, fs=8.6, weight='bold', fc='#ffffff', z=6)
        txt(ax, cx, 49.5, sub, fs=7.2, fc='#9fb2c6', z=6)

    txt(ax, 50, 79,
        'зелёная зона = правый стик (движение) · жёлтая = левый стик (газ/рыск)',
        fs=8.2, fc=C['dim'])
    txt(ax, 50, 8.5,
        'Стики появляются на тач-экране автоматически. Левый стик вверх = газ '
        '≈50% и взлёт.\nТочность посадки: уменьшайте газ плавно (жёлтый стик '
        'вниз на 1/4). Кнопки = клавиши клавиатуры.',
        fs=8.0, fc='#aebfcf')
    return save(fig, 'ill_tab.png')


# =============================================================================
#  3. КАРТА МАРШРУТОВ (вид сверху)
# =============================================================================
def draw_routes():
    fig, ax = canvas(11.5, 6.4)
    ax.set_xlim(-26, 58)
    ax.set_ylim(-24, 24)
    ax.set_aspect('equal')
    txt(ax, 16, 22.5, 'КАРТА МАРШРУТОВ (вид сверху, координаты X→Z м)',
        fs=15, weight='bold')

    ax.add_patch(Circle((0, 0), 2.4, fc='#fff3d6', ec='#b8860b', lw=1.6, zorder=3))
    ax.add_patch(Circle((0, 0), 0.9, fc='none', ec='#c62828', lw=2.2, zorder=4))
    txt(ax, 0, 0, '⊕', fs=8, fc='#8e0000', weight='bold')

    for x, z, l in [(16, 0, '1'), (32, 10, '2'), (50, -4, '3')]:
        ax.add_patch(Circle((x, z), 2.4, fc='none', ec='#2f6fb2', lw=2.0, zorder=4))
        txt(ax, x, z, l, fs=8, fc='#0d47a1', weight='bold')
    ax.plot([0, 16, 32, 50], [0, 0, 10, -4], color='#90a4ae', lw=1.2, ls=':')
    txt(ax, 16, -6, 'кольца: 1–2–3', fs=8, fc='#546e7a')

    m3 = {'A': (18, 0), 'B': (14, 18), 'C': (40, 18), 'D': (-6, 18)}
    for l, (x, z) in m3.items():
        ax.add_patch(Circle((x, z), 2.4, fc='none', ec='#c62828', lw=2.0, zorder=4))
        txt(ax, x, z, l, fs=8, fc='#8e0000', weight='bold')
    ax.plot([18, 14, 40, -6, 18], [0, 18, 18, 18, 0], color='#ef9a9a',
            lw=1.4, ls=':')
    for x, z, r in [(24, 6, 1.6), (30, -6, 1.8), (2, 16, 2.0)]:
        ax.add_patch(Circle((x, z), r, fc='#ffd6d6', ec='#c62828', lw=1.4,
                            ls='--', zorder=4))
        txt(ax, x, z, '!', fs=10, fc='#8e0000', weight='bold')
    txt(ax, 25, -11, 'слалом A→B→C→D (пунктир — препятствия)', fs=8,
        fc='#8e0000')

    progs = {
        'Круг': [(20, 0), (10, 14), (-10, 14), (-20, 0), (-10, -14),
                 (10, -14), 'square'],
        'Квадрат': [(18, 0), (18, 16), (-8, 16), (-8, 0), 'square'],
        'Спираль': [(20, 0), (8, 20), (-12, -6), (0, -20), (6, 4), 'circle'],
    }
    colmap = {'Круг': '#3ddc84', 'Квадрат': '#7e57c2', 'Спираль': '#ff9800'}
    yoff = -15
    for name, pts in progs.items():
        col = colmap[name]
        xy = pts[:-1]
        xs = [p[0] for p in xy]
        zs = [p[1] for p in xy]
        ax.plot(xs + [xs[0]], zs + [zs[0]], color=col, lw=1.4, alpha=.75,
                ls='-.' if name != 'Спираль' else '-')
        for i, (x, z) in enumerate(xy):
            ax.add_patch(Circle((x, z), 1.4, fc='#fff', ec=col, lw=1.6, zorder=5))
            txt(ax, x, z, str(i + 1), fs=6.6, fc='#37474f', weight='bold')
        txt(ax, -18, yoff + 4, 'программа {}'.format(name), fs=7.4, fc=col,
            weight='bold', ha='left')
        ax.plot([-18, -8], [yoff + 1.5, yoff + 1.5], color=col, lw=2)
        yoff += 5

    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    return save(fig, 'ill_map.png')


# =============================================================================
#  PDF-сборка
# =============================================================================
def build_pdf(path, title, subtitle, cover_lines, sections, note_prompts):
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (Paragraph, Spacer, Image, PageBreak,
                                    Table, TableStyle,
                                    BaseDocTemplate, PageTemplate, Frame,
                                    NextPageTemplate)

    MPL_TTF = os.path.join(matplotlib.get_data_path(), 'fonts', 'ttf')
    pdfmetrics.registerFont(TTFont('DJV', os.path.join(MPL_TTF,
                                                       'DejaVuSans.ttf')))
    pdfmetrics.registerFont(TTFont('DJV-B', os.path.join(MPL_TTF,
                                                         'DejaVuSans-Bold.ttf')))
    pdfmetrics.registerFont(TTFont('DJV-O', os.path.join(
        MPL_TTF, 'DejaVuSans-Oblique.ttf')))
    pdfmetrics.registerFont(TTFont('DJV-BO', os.path.join(
        MPL_TTF, 'DejaVuSans-BoldOblique.ttf')))
    pdfmetrics.registerFontFamily('DJV', normal='DJV', bold='DJV-B',
                                  italic='DJV-O', boldItalic='DJV-BO')

    st_h1 = ParagraphStyle('h1', fontName='DJV-B', fontSize=15, leading=19,
                           textColor=colors.HexColor('#0d47a1'), spaceBefore=2,
                           spaceAfter=6)
    st_h2 = ParagraphStyle('h2', fontName='DJV-B', fontSize=10.5, leading=14,
                           textColor=colors.HexColor('#5d4037'), spaceBefore=8,
                           spaceAfter=4)
    st_p = ParagraphStyle('p', fontName='DJV', fontSize=9.2, leading=13,
                          textColor=colors.HexColor('#1b2a3a'), spaceAfter=5)
    st_td = ParagraphStyle('td', fontName='DJV', fontSize=8.4, leading=10.8,
                           textColor=colors.HexColor('#1b2a3a'))
    st_th = ParagraphStyle('th', fontName='DJV-B', fontSize=8.4, leading=10.8,
                           textColor=colors.white)
    st_cov = ParagraphStyle('cov', fontName='DJV', fontSize=10.5, leading=15,
                            textColor=colors.HexColor('#33465c'),
                            spaceAfter=6, alignment=TA_CENTER)
    st_note = ParagraphStyle('note', fontName='DJV', fontSize=9, leading=13,
                             textColor=colors.HexColor('#455a64'),
                             spaceAfter=4)

    def tbl(rows, colWidths=None):
        data = []
        for r, row in enumerate(rows):
            data.append([Paragraph(c, st_th if r == 0 else st_td)
                         for c in row])
        t = Table(data, hAlign='CENTER', colWidths=colWidths)
        style = [
            ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#b0bec5')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 2.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2f6fb2')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [colors.white, colors.HexColor('#f2f6fb')]),
        ]
        t.setStyle(TableStyle(style))
        return t

    def img_flow(path, width_mm_, max_h_mm=210):
        p = os.path.join(OUT, path)
        if not os.path.exists(p):
            return Paragraph('<i>(нет файла: {})</i>'.format(path), st_note)
        im = Image(p)
        iw, ih = im.imageWidth, im.imageHeight
        w = width_mm_ * mm
        h = w * ih / iw
        if h > max_h_mm * mm:
            h = max_h_mm * mm
            w = h * iw / ih
        im.drawWidth, im.drawHeight = w, h
        return im

    story = []
    story.append(Spacer(1, 40 * mm))
    story.append(Paragraph(subtitle, ParagraphStyle(
        'sub', parent=st_cov, fontName='DJV-B', fontSize=16, leading=21,
        textColor=colors.HexColor('#0d47a1'))))
    story.append(Paragraph(title, st_cov))
    story.append(Spacer(1, 8 * mm))
    for ln in cover_lines:
        story.append(Paragraph(ln, st_cov))
    story.append(Spacer(1, 30 * mm))
    story.append(Paragraph('https://pop31-ai.github.io/drone-trainer/',
                           ParagraphStyle('url', parent=st_cov, fontName='DJV-B',
                                          fontSize=11.5,
                                          textColor=colors.HexColor('#1b5e20'))))
    story.append(NextPageTemplate('normal'))
    story.append(PageBreak())

    for sec in sections:
        kind = sec[0]
        if kind == 'h1':
            story.append(Paragraph(sec[1], st_h1))
        elif kind == 'h2':
            story.append(Paragraph(sec[1], st_h2))
        elif kind == 'p':
            story.append(Paragraph(sec[1], st_p))
        elif kind == 'tbl':
            colw = sec[2] if len(sec) > 2 else None
            story.append(tbl(sec[1], colWidths=colw))
            story.append(Spacer(1, 6))
        elif kind == 'img':
            story.append(img_flow(sec[1], sec[2]))
            story.append(Spacer(1, 6))
        elif kind == 'pb':
            story.append(PageBreak())
        elif kind == 'bullets':
            for b in sec[1]:
                story.append(Paragraph('•  ' + b, st_note))
            story.append(Spacer(1, 4))

    story.append(NextPageTemplate('notes'))
    story.append(PageBreak())
    for i, prompt in enumerate(note_prompts):
        if i > 0:
            story.append(NextPageTemplate('notes'))
            story.append(PageBreak())
        story.append(Paragraph('ЗАМЕТКИ И ЭСКИЗЫ · ' + prompt[0],
                               ParagraphStyle('nh', fontName='DJV-B',
                                              fontSize=13, leading=17,
                                              textColor=colors.HexColor(
                                                  '#4a148c'))))
        story.append(Paragraph(prompt[1], st_note))
        story.append(Spacer(1, 6))
        story.append(Table([['', '', '']], colWidths=[52 * mm, 52 * mm, 52 * mm],
                           rowHeights=[150 * mm],
                           style=TableStyle([
                               ('GRID', (0, 0), (-1, -1), 0.35,
                                colors.HexColor('#9e9e9e')),
                               ('BACKGROUND', (0, 0), (-1, -1),
                                colors.HexColor('#fffdf5')),
                           ])))
        story.append(Spacer(1, 8 * mm))
        story.append(Paragraph('Запись: …', st_note))

    def draw_grid(canv, doc):
        canv.saveState()
        canv.setLineWidth(0.25)
        canv.setStrokeColor(colors.HexColor('#c8bdc0'))
        canv.setDash(1, 3)
        x0, y0 = 14 * mm, 16 * mm
        w, h = A4[0] - 28 * mm, A4[1] - 30 * mm
        x = x0
        while x < x0 + w:
            canv.line(x, y0, x, y0 + h)
            x += 8 * mm
        y = y0
        while y < y0 + h:
            canv.line(x0, y, x0 + w, y)
            y += 8 * mm
        canv.setDash()
        canv.setStrokeColor(colors.HexColor('#90a4ae'))
        canv.setLineWidth(0.7)
        y = y0 + h - 12 * mm - 2 * mm
        canv.line(x0, y, x0 + w, y)
        canv.setLineWidth(0.25)
        for i in range(1, 6):
            canv.line(x0, y - i * 8 * mm, x0 + w, y - i * 8 * mm)
        canv.restoreState()

    def page_bg(canv, doc):
        if canv.getPageNumber() != 1:
            return
        canv.saveState()
        canv.setFillColor(colors.HexColor('#eef4fb'))
        canv.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
        canv.setStrokeColor(colors.HexColor('#2f6fb2'))
        canv.setLineWidth(1.6)
        canv.line(20, 42, A4[0] - 20, 42)
        canv.setFont('DJV-B', 8)
        canv.setFillColor(colors.HexColor('#546e7a'))
        canv.drawCentredString(A4[0] / 2, 18,
                               'drone-trainer · GitHub Pages · автономный '
                               'учебный тренажёр')
        canv.restoreState()

    pdf_path = os.path.join(OUT, path)
    frame = Frame(16 * mm, 16 * mm, A4[0] - 32 * mm, A4[1] - 34 * mm,
                  id='frame')
    doc = BaseDocTemplate(pdf_path, pagesize=A4, title=title,
                          author='drone-trainer')
    doc.addPageTemplates([
        PageTemplate(id='normal', frames=[frame], onPage=page_bg),
        PageTemplate(id='notes', frames=[Frame(16 * mm, 16 * mm,
                                               A4[0] - 32 * mm,
                                               A4[1] - 34 * mm, id='notes')],
                     onPage=draw_grid),
    ])
    doc.build(story)
    print('PDF:', pdf_path)
    return pdf_path


# =============================================================================
#  КОНТЕНТ
# =============================================================================
CONTROLS_DESKTOP = [
    ['Клавиши', 'Действие'],
    ['B', 'Вооружить моторы (взлёт требует газ ≥ небольшого)'],
    ['Space', 'Выключить моторы'],
    ['↑ / ↓', 'Газ: вверх — больше тяга, вниз — падение. ~50% = зависание'],
    ['W / S', 'Тангаж: вперёд / назад (наклон корпуса)'],
    ['A / D', 'Крен: влево / вправо'],
    ['← / →', 'Рыскание: поворот носом влево / вправо'],
    ['H', 'Автовысота 4 м (комфортный режим для новичков)'],
    ['V', 'Режим пилота: РУЧНОЙ → АВТО → CV-АВТО'],
    ['X', 'Ветер: спокойно / слабый / шторм'],
    ['C', 'Камера: следящая / орбита'],
    ['T', 'Векторы сил (физика)'],
    ['N', 'Научные факты (автолистание)'],
    ['P', 'Пауза'],
    ['Enter', 'Старт / перезапуск миссии'],
]

STICK_PILOT = [
    ['Действие', 'Как на планшете'],
    ['Взлёт', '«⚙ моторы», затем левый стик вверх ≈ 50%'],
    ['Вперёд / назад', 'Правый стик вверх / вниз (тангаж)'],
    ['Влево / вправо', 'Правый стик влево / вправо (крен)'],
    ['Поворот', 'Левый стик влево / вправо (рыск)'],
    ['Зависание', 'Газ ровно 50% или кнопка «H» (автовысота 4 м)'],
    ['Режим автопилота', 'Кнопка «V»: РУЧНОЙ → АВТО → CV-АВТО'],
    ['Камера', 'Кнопка «C»'],
    ['Перезапуск', 'Кнопка «⟳ старт»'],
]

MISSIONS_TAB = [
    ['Испытание', 'Суть', 'Победа'],
    ['1. Взлёт и зависание', 'взлететь, держать 4 м', 'мягкая посадка'],
    ['2. Кольца', 'пролететь 3 кольца по порядку', '3 кольца'],
    ['3. Мягкая посадка', 'сесть в красный круг на подиуме', '2 с в круге'],
    ['4. Слалом', 'A→B→C→D + не задеть шары', '4 кольца'],
]

MISSIONS_TAB_D = [
    ['Испытание', 'Суть', 'Победа'],
    ['1. Взлёт и зависание', 'взлететь, 4 с удержать 4 м, сесть',
     'мягкая посадка'],
    ['2. Кольца', 'пролететь 3 кольца по порядку', '3 кольца'],
    ['3. Мягкая посадка', 'сесть в красный круг на подиуме', '2 с в круге'],
    ['4. Слалом', 'A→B→C→D + обойти шары', '4 кольца'],
]

CRASH_TAB = [
    ['Что ломает полёт', 'Условие'],
    ['Жёсткий удар о землю', 'Vy < −1.6 м/с на касании (hardHit)'],
    ['Переворот при касании', 'наклон корпуса > 0.8 рад'],
    ['Вылет за зону', '|pos| > 95 м'],
    ['Столкновение с препятствием', 'центр дрона ближе радиуса шара'],
    ['Касание кольца', '0.85 < perp, 2 < rad < 2.5'],
    ['Разряд батареи', 'batt ≤ 0'],
    ['Таймаут', 'задание не пройдено за 420 с'],
]

TIMES_TAB = [
    ['Испытание', 'АВТО', 'CV-АВТО'],
    ['1. Взлёт и зависание', '16.4 с', '16.4 с'],
    ['2. Кольца', '51.6 с', '59.6 с'],
    ['3. Мягкая посадка', '18.9 с', '18.9 с'],
    ['4. Слалом', '74.7 с', '76.4 с'],
    ['Программа «Круг»', '90 с', '93 с'],
    ['Программа «Квадрат»', '63 с', '66 с'],
    ['Программа «Спираль»', '92 с', '99 с'],
]

DESKTOP_SECTIONS = [
    ('h1', 'БЫСТРЫЙ СТАРТ · ДЕСКТОП'),
    ('p', '1. Откройте https://pop31-ai.github.io/drone-trainer/  (или '
          'локально index.html). Интернет нужен только для загрузки Three.js '
          'с CDN.'),
    ('p', '2. При первом запуске всплывает МИНИ-ТУТОРИАЛ (4 шага) — '
          'пролистайте «Дальше →», в конце «Понятно ✓».'),
    ('p', '3. Выберите испытание (кнопки «1–4») и нажмите зелёную '
          '«ПОЕХАЛИ →». 4. В полёте нажмите B (вооружить моторы) и дайте газ '
          '↑ до ~50% — дрон зависнет.'),
    ('pb',),
    ('h1', 'УПРАВЛЕНИЕ КЛАВИАТУРОЙ'),
    ('img', 'ill_kbd.png', 150),
    ('tbl', CONTROLS_DESKTOP,
     [26 * mm, 164 * mm]),
    ('bullets', [
        'Газ — это «лифт», а не скорость: на 0 газ дрон падает камнем.',
        'Резкий газ из 0 «подкидывает» дрон — набирайте плавно.',
        'Поворот + движение: сначала рыск, потом W вперёд (наклон по ходу '
        'носа).',
        'H (автовысота 4 м) — идеальна для первых полётов.',
    ]),
    ('h2', 'Режимы пилота (клавиша V или кнопка «РУЧНОЙ» в шапке)'),
    ('bullets', [
        'РУЧНОЙ — стики полностью ваши.',
        'АВТО — автопилот следит за осью следующего кольца; высотой '
        'управляете вы.',
        'CV-АВТО — то же, но наведение «из кадра камеры» дрона (вид вперёд).',
    ]),
    ('pb',),
    ('h1', '4 ИСПЫТАНИЯ'),
    ('img', 'ill_map.png', 168),
    ('tbl', MISSIONS_TAB_D),
    ('p', '<b>Контрольные времена автопилота (АВТО / CV-АВТО):</b>'),
    ('tbl', TIMES_TAB),
    ('h2', 'Программы (конструктор заданий)'),
    ('p', 'На стартовом экране внизу — конструктор «ПОЛЁТНЫЕ ЗАДАНИЯ»: '
          'добавьте ворота (X, Z, высота, поворот, метка), сохраните и '
          'запустите «▶ ЗАПУСТИТЬ ЗАДАНИЕ». Пресеты: Круг, Квадрат, Спираль. '
          'Рекорды и история видны на стартовом экране, хранятся в браузере.'),
    ('pb',),
    ('h1', 'ЧТО ЛОМАЕТ ПОЛЁТ'),
    ('tbl', CRASH_TAB),
    ('p', 'Автопилот не «читерствует»: при штормовом ветре (X) запаса тяги '
          'может не хватить — об этом честно предупреждают «Рекомендации». '
          'На сильном ветре помогают автовысота H и CV-режим.'),
    ('bullets', [
        'Мягкая посадка: снижайте газ плавно, не «гасите» на высоте.',
        'Пролёт кольца: цельтесь в ось, а не в центр кольца.',
        'Слалом: закладывайте повороты заранее — дрон инерционен.',
    ]),
]

TABLET_SECTIONS = [
    ('h1', 'БЫСТРЫЙ СТАРТ · ПЛАНШЕТ (гостевой режим, без входа)'),
    ('p', '1. Откройте в браузере планшета '
          'https://pop31-ai.github.io/drone-trainer/ — вход в GitHub не нужен, '
          'это отдельный сайт (GitHub Pages).'),
    ('p', '2. Закройте МИНИ-ТУТОРИАЛ («Дальше →» … «Понятно ✓»), если он '
          'всплыл — иначе он перекрывает экран.'),
    ('p', '3. Коснитесь миссии («1. Взлёт и зависание» и т.д.), затем зелёной '
          '«ПОЕХАЛИ →». 4. В полёте коснитесь «⚙ моторы» и поднимите ЛЕВЫЙ '
          'стик вверх до ~50% — взлёт.'),
    ('pb',),
    ('h1', 'ЭКРАННОЕ УПРАВЛЕНИЕ (стики и кнопки)'),
    ('img', 'ill_tab.png', 158),
    ('tbl', STICK_PILOT, [62 * mm, 128 * mm]),
    ('bullets', [
        'Стики появляются только на сенсорном экране и только в полёте.',
        'Левый стик ВВЕРХ = газ (взлёт), ВНИЗ = снижение; ВЛЕВО/ВПРАВО = рыск.',
        'Правый стик = движение: вверх/вниз тангаж, влево/вправо крен.',
        'Точная посадка: левым стиком плавно убирайте газ до касания земли.',
        'Кнопки = клавиши: «H» — автовысота 4 м, «V» — режим автопилота, '
        '«⟳» — перезапуск.',
    ]),
    ('h2', 'Что видите на экране'),
    ('bullets', [
        'Сверху-слева: задачи миссии. Сверху-справа: телеметрия (высота, '
        'углы, скорость, статус, аккумулятор).',
        'Красный светящийся круг на жёлтом подиуме — точка мягкой посадки '
        '(цель испытания 3).',
        'Кольца — ворота; касание обода = крушение.',
    ]),
    ('pb',),
    ('h1', '4 ИСПЫТАНИЯ'),
    ('img', 'ill_map.png', 168),
    ('tbl', MISSIONS_TAB),
    ('h2', 'Режимы автопилота (кнопка «V»)'),
    ('p', 'РУЧНОЙ → АВТО (следит за осью кольца) → CV-АВТО (наведение «из '
          'кадра камеры»). Новичку проще АВТО: приподнимите газ — и автопилот '
          'сам ведёт от кольца к кольцу, вам остаётся следить за '
          'препятствиями и высотой.'),
    ('pb',),
    ('h1', 'ЧТО ЛОМАЕТ ПОЛЁТ'),
    ('tbl', CRASH_TAB),
    ('bullets', [
        'Ветер («X»): при шторме дрон может «падать» — включайте автовысоту '
        'H и увеличивайте газ.',
        'Касание кольца/шара или жёсткая посадка = перезапуск «⟳».',
        'Следите за «АККУМУЛЯТОР» в телеметрии.',
    ]),
]


def main():
    draw_kbd()
    draw_tab()
    draw_routes()

    note_prompts_desk = [
        ('СВОЙ ПЛАН ПРОХОЖДЕНИЯ',
         'Набросайте на карте траекторию захода на каждое кольцо и отметьте, '
         'где снижаете газ.'),
        ('ФОРМУЛЫ И ПАРАМЕТРЫ',
         'Запишите углы, высоты и пороги скоростей миссий или свои наблюдения '
         'по управлению.'),
    ]
    note_prompts_tab = [
        ('СХЕМА СВОЕЙ ПРОГРАММЫ',
         'Нарисуйте программу из конструктора заданий (ворота по карте: X, Z, '
         'высота).'),
        ('ЗАМЕТКИ',
         'Записывайте высоты посадки, поведение на ветре, что понравилось и '
         'что чинить.'),
    ]

    build_pdf(
        'Инструкция_десктоп_управление_дроном.pdf',
        '3D-ТРЕНАЖЁР ДРОНА',
        'ИНСТРУКЦИЯ · ДЕСКТОП',
        ['Управление клавиатурой, 4 испытания, автопилот АВТО / CV-АВТО.',
         'Физика: ПИД-регулятор, тяга винтов, инерция, сопротивление воздуха.',
         'В конце — страницы для заметок и эскизов.'],
        DESKTOP_SECTIONS,
        note_prompts_desk,
    )

    build_pdf(
        'Инструкция_планшет_управление_дроном.pdf',
        '3D-ТРЕНАЖЁР ДРОНА',
        'ИНСТРУКЦИЯ · ПЛАНШЕТ',
        ['Гостевой режим без входа на GitHub Pages.',
         'Экранные стики и кнопки вместо клавиатуры.',
         '4 испытания, автопилот АВТО / CV-АВТО.',
         'В конце — страницы для заметок и эскизов.'],
        TABLET_SECTIONS,
        note_prompts_tab,
    )
    print('ГОТОВО. Инструкции в папке:', OUT)


if __name__ == '__main__':
    main()