import streamlit as st
import requests
from bs4 import BeautifulSoup
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

KATEGORIE = {
    "GPU":                    "https://www.morele.net/kategoria/karty-graficzne-12/",
    "CPU":                    "https://www.morele.net/kategoria/procesory-45/",
    "RAM":                    "https://www.morele.net/kategoria/pamieci-ram-38/",
    "SSD":                    "https://www.morele.net/kategoria/dyski-ssd-518/",
    "HDD":                    "https://www.morele.net/kategoria/dyski-hdd-4/",
    "Monitory":               "https://www.morele.net/kategoria/monitory-523/",
    "Płyty główne":           "https://www.morele.net/kategoria/plyty-glowne-44/",
}

def scrape_kategoria(url: str, strony: int = 2) -> list[dict]:
    produkty = []

    for strona in range(1, strony + 1):
        page_url = f"{url},,,,,,,,0,,,,/{strona}/"
        try:
            response = requests.get(page_url, headers=HEADERS, timeout=10)
            response.raise_for_status()
        except Exception as e:
            st.warning(f"Błąd na stronie {strona}: {e}")
            break

        soup = BeautifulSoup(response.text, "lxml")

        for card in soup.select(".cat-product-card"):
            name  = card.select_one(".product-title")
            price = card.select_one(".price-new")

            if name and price:
                # Wyciągamy samą liczbę z ceny np. "1 234,56 zł" -> 1234.56
                price_text = price.text.strip()
                price_text = price_text.replace("\xa0", "").replace(" ", "").replace("zł", "").replace(",", ".")
                try:
                    price_val = float(price_text)
                except ValueError:
                    continue

                produkty.append({
                    "nazwa": name.text.strip(),
                    "cena":  price_val,
                })

        time.sleep(1)

    return produkty


# ── UI Streamlit ──────────────────────────────────────────

st.title("🖥️ Porównywarka cen komponentów PC")
st.write("Wybierz komponent i sprawdź ceny na morele.net")

komponent = st.selectbox("Wybierz komponent:", list(KATEGORIE.keys()))

strony = st.slider("Ile stron przeszukać?", min_value=1, max_value=5, value=2)

if st.button("🔍 Szukaj cen"):
    with st.spinner("Scrapuję morele.net..."):
        url      = KATEGORIE[komponent]
        produkty = scrape_kategoria(url, strony)

    if not produkty:
        st.error("Nie znaleziono produktów. Selektory CSS mogły się zmienić.")
    else:
        ceny = [p["cena"] for p in produkty]

        st.success(f"Znaleziono {len(produkty)} produktów")

        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Minimalna cena", f"{min(ceny):,.2f} zł")
        col2.metric("📊 Średnia cena",   f"{sum(ceny)/len(ceny):,.2f} zł")
        col3.metric("💎 Maksymalna cena", f"{max(ceny):,.2f} zł")

        st.divider()

        min_prod = min(produkty, key=lambda x: x["cena"])
        max_prod = max(produkty, key=lambda x: x["cena"])

        st.write(f"**Najtańszy:** {min_prod['nazwa']} — {min_prod['cena']:,.2f} zł")
        st.write(f"**Najdroższy:** {max_prod['nazwa']} — {max_prod['cena']:,.2f} zł")

        st.divider()
        st.subheader("Wszystkie produkty")
        st.dataframe(
            sorted(produkty, key=lambda x: x["cena"]),
            use_container_width=True
        )