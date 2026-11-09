from __future__ import annotations

import os
import socket
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest
from playwright.sync_api import Error as PlaywrightError, sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return int(sock.getsockname()[1])


def _wait_for_server(url: str, process: subprocess.Popen, timeout: float = 25) -> None:
    deadline = time.monotonic() + timeout
    last_error = None
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"Uvicorn exited early with code {process.returncode}")
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except Exception as error:  # server is still starting
            last_error = error
            time.sleep(.25)
    raise RuntimeError(f"Server did not become ready: {last_error}")


@pytest.fixture(scope='module')
def running_app(tmp_path_factory):
    port = _free_port()
    database = tmp_path_factory.mktemp('browser-e2e') / 'algoforge.db'
    env = os.environ.copy()
    env.update({
        'DATABASE_URL': f'sqlite:///{database.as_posix()}',
        'APP_ENV': 'development',
        'COOKIE_SECURE': 'false',
        'PUBLIC_BASE_URL': f'http://127.0.0.1:{port}',
    })
    process = subprocess.Popen(
        [sys.executable, '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', str(port)],
        cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
    )
    base_url = f'http://127.0.0.1:{port}'
    try:
        _wait_for_server(f'{base_url}/api/health', process)
        yield base_url
    finally:
        process.terminate()
        try:
            process.wait(timeout=8)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def _launch_chromium(playwright):
    executable = os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE') or shutil.which('chromium')
    if executable:
        return playwright.chromium.launch(headless=True, executable_path=executable, args=['--no-sandbox'])
    return playwright.chromium.launch(headless=True, args=['--no-sandbox'])


def _goto_local(page, url: str):
    try:
        return page.goto(url, wait_until='domcontentloaded')
    except PlaywrightError as error:
        if 'ERR_BLOCKED_BY_ADMINISTRATOR' in str(error):
            pytest.skip('This managed execution environment blocks Chromium access to loopback HTTP; CI runs the same browser checks on its runner.')
        raise


def test_browser_learning_paths_navigation_and_progress_surfaces(running_app):
    with sync_playwright() as playwright:
        browser = _launch_chromium(playwright)
        page = browser.new_page(viewport={'width': 1365, 'height': 900})
        page_errors = []
        page.on('pageerror', lambda error: page_errors.append(str(error)))
        _goto_local(page, f'{running_app}/#/roadmap')
        page.get_by_role('heading', name='Learning paths').wait_for()
        assert page.locator('.path-card').count() == 4
        assert page.get_by_role('navigation', name='Workspace navigation').count() == 1
        assert page.locator('main#main-content').count() == 1
        assert page.locator('.path-module').count() >= 20
        assert page.locator('.path-question').count() > 0
        assert not page_errors, page_errors
        browser.close()


def test_browser_theme_toggle_and_mobile_learning_path_layout(running_app):
    with sync_playwright() as playwright:
        browser = _launch_chromium(playwright)
        page = browser.new_page(viewport={'width': 1365, 'height': 900})
        _goto_local(page, f'{running_app}/#/roadmap')
        page.get_by_role('heading', name='Learning paths').wait_for()
        theme = page.locator('button[data-action="theme"]')
        assert theme.count() == 1
        before = page.locator('html').get_attribute('data-theme')
        theme.click()
        after = page.locator('html').get_attribute('data-theme')
        assert before != after
        assert page.evaluate("localStorage.getItem('algoforge-theme')") == after
        page.set_viewport_size({'width': 390, 'height': 844})
        page.wait_for_timeout(150)
        widths = page.evaluate("({viewport: document.documentElement.clientWidth, document: document.documentElement.scrollWidth})")
        assert widths['document'] <= widths['viewport'], widths
        assert page.locator('.path-card').count() == 4
        browser.close()


def test_browser_problem_workspace_exposes_function_mode_for_new_adapter(running_app):
    with sync_playwright() as playwright:
        browser = _launch_chromium(playwright)
        page = browser.new_page(viewport={'width': 1365, 'height': 900})
        _goto_local(page, f'{running_app}/#/problem/af-valid-parentheses')
        page.locator('#editor-mode-select').wait_for()
        page.locator('#editor-mode-select').select_option('function')
        assert page.locator('#editor-mode-select').input_value() == 'function'
        assert page.locator('#language-select').count() == 1
        assert page.locator('.workspace-grid').count() == 1
        browser.close()
