import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless") # Run headless so no browser window opens
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Setup webdriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Open the application
    driver.get("http://127.0.0.1:8080")
    print("✅ Opened BeeSmart Spelling Bee App")

    # Give the page time to load, especially the 3D avatar
    time.sleep(5)

    print(driver.page_source)

    # Find the avatar controls
    print("🔎 Finding avatar controls...")
    zoom_in_btn = driver.find_element(By.CSS_SELECTOR, "[data-testid='zoom-in-btn']")
    zoom_out_btn = driver.find_element(By.CSS_SELECTOR, "[data-testid='zoom-out-btn']")
    rotate_left_btn = driver.find_element(By.CSS_SELECTOR, "[data-testid='rotate-left-btn']")
    rotate_right_btn = driver.find_element(By.CSS_SELECTOR, "[data-testid='rotate-right-btn']")
    reset_view_btn = driver.find_element(By.CSS_SELECTOR, "[data-testid='reset-view-btn']")
    print("✅ Found all avatar control buttons.")

    # --- Test each button ---
    print("\n▶️ Testing Zoom In...")
    zoom_in_btn.click()
    time.sleep(1)
    print("✅ Clicked Zoom In")

    print("\n▶️ Testing Zoom Out...")
    zoom_out_btn.click()
    time.sleep(1)
    print("✅ Clicked Zoom Out")

    print("\n▶️ Testing Rotate Left...")
    rotate_left_btn.click()
    time.sleep(1)
    print("✅ Clicked Rotate Left")

    print("\n▶️ Testing Rotate Right...")
    rotate_right_btn.click()
    time.sleep(1)
    print("✅ Clicked Rotate Right")

    print("\n▶️ Testing Reset View...")
    reset_view_btn.click()
    time.sleep(1)
    print("✅ Clicked Reset View")

    # Check for any JavaScript errors in the browser console
    errors = driver.get_log('browser')
    js_errors = [error for error in errors if error['level'] == 'SEVERE']

    if not js_errors:
        print("\n✅🎉 Smoke test passed! No severe JavaScript errors detected.")
    else:
        print("\n❌🔥 Smoke test failed! Severe JavaScript errors found:")
        for error in js_errors:
            print(f"  - {error['message']}")

except Exception as e:
    print(f"\n❌ An error occurred during the test: {e}")

finally:
    # Clean up
    driver.quit()
    print("\n✅ Browser closed.")
