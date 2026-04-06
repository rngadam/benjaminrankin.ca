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

        browser.close()

if __name__ == "__main__":
    test_navigation_and_menu()
    print("Regression test passed.")