from playwright.sync_api import sync_playwright, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto("http://localhost:8000/")

    # Check Donate Section
    expect(page.get_by_text("Donate", exact=True)).to_be_visible()
    expect(page.get_by_placeholder("101")).to_be_visible()

    # Check Provider Selection
    expect(page.get_by_label("Razorpay")).to_be_visible()
    expect(page.get_by_label("Stripe")).to_be_visible()
    expect(page.get_by_label("PayPal")).to_be_visible()

    # Check Default State (Razorpay selected, others hidden)
    expect(page.locator("#razorpay-section")).to_be_visible()
    expect(page.locator("#stripe-section")).not_to_be_visible()
    expect(page.locator("#paypal-section")).not_to_be_visible()

    # Take screenshot
    page.screenshot(path="frontend_verification_payment.png", full_page=True)

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
