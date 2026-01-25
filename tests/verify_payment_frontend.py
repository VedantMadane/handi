from playwright.sync_api import sync_playwright, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto("http://localhost:8000/")

    # Check Donate Section
    expect(page.get_by_text("Donate", exact=True)).to_be_visible()
    expect(page.get_by_placeholder("101")).to_be_visible()

    # Take screenshot of Home Page with Donate Button
    page.screenshot(path="frontend_verification_payment.png")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
