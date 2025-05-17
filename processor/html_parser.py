from bs4 import BeautifulSoup

def extract_text_from_html(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    headings = [tag.get_text(strip=True) for tag in soup.find_all(['h1', 'h2', 'h3'])]
    paragraphs = [tag.get_text(strip=True) for tag in soup.find_all('p')]

    		# Amazon-style price extraction 
    price_tags = soup.select("span.a-offscreen")
    prices = [tag.get_text(strip=True) for tag in price_tags]

    extracted = "\n".join(headings + paragraphs + prices)
    return extracted
