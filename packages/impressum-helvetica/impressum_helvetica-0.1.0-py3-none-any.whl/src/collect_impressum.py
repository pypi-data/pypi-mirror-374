#!/usr/bin/env python3
"""
collect_impressum.py

Usage:
    python collect_impressum.py [hostname]

Examples:
    python collect_impressum.py digitec.ch
    python collect_impressum.py          # Uses hostnames from src/hostnames.py
"""

import sys
import os
import asyncio
from urllib.parse import urlparse, urlunparse, urljoin
import json
import re

from PIL import Image
from playwright.async_api import async_playwright

# -------------------- Settings --------------------

OUTPUT_DIR = "results"

BROWSER_TYPE = "chrome"
VIEWPORT_WIDTH = 1280
VIEWPORT_HEIGHT = 800
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)

COOKIE_BANNER_WAIT = 2000
DYNAMIC_CONTENT_WAIT = 1500
COOKIE_CLICK_WAIT = 1000

COOKIE_ACCEPT_KEYWORDS = [
    "akzeptieren","accept","accept all","accept cookies","accepter","accepter tout",
    "ok","agree","consent","allow all","allow cookies","got it","i understand","continue",
]

IMPRESSUM_KEYWORDS = [
    {"term": "impressum", "prio": 1},        # German - highest priority
    {"term": "legal notice", "prio": 2},    # English
    {"term": "legal", "prio": 2},           # English (short)
    {"term": "mentions légales", "prio": 2},# French
    {"term": "mentions legales", "prio": 2},# French (no accent)
    {"term": "notice légale", "prio": 2},   # French (variant)
    {"term": "notice legale", "prio": 2},   # French (no accent)
    {"term": "about us", "prio": 2},        # English
    {"term": "contact", "prio": 2},         # fallback, common legal/contact page
]

HTML_EXTENSION = ".html"
PNG_EXTENSION = ".png"
HTML_SUBFOLDER = "html"
IMG_SUBFOLDER = "img"
DEFAULT_PROTOCOL = "https://"

# Screenshot output caps
MAX_OUT_W = 1280
MAX_OUT_H = 5000          # final image height cap

# -------------------- Hostname loader --------------------

def load_hostnames_from_file(filepath: str = "./src/hostnames.py") -> list:
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("hostnames_module", filepath)
        hostnames_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(hostnames_module)
        return hostnames_module.hostnames
    except Exception as e:
        print(f"Error loading hostnames from {filepath}: {e}")
        return []

# -------------------- Helpers --------------------

def _normalize_url(hostname: str) -> str:
    if not hostname.startswith(("http://", "https://")):
        url = f"{DEFAULT_PROTOCOL}{hostname}"
    else:
        url = hostname
    _p = urlparse(url)
    if _p.netloc and not _p.netloc.startswith("www."):
        url = urlunparse((_p.scheme, "www."+_p.netloc, _p.path, _p.params, _p.query, _p.fragment))
    return url

