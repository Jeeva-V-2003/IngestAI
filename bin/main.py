from html_fetcher import fetch_and_save_html
from processor.html_parser import extract_text_from_html
from summarizer import clean_and_structure_full_text
import os

if __name__ == "__main__":
    url = input("🔗 Enter the URL to scrape: ")
    html_path = fetch_and_save_html(url)

    print("\n📄 Extracting clean text from HTML...")
    clean_text = extract_text_from_html(html_path)

    # Save parsed text before sending to AI
    base_name = os.path.basename(html_path).replace(".html", "")
    parsed_path = os.path.join("outputs", "summaries", f"{base_name}_parsed_text.txt")
    with open(parsed_path, "w", encoding="utf-8") as f:
        f.write(clean_text)
    print(f"📝 Parsed text saved to: {parsed_path}")

    # Send full parsed text to LM Labs for AI cleanup
    print("\n🧠 Cleaning and structuring full text with LM Labs (streaming output)...")
    formatted_text = clean_and_structure_full_text(clean_text)

    # Save cleaned AI result
    formatted_path = os.path.join("outputs", "summaries", f"{base_name}_formatted.txt")
    with open(formatted_path, "w", encoding="utf-8") as f:
        f.write(formatted_text)
    print(f"\n✅ Final structured output saved to: {formatted_path}")
