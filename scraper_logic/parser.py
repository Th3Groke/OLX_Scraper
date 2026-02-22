from scraper_logic.engine import get_page_html
from scraper_logic.models import Listing
from bs4 import BeautifulSoup


def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    print("parsing data...")
    return soup.find_all('div', {'data-testid': 'l-card'})


def serialize_data(listings):
    offers = []
    for item in listings:
        title_tag = item.select_one('h4') or item.select_one('h6')
        price_tag = item.select_one('[data-testid="ad-price"]')
        loc_date_tag = item.select_one('[data-testid="location-date"]')
        link_tag = item.select_one('a')

        if all([title_tag, price_tag, loc_date_tag]):
            title = title_tag.get_text(strip=True)
            price = price_tag.get_text(strip=True)

            raw_loc_date = loc_date_tag.get_text(strip=True)
            parts = raw_loc_date.split("-")

            location = parts[0].strip() if len(parts) > 0 else "Unknown"
            date = parts[1].strip() if len(parts) > 1 else "Unknown"

            href = link_tag.get('href', '') if link_tag else ''
            link = f"https://www.olx.pl{href}" if href.startswith(
                '/') else href

            offers.append(Listing(title, price, location, date, link))
        else:
            continue

    return offers


def serialize_run(window, url):
    html = get_page_html(window, url)
    listings = parse_html(html)
    data = serialize_data(listings)
    return data