async def _launch(browser_name, p):
    if browser_name == "chromium":
        browser = await p.chromium.launch(args=["--disable-http2"])
    elif browser_name == "firefox":
        browser = await p.firefox.launch()
    elif browser_name == "webkit":
        browser = await p.webkit.launch()
    else:
        raise ValueError("unknown browser")

    context = await browser.new_context(
        viewport={"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT},
        user_agent=USER_AGENT,
        ignore_https_errors=True,
        locale="de-CH",
        extra_http_headers={"Accept-Language": "de-CH,de;q=0.9,en-US;q=0.8,en;q=0.7,fr;q=0.6"},
    )
    page = await context.new_page()
    page.set_default_timeout(15000)
    page.set_default_navigation_timeout(20000)
    return browser, context, page

async def _with_browser_fallbacks(task_fn):
    order = ["chromium", "firefox", "webkit"]
    pref = (BROWSER_TYPE or "chrome").lower()
    if pref == "chrome":
        pref = "chromium"
    if pref in order:
        order.remove(pref)
        order.insert(0, pref)

    async with async_playwright() as p:
        last_err = None
        for engine in order:
            browser = context = page = None
            try:
                browser, context, page = await _launch(engine, p)
                print(f"→ Using engine: {engine}")
                result = await task_fn(page, engine)
                await context.close()
                await browser.close()
                return result
            except Exception as e:
                last_err = e
                try:
                    if context: await context.close()
                except Exception:
                    pass
                try:
                    if browser: await browser.close()
                except Exception:
                    pass
                print(f"⚠️  {engine} failed: {e}")
                continue
        raise last_err if last_err else RuntimeError("all engines failed")

# -------------------- Smart screenshot --------------------

async def _smart_screenshot(page, png_path: str):
    """
    Crop to visible content, not the entire scroll height.
    Strategy:
      1) Pick width from content.
      2) Find bottom-most element that actually contains text/meaningful content.
      3) Clip to [0, 0, width, content_bottom + padding].
      4) Downscale if above caps.
    """
    await page.evaluate("window.scrollTo(0,0)")

    try:
        content_w = await page.evaluate(
            "Math.min(document.documentElement.scrollWidth || 1280, 1600)"
        )
    except Exception:
        content_w = 1280
    ideal_w = max(800, min(int(content_w), MAX_OUT_W))
    await page.set_viewport_size({"width": ideal_w, "height": 900})

    # Compute bottom of meaningful content
    js = """
(() => {
  const MIN_TEXT = 16;           // ignore tiny labels
  const PAD = 24;                // extra pixels at bottom
  const nodes = Array.from(document.body.querySelectorAll('*'));
  let bottom = 0;

  // prefer main/article/section when available
  const anchors = document.querySelectorAll('main, article, [role="main"], .content, .page, .page-wrapper');
  const base = anchors.length ? anchors : nodes;

  for (const el of base) {
    const st = getComputedStyle(el);
    if (st.visibility !== 'visible' || st.display === 'none') continue;
    const rect = el.getBoundingClientRect();
    if (rect.width < 4 || rect.height < 4) continue;

    // heuristic: text length or interactive container
    const txt = (el.innerText || '').trim();
    const dense = txt.length >= MIN_TEXT || el.querySelector('p,li,ul,ol,table,article,section,header,footer,h1,h2,h3');
    if (!dense) continue;

    bottom = Math.max(bottom, rect.bottom);
  }
  // Fallback if nothing matched
  if (!bottom) bottom = document.documentElement.scrollHeight;

  const width = Math.max(document.documentElement.clientWidth, document.documentElement.scrollWidth);
  return { width: Math.ceil(width), height: Math.ceil(bottom) + PAD };
})()
"""
    bounds = await page.evaluate(js)
    clip_w = min(max(ideal_w, 320), MAX_OUT_W)
    clip_h = min(max(bounds.get("height", 900), 300), MAX_OUT_H)

    await page.screenshot(path=png_path, clip={"x": 0, "y": 0, "width": clip_w, "height": clip_h})

    # Safety downscale (usually no-op because we clipped)
    try:
        with Image.open(png_path) as im:
            w, h = im.size
            if w > MAX_OUT_W or h > MAX_OUT_H:
                scale = min(MAX_OUT_W / w, MAX_OUT_H / h)
                im = im.resize((max(1, int(w*scale)), max(1, int(h*scale))), Image.LANCZOS)
                im.save(png_path, optimize=True)
    except Exception as e:
        print(f"⚠️  Resize skipped: {e}")

# -------------------- Core capture flow --------------------

async def _common_capture_flow(page, engine_name, url, html_path, png_path):
    resp = await page.goto(url, wait_until="domcontentloaded")
    if not resp or resp.status >= 400:
        print(f"⚠️  First load status {resp.status if resp else 'None'}; retrying once")
        await page.wait_for_timeout(500)
        resp = await page.reload(wait_until="domcontentloaded")
    if not resp or resp.status >= 400:
        print(f"⚠️  Warning: got HTTP {resp.status if resp else 'None'} ({engine_name})")

    print("→ Checking for cookie consent banners...")
    await page.wait_for_timeout(COOKIE_BANNER_WAIT)
    cookie_found = False
    for keyword in COOKIE_ACCEPT_KEYWORDS:
        try:
            button = await page.locator(f'button:has-text("{keyword}")').first
            if not await button.count():
                button = await page.locator(f'a:has-text("{keyword}")').first
            if not await button.count():
                button = await page.locator(
                    f'[class*="accept"], [class*="cookie"], [id*="accept"], [id*="cookie"]:has-text("{keyword}")'
                ).first
            if await button.count():
                print(f"→ Found cookie accept button: '{keyword}', clicking...")
                await button.click()
                cookie_found = True
                await page.wait_for_timeout(COOKIE_CLICK_WAIT)
                break
        except Exception:
            continue
    if not cookie_found:
        print("→ No cookie banner found or already accepted")

    await page.wait_for_timeout(DYNAMIC_CONTENT_WAIT)

    impressum_href = None
    candidate_links = []
    links = await page.query_selector_all('a')
    impressum_candidates = []  # Store all matching links with their priority
    
    for link in links:
        try:
            text = (await link.inner_text()).strip().lower()
        except Exception:
            text = ''
        if not text:
            try:
                text = (await link.text_content() or '').strip().lower()
            except Exception:
                text = ''
        href = await link.get_attribute('href')
        href_lc = href.lower() if href else ''
        candidate_links.append((text, href))
        
        # Check for keyword matches and store with priority
        for keyword_dict in IMPRESSUM_KEYWORDS:
            keyword = keyword_dict["term"]
            priority = keyword_dict["prio"]
            if keyword in text or keyword in href_lc:
                impressum_candidates.append((href, priority, keyword))
                break  # Only one match per link
    
    # Select the link with the highest priority (lowest priority number)
    if impressum_candidates:
        impressum_candidates.sort(key=lambda x: x[1])  # Sort by priority
        impressum_href = impressum_candidates[0][0]
        matched_keyword = impressum_candidates[0][2]
        print(f"→ Found {len(impressum_candidates)} impressum candidate(s), selected '{matched_keyword}' (priority {impressum_candidates[0][1]})")

    navigation_success = False
    if impressum_href:
        print(f"→ Found Impressum link: {impressum_href}, navigating...")
        impressum_url = urljoin(url, impressum_href)
        try:
            resp = await page.goto(impressum_url, wait_until="domcontentloaded")
            if not resp or resp.status >= 400:
                print(f"⚠️  Warning: got HTTP {resp.status if resp else 'None'} (Impressum)")
            else:
                navigation_success = True
        except Exception as nav_err:
            print(f"❌ Failed to navigate to Impressum: {nav_err}")
            print("→ Trying link click fallback...")
            try:
                await page.go_back(wait_until="domcontentloaded")
                await page.click(f'a[href="{impressum_href}"]', timeout=4000)
                await page.wait_for_load_state("domcontentloaded", timeout=8000)
                navigation_success = True
            except Exception as click_err:
                print(f"→ Click fallback failed: {click_err}")
                print("→ Staying on current page and capturing that instead")
        if navigation_success:
            print("→ Successfully navigated to Impressum, capturing...")
        else:
            print("→ Capturing current page instead")
    else:
        print("→ No Impressum link found, capturing home page.")
        print("→ Debug: sample of <a> links found:")
        for t, h in candidate_links[:10]:
            print(f"  text: '{t}' | href: '{h}'")

    try:
        html = await page.content()
        print(f"→ Saving HTML to {html_path} ({engine_name})")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
    except Exception as save_err:
        print(f"❌ Failed saving HTML: {save_err}")

    try:
        print(f"→ Taking smart screenshot to {png_path} ({engine_name})")
        await _smart_screenshot(page, png_path)
    except Exception as shot_err:
        print(f"❌ Failed taking screenshot: {shot_err}")

# -------------------- Tasks --------------------

async def _task_capture(hostname: str, output_dir: str):
    url = _normalize_url(hostname)
    parsed = urlparse(url)
    base = parsed.netloc.replace(":", "_")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, HTML_SUBFOLDER), exist_ok=True)
    os.makedirs(os.path.join(output_dir, IMG_SUBFOLDER), exist_ok=True)
    html_path = os.path.join(output_dir, HTML_SUBFOLDER, f"{base}{HTML_EXTENSION}")
    png_path = os.path.join(output_dir, IMG_SUBFOLDER, f"{base}{PNG_EXTENSION}")

    async def run(page, engine):
        if any(h in parsed.netloc for h in ["digitec.ch"]) or hostname.endswith("digitec.ch"):
            direct = "https://www.digitec.ch/en/guide/47"
            try:
                print(f"→ Attempt direct Impressum: {direct}")
                resp = await page.goto(direct, wait_until="domcontentloaded")
                if resp and (resp.status < 400):
                    print("→ Direct Impressum load OK")
                    try:
                        html = await page.content()
                        print(f"→ Saving HTML to {html_path} ({engine})")
                        with open(html_path, "w", encoding="utf-8") as f:
                            f.write(html)
                    except Exception as save_err:
                        print(f"❌ Failed saving HTML: {save_err}")
                    try:
                        print(f"→ Taking smart screenshot to {png_path} ({engine})")
                        await _smart_screenshot(page, png_path)
                    except Exception as shot_err:
                        print(f"❌ Failed taking screenshot: {shot_err}")
                    return
                else:
                    print("→ Direct Impressum returned bad status; falling back to home flow")
            except Exception as e:
                print(f"→ Direct Impressum attempt failed: {e}. Falling back to home flow.")
        await _common_capture_flow(page, engine, url, html_path, png_path)

    await _with_browser_fallbacks(run)

