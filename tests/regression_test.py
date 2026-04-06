from playwright.sync_api import sync_playwright, expect
import os
import datetime
import subprocess

def get_git_branch():
    try:
        branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode('utf-8').strip()
        return branch
    except Exception:
        return "unknown"

def test_navigation_and_menu():
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    branch = get_git_branch()
    prefix = f"{date_str}-{branch}"

    os.makedirs("screenshots", exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        page.goto("http://localhost:8000")

        # Initial screenshot
        page.screenshot(path=f"screenshots/{prefix}-desktop.png")

        # Verify the desktop menu is hidden (we removed it, so we can verify mobile menu is present)
        mobile_menu = page.locator("#mobile-menu")
        expect(mobile_menu).to_be_hidden()

        # Click the hamburger menu
        menu_btn = page.locator("#mobile-menu-btn")
        expect(menu_btn).to_be_visible()
        menu_btn.click()

        # Wait for menu to be visible without timeout
        expect(mobile_menu).to_be_visible()

        # Take screenshot of the menu open to retain the screenshot functionality
        page.screenshot(path=f"screenshots/{prefix}-menu_open.png")

        # Validate all URLs
        links = page.locator("a").element_handles()
        urls_to_check = set()
        for link in links:
            href = link.get_attribute("href")
            if href and not href.startswith("#") and not href.startswith("mailto:") and not href.startswith("data:text/calendar"):
                # Handle relative URLs
                if href.startswith("/"):
                    urls_to_check.add(f"http://localhost:8000{href}")
                elif href.startswith("http"):
                    urls_to_check.add(href)
                else:
                    urls_to_check.add(f"http://localhost:8000/{href}")

        print(f"Validating {len(urls_to_check)} URLs...")

        # We need a new context with a larger timeout to check external links
        # Greenparty site blocks automated requests, so we simulate a real browser
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        check_page = context.new_page()

        failed_urls = []
        for url in urls_to_check:
            try:
                print(f"Checking {url}...")
                response = check_page.goto(url, wait_until="domcontentloaded", timeout=15000)
                # Some sites return 403, 401, 405 for bots, and instagram returns 429 too often. We'll consider those okay for this simple check
                # as long as we reached a server that responded
                if response and response.status >= 400 and response.status not in (403, 401, 405, 429):
                    failed_urls.append(f"{url} (Status: {response.status})")
            except Exception as e:
                failed_urls.append(f"{url} (Error: {str(e)})")

        if failed_urls:
            print("Failed URLs:")
            for failed_url in failed_urls:
                print(f"  - {failed_url}")
            raise Exception("Some URLs are unreachable or invalid.")

        browser.close()

if __name__ == "__main__":
    test_navigation_and_menu()
    print("Regression test passed.")