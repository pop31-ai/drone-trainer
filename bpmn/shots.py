# -*- coding: utf-8 -*-
"""Захват скриншотов тренажёра через headless Chromium + SwiftShader WebGL.

Скриншоты:
  sc_start.png  — стартовый экран (меню миссий)
  sc_pad.png    — дрон на стартовом подиуме (без меню)
  sc_hover.png  — миссия 1: зависание на 4 м, следящая камера
  sc_orbit.png  — орбитальная камера вокруг дрона
  sc_land.png   — мягкая посадка в красное кольцо на подиуме
  sc_ring.png   — миссия 2: пролёт синего кольца #1
  sc_slalom.png — миссия 4: слалом, полёт к воротам A

Запуск:  python shots.py  (требует python -m http.server 8123 в корне репо)
"""
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from playwright.sync_api import sync_playwright

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
os.makedirs(OUT, exist_ok=True)
URL = 'http://127.0.0.1:8123/index.html'
W, H = 1920, 1080


def shot(page, name):
    p = os.path.join(OUT, name)
    page.screenshot(path=p)
    print('скриншот:', name)


def js(page, expr):
    return page.evaluate(expr)


def keys(page, on, off=()):
    js(page, 'keys[%r]=true;' % on)
    for k in off:
        js(page, 'delete keys[%r];' % k)


def keyup(page, *names):
    for n in names:
        js(page, 'delete keys[%r];' % n)


def press(page, code):
    js(page, "document.dispatchEvent(new KeyboardEvent('keydown',{code:%r,"
             "bubbles:true,cancelable:true}));" % code)


def arm(page):
    press(page, 'KeyB')
    time.sleep(0.6)


def wait_y(page, gt, timeout=40):
    page.wait_for_function(
        '() => S.pos.y > %f' % gt, timeout=timeout * 1000)


def wait_below(page, lt, timeout=40):
    page.wait_for_function(
        '() => S.pos.y < %f' % lt, timeout=timeout * 1000)


def take_off(page, target_y=4.5, climb=6.0):
    keys(page, 'ArrowUp')
    wait_y(page, target_y)
    keyup(page, 'ArrowUp')


def start_menu(page):
    js(page, "document.getElementById('start').style.display='none'; "
             "loadMission(0);")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=[
            '--use-gl=swiftshader', '--enable-unsafe-swiftshader',
            '--disable-gpu-sandbox', '--no-sandbox',
            '--disable-dev-shm-usage'])
        ctx = browser.new_context(viewport={'width': W, 'height': H},
                                  device_scale_factor=1)
        ctx.add_init_script("try{localStorage.setItem('dt_tut','1')}catch(e){}")
        page = ctx.new_page()
        page.goto(URL, wait_until='networkidle', timeout=90000)
        page.wait_for_function("() => typeof S!=='undefined' && S.pos")
        time.sleep(2.5)

        # 1. стартовый экран
        shot(page, 'sc_start.png')

        # 2. сцена без меню: дрон на подиуме
        js(page, "loadMission(0); document.getElementById('start')"
                 ".style.display='none';")
        time.sleep(1.2)
        shot(page, 'sc_pad.png')

        # 3. зависание на 4 м (следящая камера)
        arm(page)
        take_off(page)
        time.sleep(1.0)
        shot(page, 'sc_hover.png')

        # 4. орбитальная камера
        js(page, "camMode=1; orbitYaw=-0.75; orbitPitch=0.45; orbitDist=10.5;")
        time.sleep(1.5)
        shot(page, 'sc_orbit.png')

        # 5. мягкая посадка в красное кольцо
        js(page, "camMode=0;")
        keys(page, 'ArrowDown')
        wait_below(page, 0.45)
        keyup(page, 'ArrowDown')
        press(page, 'Space')
        time.sleep(1.2)
        shot(page, 'sc_land.png')

        # 6. миссия «кольца»: пролёт синего кольца #1
        js(page, "loadMission(1);")
        time.sleep(0.8)
        arm(page)
        keys(page, 'ArrowUp')
        wait_y(page, 5.5)
        keyup(page, 'ArrowUp')
        keys(page, 'KeyW')
        page.wait_for_function(
            '() => S.pos.x > 13', timeout=40000)
        time.sleep(0.8)
        shot(page, 'sc_ring.png')
        keyup(page, 'KeyW')

        # 7. слалом: полёт к воротам A
        js(page, "loadMission(3);")
        time.sleep(0.8)
        arm(page)
        keys(page, 'ArrowUp')
        wait_y(page, 3.5)
        keyup(page, 'ArrowUp')
        keys(page, 'KeyW')
        page.wait_for_function(
            '() => S.pos.x > 10', timeout=40000)
        time.sleep(0.8)
        shot(page, 'sc_slalom.png')
        keyup(page, 'KeyW')

        browser.close()
    print('ГОТОВО. Скриншоты в:', OUT)


if __name__ == '__main__':
    main()