async def _task_capture_return(hostname: str, output_dir: str):
    url = _normalize_url(hostname)
    parsed = urlparse(url)
    base = parsed.netloc.replace(":", "_")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, HTML_SUBFOLDER), exist_ok=True)
    os.makedirs(os.path.join(output_dir, IMG_SUBFOLDER), exist_ok=True)
    html_path = os.path.join(output_dir, HTML_SUBFOLDER, f"{base}{HTML_EXTENSION}")
    png_path = os.path.join(output_dir, IMG_SUBFOLDER, f"{base}{PNG_EXTENSION}")

    result = {"impressum_url": None}

    async def run(page, engine):
        if any(h in parsed.netloc for h in ["digitec.ch"]) or hostname.endswith("digitec.ch"):
            direct = "https://www.digitec.ch/en/guide/47"
            try:
                print(f"→ Attempt direct Impressum: {direct}")
                resp = await page.goto(direct, wait_until="domcontentloaded")
                if resp and (resp.status < 400):
                    result["impressum_url"] = page.url
                    try:
                        html = await page.content()
                        print(f"→ Saving HTML to {html_path} ({engine})")
                        with open(html_path, "w", encoding="utf-8") as f:
                            f.write(html)
                    except Exception as save_err:
                        print(f"❌ Failed saving HTML: {save_err}")
                    try:
                        print(f"→ Taking smart screenshot to {png_path} ({engine})")
                        await _smart_screenshot(page, png_path)
                    except Exception as shot_err:
                        print(f"❌ Failed taking screenshot: {shot_err}")
                    return
                else:
                    print("→ Direct Impressum returned bad status; falling back to home flow")
            except Exception as e:
                print(f"→ Direct Impressum attempt failed: {e}. Falling back to home flow.")

        before = None

        async def wrapped(page_inner, engine_inner, url_inner, html_p, png_p):
            nonlocal before
            before = page_inner.url or url_inner
            await _common_capture_flow(page_inner, engine_inner, url_inner, html_p, png_p)

        await wrapped(page, engine, url, html_path, png_path)
        after = page.url
        if after and after != before:
            result["impressum_url"] = after

    await _with_browser_fallbacks(run)
    return result["impressum_url"]

