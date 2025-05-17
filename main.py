import time
start_time = time.time()


from html_fetcher import fetch_and_save_html
from processor.html_parser import extract_text_from_html
from summarizer import clean_and_structure_full_text
import os

if __name__ == "__main__":
    url = input("🔗 Enter the URL to scrape: ")
    html_path = fetch_and_save_html(url)

    print("\n📄 Extracting clean text from HTML...")
    clean_text = extract_text_from_html(html_path)

    
    base_name = os.path.basename(html_path).replace(".html", "")
    parsed_path = os.path.join("outputs", "summaries", f"{base_name}_parsed_text.txt")
    with open(parsed_path, "w", encoding="utf-8") as f:
        f.write(clean_text)
    print(f"📝 Parsed text saved to: {parsed_path}")

    
    print("\n🧠 Cleaning and structuring full text with LM Labs (streaming output)...")
    formatted_text = clean_and_structure_full_text(clean_text)

    
    formatted_path = os.path.join("outputs", "summaries", f"{base_name}_formatted.txt")
    with open(formatted_path, "w", encoding="utf-8") as f:
        f.write(formatted_text)
    print(f"\n✅ Final structured output saved to: {formatted_path}")


from screenshot_scroller import take_screenshot
from ocr_extractor import extract_text_from_screenshot
from summarizer import clean_and_structure_full_text  # reuses same function for OCR cleanup

print("\n📸 Taking full-page screenshot...")
screenshot_path = take_screenshot(url)

print("\n🔍 Running OCR on the screenshot...")
ocr_file_path, ocr_text = extract_text_from_screenshot(screenshot_path)

ocr_raw_path = ocr_file_path  # already saved by extract_text_from_screenshot

print("\n🧹 Cleaning and structuring OCR text with LM Labs...")
formatted_ocr_text = clean_and_structure_full_text(ocr_text)

ocr_base = os.path.basename(screenshot_path).replace(".png", "")
formatted_ocr_path = os.path.join("outputs", "summaries", f"{ocr_base}_ocr_cleaned.txt")
with open(formatted_ocr_path, "w", encoding="utf-8") as f:
    f.write(formatted_ocr_text)
print(f"\n✅ Final structured OCR output saved to: {formatted_ocr_path}")

from summarizer import merge_and_deduplicate_text

with open(formatted_path, "r", encoding="utf-8") as f:
    html_cleaned = f.read()

with open(formatted_ocr_path, "r", encoding="utf-8") as f:
    ocr_cleaned = f.read()

merged_text = merge_and_deduplicate_text(html_cleaned, ocr_cleaned)

merged_path = os.path.join("outputs", "summaries", f"{base_name}_merged_cleaned.txt")
with open(merged_path, "w", encoding="utf-8") as f:
    f.write(merged_text)

print(f"\n✅ Merged, deduplicated final text saved to: {merged_path}")

from summarizer import generate_excel_data_from_merged_text
from excel_builder import save_product_table_to_excel

with open(merged_path, "r", encoding="utf-8") as f:
    merged_text = f.read()

excel_data = generate_excel_data_from_merged_text(merged_text)

excel_output_path = os.path.join("outputs", "excels", f"{base_name}_final.xlsx")
save_product_table_to_excel(excel_data, excel_output_path)

print(f"\n✅ Final Excel saved to: {excel_output_path}")

import glob

print("\n🧹 Cleaning up temporary files...")

for file in glob.glob("outputs/html/*.html"):
    os.remove(file)

for file in glob.glob("outputs/screenshots/*.png"):
    os.remove(file)

for file in glob.glob("outputs/summaries/*.txt"):
    os.remove(file)

print("✅ All intermediate files removed.")

end_time = time.time()
elapsed = end_time - start_time
mins, secs = divmod(elapsed, 60)
print(f"\n⏱️ Time Elapsed: {int(mins)} min {int(secs)} sec")

