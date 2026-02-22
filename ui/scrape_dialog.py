from PyQt6.QtWidgets import (
    QDialog, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QVBoxLayout, QPushButton)
from PyQt6.QtCore import QThread, Qt, pyqtSignal
from PyQt6.QtGui import QCloseEvent, QIntValidator

from constants import URL
from database_handling import DBinsertData
from scraper_logic.parser import serialize_run


class ScrapeDialog(QDialog):
    url = URL

    def __init__(self):
        super().__init__()
        self.setWindowTitle("scraper")
        self.setWindowFlag(Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.current_name = 'iphone'
        self.current_min_scrape = None
        self.current_max_scrape = None

        layout = QVBoxLayout()
        self.scrape_btn = QPushButton("Scrape")
        self.label = QLabel("log: ")
        self.log = QTextEdit()
        self.log.setReadOnly(True)

        settings_btn = QPushButton("Settings")
        layout.addWidget(settings_btn)
        layout.addWidget(self.scrape_btn)
        layout.addWidget(self.label)
        layout.addWidget(self.log)

        self.setLayout(layout)

        settings_btn.clicked.connect(self.open_settings)
        self.scrape_btn.clicked.connect(self.start_task)

    def closeEvent(self, event: QCloseEvent):
        print("saving to db")
        event.accept()

    def start_task(self):
        self.log.append("Starting scraper...")
        name = self.current_name
        min_scrape = self.current_min_scrape
        max_scrape = self.current_max_scrape
        target_url = self.build_olx_url(URL, name, min_scrape, max_scrape)
        self.worker = ScraperWorker(target_url)
        self.worker.new_listing_signal.connect(self.display_listing)
        self.worker.new_status.connect(self.display_status)
        self.worker.start()

    def build_olx_url(self, base, name='iphone', min_p=None, max_p=None):
        url = str(base).rstrip('/')
        params = []
        if name and str(name).strip():
            name = name.replace(' ', '-')
            url += f"/q-{name}"
        params.append(f"search[order]=created_at:desc")
        if min_p and str(min_p).strip():
            params.append(f"search[filter_float_price:from]={min_p}")
        if max_p and str(max_p).strip():
            params.append(f"search[filter_float_price:to]={max_p}")

        if params:
            url += "/?" + "&".join(params)
        return url

    def display_listing(self, text):
        self.log.append(f"Found: {text}")

    def display_status(self, text):
        self.log.append(f"{text}")

    def open_settings(self):
        dialog = ScrapeSettingsDialog(
            self.current_name, self.current_min_scrape, self.current_max_scrape)
        if dialog.exec():
            self.current_name = dialog.result_name
            self.current_min_scrape = dialog.result_min
            self.current_max_scrape = dialog.result_max


class ScraperWorker(QThread):
    new_listing_signal = pyqtSignal(str)
    new_status = pyqtSignal(str)

    def __init__(self, target_url):
        super().__init__()
        self.target_url = target_url

    def run(self):
        print(f"scraping: {self.target_url}")
        self.new_status.emit(f"scraping: {self.target_url}")

        data = serialize_run(self, self.target_url)
        for listing in data:
            self.new_status.emit("-"*40)
            self.new_listing_signal.emit(listing.title)
            print(listing.title)
            print(listing.price)
            print(listing.location)
            print(listing.date)
            print(listing.link)
            print("-" * 40)
        self.new_status.emit("="*20)
        self.new_status.emit(f"Found {len(data)} listings")
        self.new_status.emit("Close this window to save the listings")
        DBinsertData(data)


class ScrapeSettingsDialog(QDialog):
    def __init__(self, current_name, current_min, current_max):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setWindowTitle("Settings")
        self.current_name = current_name
        self.current_min = current_min
        self.current_max = current_max
        layout = QVBoxLayout()
        nameLayout = QHBoxLayout()
        maxPriceLayout = QHBoxLayout()
        minPriceLayout = QHBoxLayout()
        self.nameBox = QLineEdit(self.current_name)
        self.minPriceBox = QLineEdit(self.current_min)
        self.maxPriceBox = QLineEdit(self.current_max)
        self.minPriceBox.setValidator(QIntValidator(0, 100000))
        self.maxPriceBox.setValidator(QIntValidator(0, 100000))
        confirmButton = QPushButton("confirm")
        confirmButton.clicked.connect(self.updateSettings)
        nameLayout.addWidget(QLabel("Name: "))
        nameLayout.addWidget(self.nameBox)
        minPriceLayout.addWidget(QLabel("Min price: "))
        minPriceLayout.addWidget(self.minPriceBox)
        maxPriceLayout.addWidget(QLabel("Max price: "))
        maxPriceLayout.addWidget(self.maxPriceBox)
        layout.addLayout(nameLayout)
        layout.addLayout(minPriceLayout)
        layout.addLayout(maxPriceLayout)
        layout.addWidget(confirmButton)

        self.setLayout(layout)

    def updateSettings(self):
        self.result_name = self.nameBox.text()
        self.result_min = self.minPriceBox.text()
        self.result_max = self.maxPriceBox.text()
        self.accept()