# -------------------- Public API --------------------

async def capture(hostname: str, output_dir: str = OUTPUT_DIR):
    await _task_capture(hostname, output_dir)

async def capture_and_return_impressum_url(hostname: str, output_dir: str = OUTPUT_DIR):
    return await _task_capture_return(hostname, output_dir)

# -------------------- CLI --------------------

if __name__ == "__main__":
    if len(sys.argv) == 2:
        hostname = sys.argv[1]
        print(f"→ Processing single hostname: {hostname}")
        asyncio.run(capture(hostname))
    elif len(sys.argv) == 1:
        print("→ No hostname provided, loading hostnames from src/hostnames.py...")
        hostnames = load_hostnames_from_file()

        if not hostnames:
            print("❌ No hostnames found in src/hostnames.py")
            print("Please run src/environment.py first to generate the hostnames file.")
            sys.exit(1)

        hostnames_to_process = [entry for entry in hostnames if entry.get("url_to_impressum") is None]

        async def main_batch():
            hostnames_to_process = [entry for entry in hostnames if entry.get("url_to_impressum") is None]
            if not hostnames_to_process:
                print("✅ All hostnames already have url_to_impressum values. Nothing to process.")
                return

            print(f"→ Found {len(hostnames_to_process)} hostnames to process (with url_to_impressum = None)")
            print(f"→ Skipping {len(hostnames) - len(hostnames_to_process)} hostnames that already have url_to_impressum values")

            for i, host_entry in enumerate(hostnames_to_process, 1):
                hostname = host_entry["hostname"]
                print(f"\n→ Processing hostname {i}/{len(hostnames_to_process)}: {hostname}")
                try:
                    impressum_url = await capture_and_return_impressum_url(hostname)
                    host_entry["url_to_impressum"] = impressum_url if impressum_url else None
                except Exception as e:
                    print(f"❌ Failed to process {hostname}: {e}")
                    host_entry["url_to_impressum"] = None
                    continue

            try:
                with open("./src/hostnames.py", "w") as f:
                    py_content = json.dumps(hostnames, indent=2)
                    py_content = re.sub(r":\s*null", ": None", py_content)
                    f.write(f"hostnames = {py_content}\n")
                print("✅ Updated src/hostnames.py with Impressum URLs.")
            except Exception as e:
                print(f"❌ Failed to write updated hostnames: {e}")
            print(f"\n✅ Completed processing {len(hostnames)} hostnames")

        asyncio.run(main_batch())
    else:
        print(__doc__)
        sys.exit(1)