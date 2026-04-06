from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1280, "height": 720})
    page.goto("http://localhost:8000")
    page.screenshot(path="screenshot_desktop.png")

    # Take screenshot of the menu open
    page.click("#mobile-menu-btn")
    page.wait_for_timeout(500) # Wait for menu to open
    page.screenshot(path="screenshot_menu_open.png")

    browser.close()
