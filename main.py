import requests
from bs4 import BeautifulSoup
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

def scrape_product(url: str) -> dict:
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "lxml")
    
    name  = soup.select_one("h1.prod-name")
    price = soup.select_one("span.price-new")
    
    return {
        "name":  name.text.strip()  if name  else None,
        "price": price.text.strip() if price else None,
        "url":   url,
    }

url = "https://www.morele.net/procesor-intel-core-i5-123456"
product = scrape_product(url)
print(product)