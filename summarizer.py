import requests
import json
import re
import threading
import time

LM_LABS_URL = "http://192.168.1.4:1234/v1/chat/completions"
MODEL = "meta-llama-3.1-8b-instruct"  


def clean_and_structure_full_text(text: str) -> str:
    prompt = f"""
Clean and organize the following extracted product text from a website.

🟢 Tasks:
- Preserve all real product data exactly.
- All product's price is under the given main block correspondingly.If it is not related or coresponding then ignore it.
- For each product, neatly format the information in separate blocks for easy copying to Excel.
- Do not skip any product.

🔍 Extracted Text:
{text}
"""

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You clean and format website data into readable, structured blocks."},
            {"role": "user", "content": prompt}
        ],
        "stream": True,
        "temperature": 0.3
    }

    print("📡 Sending full parsed data to LM Labs...\n")

    try:
        response = requests.post(LM_LABS_URL, json=payload, stream=True)
        response.raise_for_status()

        final_output = ""
        for line in response.iter_lines(decode_unicode=True):
            if line and line.startswith("data: "):
                raw_data = line[6:]
                if raw_data.strip() == "[DONE]":
                    break
                data = json.loads(raw_data)
                content = data["choices"][0]["delta"].get("content", "")
                print(content, end="", flush=True)  
                final_output += content
        return final_output.strip()

    except Exception as e:
        return f"❌ Failed: {e}"

def clean_and_structure_ocr_text(ocr_text: str) -> str:
    prompt = f"""
Clean and organize the following product information extracted via OCR from a webpage screenshot.

 Tasks:
- Retain all important details from each line.
- Ignore unrelated lines like 'need help', 'related searches', etc.
- Present each product cleanly and clearly.
- Do not summarize. Just reformat accurately.
- Preserve all real product data exactly.
- For each product, neatly format the information in separate blocks for easy copying to Excel.
- Do not skip any product.

 OCR Extracted Text:
{ocr_text}
"""

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You clean and format raw OCR text into readable, structured product descriptions."},
            {"role": "user", "content": prompt}
        ],
        "stream": True,
        "temperature": 0.3
    }

    print("📡 Sending OCR text to LM Labs...\n")

    try:
        response = requests.post(LM_LABS_URL, json=payload, stream=True)
        response.raise_for_status()

        final_output = ""
        for line in response.iter_lines(decode_unicode=True):
            if line and line.startswith("data: "):
                raw_data = line[6:]
                if raw_data.strip() == "[DONE]":
                    break
                data = json.loads(raw_data)
                content = data["choices"][0]["delta"].get("content", "")
                print(content, end="", flush=True)
                final_output += content
        return final_output.strip()

    except Exception as e:
        return f"❌ OCR cleanup failed: {e}"

def merge_and_deduplicate_text(html_cleaned: str, ocr_cleaned: str) -> str:
    prompt = f"""
You will receive two structured blocks of product listings:
- One from HTML parsing
- One from OCR extraction

Task Objective:
Combine both blocks into a complete product list for Excel generation.

Deduplication Rules:
- Only remove entries that are 100% identical across all fields
- If product entries have the same name or model but vary in specs (RAM, Storage, Color, Price, etc.), keep them all
- Do NOT merge variants — treat them as separate products

Formatting:
- Output each product in clear, structured, block-wise format
- Maintain numbering: Product 1, Product 2, ...
- Include all available fields: Product Name, Brand, Model, Chip, RAM, Storage, Display, Color, Battery, Price, Charger, OS, etc.
- If a field is missing, leave it blank
- Money conversion is should be ruppees as given price data.

Strictly Avoid:
- Summarizing or rephrasing
- Guessing or interpolating missing fields
- Dropping partially-filled products

Final Output Must:
- Include every product from both blocks
- Preserve all variants
- Be clean and structured for JSON conversion




📦 HTML-Cleaned Block:
{html_cleaned}

🖼️ OCR-Cleaned Block:
{ocr_cleaned}
"""

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are an expert in cleaning and merging structured product data."},
            {"role": "user", "content": prompt}
        ],
        "stream": True,
        "temperature": 0.3
    }

    print("\n🧠 Merging HTML and OCR cleaned data with LM Labs...\n")

    try:
        response = requests.post(LM_LABS_URL, json=payload, stream=True)
        response.raise_for_status()

        merged_output = ""
        for line in response.iter_lines(decode_unicode=True):
            if line and line.startswith("data: "):
                raw_data = line[6:]
                if raw_data.strip() == "[DONE]":
                    break
                data = json.loads(raw_data)
                content = data["choices"][0]["delta"].get("content", "")
                print(content, end="", flush=True)
                merged_output += content
        return merged_output.strip()

    except Exception as e:
        return f"❌ Merge failed: {e}"

def loading_animation(msg="⏳ Waiting for AI response"):
    i = 0
    chars = "|/-\\"
    while not getattr(threading.current_thread(), "stop", False):
        print(f"\r{msg}... {chars[i % 4]}", end="", flush=True)
        i += 1
        time.sleep(0.2)
    print("\r✅ Response received.                      ")

def generate_excel_data_from_merged_text(merged_text: str) -> list:
    prompt = f"""
You are given a cleaned block-wise product listing.

Task:
Extract all fields into structured JSON format.

Requirements:
- Output must be JSON only, no text or comments
- Each product = one JSON object
- Final output = an array of objects

Fields to include:
- Product Name
- Brand
- Model
- Chip / Processor
- RAM
- Storage
- Display
- Battery
- Color
- Charger
- OS
- Price

Do not:
- Skip or guess missing fields
- Include any extra message or explanation
- Wrap the result in markdown

Output Example:
[
  {{
    "Product Name": "Apple MacBook Air",
    "Brand": "Apple",
    "Model": "2025 M4 (13-inch)",
    "Chip": "Apple M4 chip with 10-core CPU and 10-core GPU",
    "RAM": "16GB Unified Memory",
    "Storage": "512GB",
    "Display": "13.6\\" Liquid Retina",
    "Battery": "",
    "Color": "Midnight",
    "Charger": "",
    "OS": "macOS 15",
    "Price": "\u20B91,24,900"
  }},
  ...
]


Text:
{merged_text}
"""


    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are an AI that converts structured product listings into clean Excel row data."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "stream": False
    }

    try:
        print("\n📊 Generating intelligent Excel table via LM Labs...")

        
        spinner = threading.Thread(target=loading_animation)
        spinner.start()

        response = requests.post(LM_LABS_URL, json=payload)
        spinner.stop = True
        spinner.join()

        response.raise_for_status()
        result = response.json()["choices"][0]["message"]["content"]

        
        json_matches = re.findall(r"\[\s*{.*?}\s*\]", result, re.DOTALL)
        if json_matches:
            return json.loads(json_matches[0])
        else:
            print("\n❌ Could not extract valid JSON block from AI response.")
            return []

    except Exception as e:
        print("\n❌ Excel JSON generation failed:", e)
        return []