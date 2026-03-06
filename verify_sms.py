from playwright.sync_api import sync_playwright, expect
import time

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    page.set_viewport_size({"width": 1280, "height": 1024}) # larger viewport

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

    # Wait for React to finish rendering and state updates
    page.wait_for_timeout(2000)

    # Check if checkbox is checked
    checkbox = page.locator("input[name=smsEnabled]")
    is_checked = checkbox.is_checked()
    print(f"Checkbox is checked initially: {is_checked}")

    if not is_checked:
      # We may need to force a click if the label intercept it
      page.wait_for_selector("text=Enable SMS notifications")
      label = page.locator("text=Enable SMS notifications")
      label.click()

    # fill the sms phone number
    page.wait_for_selector("input[name=smsPhoneNumber]")
    sms_input = page.locator("input[name=smsPhoneNumber]")
    sms_input.fill("+15551234567")

    # Click the Test SMS button
    test_button = page.get_by_role("button", name="Test SMS")
    test_button.click()

    # Wait for the status to change and the success message to appear
    # Wait longer and log network traffic
    page.on("request", lambda request: print(">>", request.method, request.url))
    page.on("response", lambda response: print("<<", response.status, response.url))

    page.wait_for_timeout(2000) # give it some time to make the call
    page.screenshot(path="verification_sms.png", full_page=True)

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
