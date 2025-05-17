import requests
import json

LM_LABS_URL = "http://192.168.1.4:1234/v1/chat/completions"
MODEL = "meta-llama-3.1-8b-instruct"  # or whatever LM Studio shows exactly


def clean_and_structure_full_text(text: str) -> str:
    prompt = f"""
Clean and organize the following extracted product text from a website.

🟢 Tasks:
- Preserve all real product data exactly.
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
                print(content, end="", flush=True)  # 🔴 LIVE OUTPUT
                final_output += content
        return final_output.strip()

    except Exception as e:
        return f"❌ Failed: {e}"
