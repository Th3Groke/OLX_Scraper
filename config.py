URL = "https://www.olx.pl/oferty/"
FREQUENCY = 3
minPrice = 0
maxPrice = 99999

SELECTORS = {
    "card": 'div[data-testid="l-card"]',
    "title": "h6",
    "price": '[data-testid="ad-price"]',
    "cookie_btn": "onetrust-accept-btn-handler"
}
