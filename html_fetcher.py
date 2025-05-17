import os
from datetime import datetime
from playwright.sync_api import sync_playwright

def fetch_and_save_html(url):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"page_{timestamp}.html"
    output_path = os.path.join("outputs", "html", filename)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, timeout=60000)
            content = page.content()
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ HTML saved to: {output_path}")
        except Exception as e:
            print(f"❌ Failed to fetch HTML: {e}")
        finally:
            browser.close()

    return output_path
