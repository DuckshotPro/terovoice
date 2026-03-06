from playwright.sync_api import sync_playwright, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()

    # Mock the onboarding state API call
    page.route("**/api/onboarding/123", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='''{
            "currentStep": 2,
            "progress": 20,
            "forwardingNumber": "+15551234567",
            "smsEnabled": true,
            "smsPhoneNumber": "+15551234567"
        }'''
    ))

    # Mock the test SMS API call
    page.route("**/api/onboarding/123/test-sms", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"success": true, "message": "Test SMS sent successfully"}'
    ))

    # Navigate to the onboarding page
    page.goto("http://localhost:5173/onboarding/123")

    # Wait for the page to load
    page.wait_for_selector("text=Phone Configuration")

    # Verify SMS checkbox is checked
    expect(page.locator("input[name=smsEnabled]")).to_be_checked()

    # Click the Test SMS button
    test_button = page.get_by_text("Test SMS")
    test_button.click()

    # Verify success message
    expect(page.get_by_text("Test SMS sent successfully!")).to_be_visible()

    # Take screenshot
    page.screenshot(path="verification_sms.png")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
