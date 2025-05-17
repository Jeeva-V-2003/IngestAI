import difflib
from summarizer import call_lm_labs  

def load_text(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().splitlines()

def recover_missing_lines(parsed_path, formatted_path):
    parsed_lines = load_text(parsed_path)
    formatted_lines = load_text(formatted_path)

   
    combined_formatted = "\n".join(formatted_lines).lower()

    recovered_lines = []
    for line in parsed_lines:
        if len(line.strip()) < 50:
            continue
        if any(x in line.lower() for x in ['skip to', 'related', 'need help', 'keyboard shortcuts']):
            continue
        if line.lower() not in combined_formatted:
            print(f"🔍 Missing line detected:\n{line[:100]}...")
            prompt = f"""This line was missed from structured output. Clean and format it as if part of a website product list:\n\n\"{line.strip()}\""""
            cleaned = call_lm_labs(prompt)
            recovered_lines.append(cleaned)

    print(f"\n✅ Recovered {len(recovered_lines)} missed lines.\n")
    return "\n\n".join(recovered_lines)
