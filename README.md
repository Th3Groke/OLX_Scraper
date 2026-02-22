# 📱 OLX Scraper Dashboard

A modern desktop application built with **PyQt6** and **Selenium** that scrapes listings from OLX.pl, stores them in a local SQLite database, and provides a searchable, filtered dashboard.

## ✨ Features
* **Asynchronous Scraping:** Uses `QThread` to keep the UI responsive while Selenium fetches data in the background.
* **Smart Duplicate Prevention:** Uses URL checks against the database to ensure no duplicate entries are saved.
* **Dynamic UI:**
    * Floating "No records" placeholder that centers automatically on app launch and window resize.
    * Real-time search bar to filter visible results instantly.
    * Custom tile-based list view for clear listing presentation.
* **Persistent Filters:** Database-side filtering for price ranges and multiple sorting options (Price, Alphabetical, and Newest).
* **Custom Scraping Settings:** Dynamically constructs complex OLX search URLs based on user keywords and price limits.

## 📦 Downloads
For non-technical users, you can download the latest standalone version from the [Releases](https://github.com/Th3Groke/OLX_Scraper/releases) page.

**Note: Requires Google Chrome to be installed.**


## 🚀 Developer setup

### 1. Prerequisites
* Python 3.10+
* Google Chrome installed (The scraper uses the installed browser version via Selenium).

### 2. Setup
Clone the repository and install dependencies:

```bash
git clone https://github.com/Th3Groke/OLX_Scraper.git
cd OLX_Scraper
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/Mac:
source .venv/bin/activate
pip install -r requirements.txt
```
## 🛠️ Usage
Launch the App:
```bash
python main.py
```

Scrape Data: Click the Scrape button to open the scraper window. Use the Settings inside that window to define your keyword (e.g., "iPhone 13") and price range.

Manage Database: Once the scraper finishes, close the scraper window. The main dashboard will automatically refresh to show new records.

Explore: Use the Filters on the main dashboard to sort existing records by price or name. Use the Search Bar for instant text-based filtering.

## 📁 Project Structure
```plaintext
OLX_Scraper/
├── main.py                # Application entry point
├── config.py              # Centralized configuration and CSS selectors 
├── database_handling.py   # SQLite logic and dynamic SQL query building 
├── serialization.py       # Data transformation and Listing object creation 
├── scraper.py             # Selenium-based HTML fetching and BeautifulSoup parsing 
├── listing.py             # Data model for individual OLX offers 
├── ui/                    # Directory for all PyQt6 graphical components 
│   ├── main_window.py     # Primary dashboard logic and search debouncing 
│   ├── scrape_dialog.py   # Scraper window logic and QThread worker 
│   └── components.py      # Reusable widgets (ListingTiles, ConfirmDialogs) 
├── requirements.txt       # Project dependencies 
└── .gitignore             # Git exclusion rules
```
## 📝 License
Distributed under the MIT License. See LICENSE for more information.
