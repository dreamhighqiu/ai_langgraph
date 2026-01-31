"""
Webpage analyzer using Playwright (direct library usage, not MCP).
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

try:
    from playwright.sync_api import sync_playwright, Page, Browser
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

from ..core.config import get_config


@dataclass
class PageElement:
    """Page element metadata."""
    tag: str
    type: Optional[str] = None
    name: Optional[str] = None
    id: Optional[str] = None
    text: Optional[str] = None
    placeholder: Optional[str] = None
    required: bool = False
    disabled: bool = False
    attributes: Dict[str, str] = field(default_factory=dict)


@dataclass
class AnalysisResult:
    """Analysis result for a page."""
    url: str
    title: str
    timestamp: str
    elements: Dict[str, List[PageElement]] = field(default_factory=dict)
    forms: List[Dict] = field(default_factory=list)
    api_requests: List[Dict] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    screenshot_path: Optional[str] = None


class WebpageAnalyzer:
    """
    Webpage analyzer using Playwright to extract elements and interactions.

    Authentication methods:
    - storage: use saved browser storage state (recommended; manual login first)
    - form: automatic form login
    - sso: SSO/OAuth login (manual interaction required)
    """

    def __init__(
        self,
        headless: bool = True,
        timeout: int = 60000,
        slow_mo: int = 0,
        auth_state: Optional[str] = None,
        login_url: Optional[str] = None,
    ):
        """
        Args:
            headless: whether to run headless
            timeout: navigation timeout in ms
            slow_mo: slow motion in ms
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError(
                "Playwright not installed. Run: pip install playwright && playwright install chromium"
            )

        self.headless = headless
        self.timeout = timeout
        self.slow_mo = slow_mo
        self.config = get_config()
        self.auth_config = self.config.get_section('auth')
        if auth_state:
            self.auth_config = dict(self.auth_config)
            self.auth_config['enabled'] = True
            self.auth_config['method'] = 'storage'
            self.auth_config['storage_state'] = auth_state
        if login_url:
            self.auth_config = dict(self.auth_config)
            self.auth_config['login_url'] = login_url

    def save_auth_state(
        self,
        storage_path: str = None,
        login_url: Optional[str] = None,
        timeout_ms: Optional[int] = None,
        wait_until: str = "domcontentloaded",
    ):
        """
        Manual login and save browser storage state.

        Steps:
        1. Opens a headed browser.
        2. Login manually.
        3. Press Enter in the terminal to save storage state.
        """
        storage_path = storage_path or self.auth_config.get('storage_state', './auth_state.json')
        login_url = login_url or self.auth_config.get('login_url', '')

        print("[login] Open browser for manual login...")
        print(f"[login] Login URL: {login_url}")
        print("[login] Complete login in browser, then press Enter to save state.")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(viewport={'width': 1920, 'height': 1080})
            page = context.new_page()

            if login_url:
                goto_timeout = timeout_ms or self.timeout
                page.goto(login_url, wait_until=wait_until, timeout=goto_timeout)

            input("\n[login] Press Enter after login completes...")

            context.storage_state(path=storage_path)
            print(f"[login] Auth state saved to: {storage_path}")

            browser.close()

    def analyze(
        self,
        url: str,
        screenshot: bool = True,
        capture_network: bool = True,
        output_dir: str = None,
    ) -> AnalysisResult:
        """
        Analyze a webpage.

        Args:
            url: target URL
            screenshot: capture screenshot
            capture_network: capture network requests
            output_dir: output directory for screenshots
        """
        result = AnalysisResult(
            url=url,
            title="",
            timestamp=datetime.now().isoformat(),
        )

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless, slow_mo=self.slow_mo)
            context = self._create_context(browser)
            page = context.new_page()

            if capture_network:
                page.on('request', lambda req: self._handle_request(req, result))

            try:
                if self.auth_config.get('enabled', False):
                    self._handle_auth(page)

                print("[analyze] Loading page...")
                page.goto(url, wait_until='domcontentloaded', timeout=self.timeout)

                page.wait_for_timeout(3000)

                try:
                    page.wait_for_load_state('networkidle', timeout=10000)
                except Exception:
                    print("[analyze] Network still busy; continue analysis.")

                result.title = page.title()
                print(f"[analyze] Title: {result.title}")
                result.elements = self._extract_elements(page)
                result.forms = self._extract_forms(page)

                if screenshot:
                    screenshot_name = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    if output_dir:
                        Path(output_dir).mkdir(parents=True, exist_ok=True)
                        screenshot_path = str(Path(output_dir) / screenshot_name)
                    else:
                        screenshot_path = screenshot_name
                    page.screenshot(path=screenshot_path, full_page=True)
                    result.screenshot_path = screenshot_path
                    print(f"[analyze] Screenshot saved: {screenshot_path}")

            except Exception as e:
                result.errors.append(str(e))
            finally:
                browser.close()

        return result

    def _create_context(self, browser: "Browser"):
        """Create browser context, optionally with auth state."""
        storage_state = None

        if self.auth_config.get('enabled', False):
            method = self.auth_config.get('method', 'storage')
            if method == 'storage':
                storage_path = self.auth_config.get('storage_state', './auth_state.json')
                if Path(storage_path).exists():
                    storage_state = storage_path
                    print(f"[auth] Using saved auth state: {storage_path}")
                else:
                    print(f"[auth] Auth state file not found: {storage_path}")
                    if self.auth_config.get('auto_login', True):
                        login_url = self.auth_config.get('login_url', '')
                        login_timeout = self.auth_config.get('login_timeout', self.timeout)
                        login_wait_until = self.auth_config.get('login_wait_until', 'domcontentloaded')
                        if login_url:
                            self.save_auth_state(
                                storage_path=storage_path,
                                login_url=login_url,
                                timeout_ms=login_timeout,
                                wait_until=login_wait_until,
                            )
                            if Path(storage_path).exists():
                                storage_state = storage_path
                        else:
                            print("[auth] login_url is not set; skip auto login.")
                    else:
                        print("[auth] Run: python -m ui_agent login")

        return browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            storage_state=storage_state,
        )

    def _handle_auth(self, page: "Page"):
        """Handle authentication if configured."""
        method = self.auth_config.get('method', 'storage')

        if method == 'form':
            self._form_login(page)
        elif method == 'storage':
            pass

    def _form_login(self, page: "Page"):
        """Form-based login."""
        form_config = self.auth_config.get('form', {})
        login_url = self.auth_config.get('login_url', '')

        if login_url:
            page.goto(login_url, wait_until='networkidle')

        username = form_config.get('username', '')
        password = form_config.get('password', '')

        if username and password:
            page.fill(form_config.get('username_selector', 'input[name="username"]'), username)
            page.fill(form_config.get('password_selector', 'input[name="password"]'), password)
            page.click(form_config.get('submit_selector', 'button[type="submit"]'))

            wait_time = self.auth_config.get('wait_after_login', 3000)
            page.wait_for_timeout(wait_time)

            success_selector = self.auth_config.get('success_selector', '')
            if success_selector:
                page.wait_for_selector(success_selector, timeout=10000)

    def _handle_request(self, request, result: AnalysisResult):
        """Capture network requests."""
        if request.resource_type in ['xhr', 'fetch']:
            result.api_requests.append({
                'url': request.url,
                'method': request.method,
                'resource_type': request.resource_type,
            })

    def _extract_elements(self, page: "Page") -> Dict[str, List[Dict]]:
        """Extract elements from the page."""
        elements = {
            'inputs': [],
            'buttons': [],
            'links': [],
            'selects': [],
            'textareas': [],
            'tables': [],
            'modals': [],
            'tabs': [],
        }

        for el in page.locator('input').all():
            try:
                elements['inputs'].append({
                    'type': el.get_attribute('type') or 'text',
                    'name': el.get_attribute('name'),
                    'id': el.get_attribute('id'),
                    'placeholder': el.get_attribute('placeholder'),
                    'required': el.get_attribute('required') is not None,
                    'disabled': el.get_attribute('disabled') is not None,
                    'data-testid': el.get_attribute('data-testid'),
                    'aria-label': el.get_attribute('aria-label'),
                })
            except Exception:
                pass

        for el in page.locator('button, input[type="button"], input[type="submit"], [role="button"]').all():
            try:
                text = (el.text_content() or '').strip()
                if not text:
                    text = el.get_attribute('aria-label') or ''
                if not text:
                    text = el.get_attribute('title') or ''
                if not text:
                    text = el.get_attribute('value') or ''
                if not text:
                    span = el.locator('span').first
                    if span.count() > 0:
                        text = (span.text_content() or '').strip()

                is_visible = el.is_visible()

                elements['buttons'].append({
                    'text': text,
                    'type': el.get_attribute('type'),
                    'name': el.get_attribute('name'),
                    'id': el.get_attribute('id'),
                    'class': el.get_attribute('class'),
                    'disabled': el.get_attribute('disabled') is not None or el.get_attribute('aria-disabled') == 'true',
                    'data-testid': el.get_attribute('data-testid'),
                    'aria-label': el.get_attribute('aria-label'),
                    'visible': is_visible,
                })
            except Exception:
                pass

        for el in page.locator('a[href]').all():
            try:
                href = el.get_attribute('href')
                if href and not href.startswith('#'):
                    elements['links'].append({
                        'text': el.text_content().strip() if el.text_content() else '',
                        'href': href,
                        'id': el.get_attribute('id'),
                    })
            except Exception:
                pass

        for el in page.locator('select').all():
            try:
                options = []
                for opt in el.locator('option').all():
                    options.append({
                        'value': opt.get_attribute('value'),
                        'text': opt.text_content(),
                    })
                elements['selects'].append({
                    'name': el.get_attribute('name'),
                    'id': el.get_attribute('id'),
                    'options': options,
                })
            except Exception:
                pass

        for el in page.locator('table, [role="grid"]').all():
            try:
                headers = []
                for th in el.locator('th').all():
                    header_text = (th.text_content() or '').strip()
                    if header_text:
                        headers.append(header_text)

                if not headers:
                    first_row = el.locator('tr').first
                    if first_row.count() > 0:
                        for cell in first_row.locator('td, th').all():
                            header_text = (cell.text_content() or '').strip()
                            if header_text:
                                headers.append(header_text)

                row_count = len(el.locator('tbody tr, tr').all())

                sample_data = []
                for row in el.locator('tbody tr').all()[:3]:
                    row_data = []
                    for cell in row.locator('td').all():
                        cell_text = (cell.text_content() or '').strip()[:50]
                        row_data.append(cell_text)
                    if row_data:
                        sample_data.append(row_data)

                elements['tables'].append({
                    'headers': headers,
                    'row_count': row_count,
                    'sample_data': sample_data,
                    'has_checkbox': el.locator('input[type="checkbox"]').count() > 0,
                    'has_actions': el.locator('button, [role="button"]').count() > 0,
                })
            except Exception:
                pass

        for el in page.locator('[role="dialog"], .modal, [aria-modal="true"]').all():
            try:
                elements['modals'].append({
                    'id': el.get_attribute('id'),
                    'aria-label': el.get_attribute('aria-label'),
                })
            except Exception:
                pass

        for el in page.locator('[role="tablist"]').all():
            try:
                tabs = []
                for tab in el.locator('[role="tab"]').all():
                    tabs.append({
                        'text': tab.text_content(),
                        'selected': tab.get_attribute('aria-selected') == 'true',
                    })
                elements['tabs'].append({'tabs': tabs})
            except Exception:
                pass

        elements['interactive'] = []
        interactive_selector = '''
            button, input, select, textarea, a[href],
            [role="button"], [role="link"], [role="checkbox"], [role="radio"],
            [role="textbox"], [role="combobox"], [role="option"],
            [onclick], [tabindex]:not([tabindex="-1"]),
            zeta-option, zeta-radio-button, zeta-checkbox
        '''

        for el in page.locator(interactive_selector).all():
            try:
                if not el.is_visible():
                    continue

                tag_name = el.evaluate('el => el.tagName.toLowerCase()')
                text = (el.text_content() or '').strip()[:100]

                elem_info = {
                    'tag': tag_name,
                    'text': text,
                    'id': el.get_attribute('id'),
                    'name': el.get_attribute('name'),
                    'class': el.get_attribute('class'),
                    'type': el.get_attribute('type'),
                    'role': el.get_attribute('role'),
                    'aria-label': el.get_attribute('aria-label'),
                    'placeholder': el.get_attribute('placeholder'),
                    'data-testid': el.get_attribute('data-testid'),
                    'value': el.get_attribute('value'),
                }

                elem_info = {k: v for k, v in elem_info.items() if v}
                elements['interactive'].append(elem_info)
            except Exception:
                pass

        return elements

    def _extract_forms(self, page: "Page") -> List[Dict]:
        """Extract forms from the page."""
        forms = []
        for form in page.locator('form').all():
            try:
                form_data = {
                    'id': form.get_attribute('id'),
                    'name': form.get_attribute('name'),
                    'action': form.get_attribute('action'),
                    'method': form.get_attribute('method') or 'get',
                    'fields': [],
                }

                for field in form.locator('input, select, textarea').all():
                    form_data['fields'].append({
                        'tag': field.evaluate('el => el.tagName.toLowerCase()'),
                        'type': field.get_attribute('type'),
                        'name': field.get_attribute('name'),
                        'required': field.get_attribute('required') is not None,
                    })

                forms.append(form_data)
            except Exception:
                pass

        return forms

    def to_dict(self, result: AnalysisResult) -> Dict:
        """Convert result to dict."""
        return {
            'url': result.url,
            'title': result.title,
            'timestamp': result.timestamp,
            'elements': result.elements,
            'forms': result.forms,
            'api_requests': result.api_requests,
            'errors': result.errors,
            'screenshot_path': result.screenshot_path,
        }

    def save_result(self, result: AnalysisResult, output_path: str):
        """Save analysis result to JSON."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(result), f, ensure_ascii=False, indent=2)
