import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

def take_screenshot(url: str) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    screenshot_path = os.path.join("outputs", "screenshots", f"page_{timestamp}.png")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  
        context = browser.new_context(
            viewport={"width": 1600, "height": 900},
            device_scale_factor=1.0,  
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            print("🔗 Opening page...")
            page.goto(url, timeout=90000)
            page.wait_for_selector("body", timeout=10000)

            
            scroll_height = page.evaluate("document.body.scrollHeight")
            for step in range(0, scroll_height, 300):
                page.evaluate(f"window.scrollTo(0, {step})")
                time.sleep(0.2)

            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)

            
            full_height = page.evaluate("document.body.scrollHeight")
            page.set_viewport_size({"width": 1600, "height": full_height})
            page.screenshot(path=screenshot_path, full_page=True)

        except Exception as e:
            print(f"❌ Screenshot failed: {e}")
            return None
        finally:
            browser.close()

    
    for _ in range(10):
        if os.path.exists(screenshot_path):
            return screenshot_path
        time.sleep(0.2)

    print("❌ Screenshot file not found after save.")
    return None
