import easyocr
import os

def extract_text_from_screenshot(image_path: str) -> (str, str):
    
    reader = easyocr.Reader(['en'], gpu=True)
    results = reader.readtext(image_path, detail=0)
    extracted_text = "\n".join(results)

    
    base = os.path.basename(image_path).replace(".png", "_ocr.txt")
    output_path = os.path.join("outputs", "summaries", base)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(extracted_text)
    print(f"✅ OCR text saved to: {output_path}")
    return output_path, extracted_text
