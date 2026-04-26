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
    "GPU":           "https://www.morele.net/kategoria/karty-graficzne-12/",
    "CPU":           "https://www.morele.net/kategoria/procesory-45/",
    "RAM":           "https://www.morele.net/kategoria/pamieci-ram-38/",
    "SSD":           "https://www.morele.net/kategoria/dyski-ssd-518/",
    "HDD":           "https://www.morele.net/kategoria/dyski-hdd-4/",
    "Monitory":      "https://www.morele.net/kategoria/monitory-523/",
    "Płyty główne":  "https://www.morele.net/kategoria/plyty-glowne-44/",
}

def get_max_pages(url: str) -> int:
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "lxml")
        pages = soup.select(".pagination-btn-nolink-anchor")
        return max((int(p.text.strip()) for p in pages if p.text.strip().isdigit()), default=1)
    except Exception:
        return 1

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

        # DEBUG — usuń po naprawieniu
        karty = soup.select(".cat-product.card")
        st.write(f"Strona {strona} — znaleziono kart: {len(karty)}, status: {response.status_code}")

        for card in karty:
            name      = card.select_one(".cat-product-name__header a")
            price_val = card.get("data-product-price")

            if name and price_val:
                try:
                    produkty.append({
                        "nazwa": name.text.strip(),
                        "cena":  float(price_val),
                    })
                except ValueError:
                    continue

        time.sleep(1)

    return produkty


# ── UI ────────────────────────────────────────────────────

st.title("🖥️ Porównywarka cen komponentów PC")
st.write("Wybierz komponent i sprawdź ceny na morele.net")

komponent = st.selectbox("Wybierz komponent:", list(KATEGORIE.keys()))

with st.spinner("Pobieram liczbę stron..."):
    url        = KATEGORIE[komponent]
    max_strony = get_max_pages(url)

st.write(f"Dostępne strony: **{max_strony}**")
strony = st.slider("Ile stron przeszukać?", min_value=1, max_value=max_strony, value=1)

if st.button("🔍 Szukaj cen"):
    with st.spinner("Scrapuję morele.net..."):
        produkty = scrape_kategoria(url, strony)

    if not produkty:
        st.error("Nie znaleziono produktów — sprawdź debug powyżej.")
    else:
        ceny = [p["cena"] for p in produkty]

        st.success(f"Znaleziono {len(produkty)} produktów")

        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Minimalna",  f"{min(ceny):,.2f} zł")
        col2.metric("📊 Średnia",    f"{sum(ceny)/len(ceny):,.2f} zł")
        col3.metric("💎 Maksymalna", f"{max(ceny):,.2f} zł")

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