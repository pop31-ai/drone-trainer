# -*- coding: utf-8 -*-
"""Брошюра-скриншоты тренажёра дрона (PDF).

Скриншоты снимаются скриптом shots.py (headless Chromium + SwiftShader);
этот скрипт верстает их в PDF-брошюру: обложка + по странице на кадр
(описание сцены и подсказки) + страница со списком управления.

Запуск:  python gen_brochure_shots.py
"""
import os

import matplotlib

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')


def build():
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (Paragraph, Spacer, Image, Table,
                                    TableStyle, BaseDocTemplate, PageTemplate,
                                    Frame, PageBreak)

    MPL_TTF = os.path.join(matplotlib.get_data_path(), 'fonts', 'ttf')
    pdfmetrics.registerFont(TTFont('DJV', os.path.join(MPL_TTF,
                                                       'DejaVuSans.ttf')))
    pdfmetrics.registerFont(TTFont('DJV-B', os.path.join(MPL_TTF,
                                                         'DejaVuSans-Bold.ttf')))
    pdfmetrics.registerFont(TTFont('DJV-BO', os.path.join(
        MPL_TTF, 'DejaVuSans-BoldOblique.ttf')))
    pdfmetrics.registerFont(TTFont('DJV-O', os.path.join(
        MPL_TTF, 'DejaVuSans-Oblique.ttf')))
    pdfmetrics.registerFontFamily('DJV', normal='DJV', bold='DJV-B',
                                  italic='DJV-O', boldItalic='DJV-BO')

    st_h1 = ParagraphStyle('h1', fontName='DJV-B', fontSize=15, leading=19,
                           textColor=colors.HexColor('#0d47a1'), spaceBefore=2,
                           spaceAfter=4)
    st_p = ParagraphStyle('p', fontName='DJV', fontSize=9.4, leading=13.4,
                          textColor=colors.HexColor('#1b2a3a'), spaceAfter=6)
    st_note = ParagraphStyle('note', fontName='DJV-B', fontSize=8.6,
                             leading=12, textColor=colors.HexColor('#5d4037'),
                             spaceAfter=8)
    st_cov = ParagraphStyle('cov', fontName='DJV', fontSize=11, leading=15.5,
                            textColor=colors.HexColor('#33465c'),
                            spaceAfter=6, alignment=TA_CENTER)

    shots = [
        ('sc_start.png', 'СТАРТОВЫЙ ЭКРАН',
         'Меню миссий поверх 3D-сцены. Четыре испытания по возрастанию '
         'сложности, конструктор полётных заданий внизу и рекорды с историей '
         'тренировок (хранятся в браузере).',
         'Подсказка: сначала пролистайте мини-туториал «Дальше → … Понятно».'),
        ('sc_pad.png', 'СТАРТОВЫЙ ПОДИУМ',
         'Взлётная площадка: жёлтый подиум, а красное светящееся кольцо — '
         'целевая точка мягкой посадки испытания 3.',
         'Дрон стоит на подиуме (физика пола учитывает высоту площадки).'),
        ('sc_hover.png', 'ВЗЛЁТ И ЗАВИСАНИЕ',
         'Миссия 1. Вооружите моторы (B), левый стик вверх до ~50% — '
         'дрон висит на 4 м. Следящая камера держит его в кадре.',
         'Подсказка: газ на 50% = зависание; H включает автовысоту 4 м.'),
        ('sc_orbit.png', 'ОРБИТАЛЬНАЯ КАМЕРА',
         'Обзорная камера вокруг дрона: вращение мышью/пальцем, масштаб '
         'колесом. Удобно осматривать трассу и точки посадки.',
         'Клавиша C (или кнопка «C») переключает следящая ↔ орбита.'),
        ('sc_land.png', 'МЯГКАЯ ПОСАДКА В КРАСНОЕ КОЛЬЦО',
         'Миссия 3. Зависьте над центром подиума, плавно убирайте газ до '
         'касания: победа, если |Vy| < 1 м/с внутри круга.',
         'Подсказка: не «гасите» газ — снижение плавное, без провала.'),
        ('sc_ring.png', 'ПРОЛЁТ ЧЕРЕЗ КОЛЬЦА',
         'Миссия 2. Три кольца по порядку: синее → зелёное → красное. '
         'Летите на ось кольца, не задевая обод (касание = крушение).',
         'Перед кольцом — выровняйте высоту и нос жёлтыми стрелками.'),
        ('sc_slalom.png', 'СЛАЛОМ',
         'Миссия 4. Шахматный маршрут A→B→C→D с шарами-препятствиями '
         'между ними. Комбинирует газ, рыск, крен и тангаж.',
         'Подсказка: закладывайте повороты заранее — дрон инерционен.'),
    ]

    controls = [
        ['Функция', 'Клавиатура', 'Планшет'],
        ['Газ (взлёт)', '↑ / ↓', 'левый стик вверх/вниз'],
        ['Рыск (поворот)', '← / →', 'левый стик вбок'],
        ['Тангаж', 'W / S', 'правый стик вверх/вниз'],
        ['Крен', 'A / D', 'правый стик вбок'],
        ['Моторы', 'B / Space', 'кнопки «моторы»'],
        ['Автовысота 4 м', 'H', 'кнопка «H»'],
        ['Режим АВТО / CV', 'V', 'кнопка «V»'],
        ['Камера', 'C', 'кнопка «C»'],
        ['Ветер / пауза', 'X / P', 'кнопки «X» / нет'],
    ]

    story = []
    story.append(Spacer(1, 45 * mm))
    story.append(Paragraph('3D-ТРЕНАЖЁР ДРОНА',
                           ParagraphStyle('t', parent=st_cov, fontName='DJV-B',
                                          fontSize=20, leading=26,
                                          textColor=colors.HexColor('#0d47a1'))))
    story.append(Paragraph('БРОШЮРА · СКРИНШОТЫ',
                           ParagraphStyle('s', parent=st_cov, fontName='DJV-B',
                                          fontSize=13, leading=18,
                                          textColor=colors.HexColor('#5d4037'))))
    story.append(Spacer(1, 10 * mm))
    for ln in ['Физика: ПИД-регулятор, тяга винтов, инерция, сопротивление '
               'воздуха.',
               '4 испытания, автопилот АВТО / CV-АВТО, ветер и '
               'Bluetooth-геймпад.',
               'Скриншоты — реальные кадры игры (SwiftShader-рендер).']:
        story.append(Paragraph(ln, st_cov))
    story.append(Spacer(1, 26 * mm))
    story.append(Paragraph('https://pop31-ai.github.io/drone-trainer/',
                           ParagraphStyle('url', parent=st_cov, fontName='DJV-B',
                                          fontSize=12,
                                          textColor=colors.HexColor('#1b5e20'))))
    story.append(PageBreak())

    for png, title, text, tip in shots:
        story.append(Paragraph(title, st_h1))
        p = os.path.join(OUT, png)
        if os.path.exists(p):
            im = Image(p)
            iw, ih = im.imageWidth, im.imageHeight
            w = 172 * mm
            h = w * ih / iw
            im.drawWidth, im.drawHeight = w, h
            story.append(im)
        story.append(Spacer(1, 5 * mm))
        story.append(Paragraph(text, st_p))
        story.append(Paragraph('Совет: ' + tip, st_note))
        story.append(PageBreak())

    story.append(Paragraph('УПРАВЛЕНИЕ В ДВУХ СЛОВАХ', st_h1))
    st_th = ParagraphStyle('th', fontName='DJV-B', fontSize=8.6,
                           textColor=colors.white)
    st_td = ParagraphStyle('td', fontName='DJV', fontSize=8.6,
                           textColor=colors.HexColor('#1b2a3a'))
    rows = []
    for r, row in enumerate(controls):
        rows.append([Paragraph(c, st_th if r == 0 else st_td) for c in row])
    t = Table(rows, colWidths=[44 * mm, 68 * mm, 68 * mm], hAlign='CENTER')
    t.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#b0bec5')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2f6fb2')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
         [colors.white, colors.HexColor('#f2f6fb')]),
    ]))
    story.append(Spacer(1, 4 * mm))
    story.append(t)
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph('Геймпад по Bluetooth и экранные стики на '
                           'планшете — тот же лад, что и у клавиатуры: '
                           'левый стик газ/рыск, правый тангаж/крен.',
                           st_p))

    def bg(canv, doc):
        canv.saveState()
        canv.setFillColor(colors.HexColor('#eef4fb'))
        canv.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
        if canv.getPageNumber() == 1:
            canv.setStrokeColor(colors.HexColor('#2f6fb2'))
            canv.setLineWidth(1.6)
            canv.line(20, 42, A4[0] - 20, 42)
        canv.setFont('DJV', 8)
        canv.setFillColor(colors.HexColor('#546e7a'))
        canv.drawCentredString(A4[0] / 2, 14,
                               'drone-trainer · брошюра скриншотов · '
                               'https://pop31-ai.github.io/drone-trainer/')
        canv.restoreState()

    pdf_path = os.path.join(OUT, 'Брошюра_скриншоты_дрона.pdf')
    doc = BaseDocTemplate(pdf_path, pagesize=A4, title='Тренажёр дрона — '
                          'брошюра скриншотов', author='drone-trainer')
    doc.addPageTemplates([PageTemplate(id='all',
                                       frames=[Frame(16 * mm, 16 * mm,
                                                     A4[0] - 32 * mm,
                                                     A4[1] - 34 * mm,
                                                     id='f')],
                                       onPage=bg)])
    doc.build(story)
    print('PDF:', pdf_path)
    return pdf_path


if __name__ == '__main__':
    build()