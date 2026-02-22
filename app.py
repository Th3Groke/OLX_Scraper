import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QStackedLayout, QListWidgetItem, QLineEdit, QTextEdit, QLabel, QDialog, QListWidget, QComboBox)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QIntValidator, QCloseEvent

import webbrowser

from serialization import serialize_run
from config import URL, minPrice, maxPrice
from database_handling import DBloadData, DBinsertData, DBinsertDummy, DBremoveData, DBclear


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OLX Scraper Dashboard")
        self.setMinimumSize(800, 600)
        # main layout
        layout = QVBoxLayout()
        size = 0
        # topbar
        top_bar = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search...")
        filter_btn = QPushButton("Filters")
        scrape_btn = QPushButton("scrape")
        clear_btn = QPushButton("clear DB")

        top_bar.addWidget(self.search_bar)
        top_bar.addWidget(filter_btn)
        top_bar.addWidget(clear_btn)
        top_bar.addWidget(scrape_btn)
        layout.addLayout(top_bar)

        # filters tab
        self.filter_container = QWidget()
        self.filters_layout = QHBoxLayout(self.filter_container)

        self.minPriceBox = QLineEdit()
        self.maxPriceBox = QLineEdit()
        self.OrderBox = QComboBox()
        filters_done_btn = QPushButton("Done")
        self.OrderBox.addItem("ORDER BY id DESC")
        self.OrderBox.addItem("Price: Low to High")
        self.OrderBox.addItem("Price: High to Low")
        self.OrderBox.addItem("ORDER BY title ASC")

        self.filters_layout.addWidget(QLabel("Min price: "))
        self.filters_layout.addWidget(self.minPriceBox)
        self.filters_layout.addWidget(QLabel("Max price: "))
        self.filters_layout.addWidget(self.maxPriceBox)
        self.filters_layout.addWidget(QLabel("Order by: "))
        self.filters_layout.addWidget(self.OrderBox)
        self.filters_layout.addWidget(filters_done_btn)

        self.minPriceBox.setValidator(QIntValidator(0, 1000000))
        self.maxPriceBox.setValidator(QIntValidator(0, 1000000))

        layout.addWidget(self.filter_container)
        self.filter_container.hide()

        self.sizeLabel = QLabel("0 items in database")
        layout.addWidget(self.sizeLabel)

        # Listings list
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        self.placeholder_label = QLabel(
            "There are no records in the database. Start by scraping new ones", self.list_widget)
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.center_placeholder()

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        size = self.load_tiles_from_db()
        # connections
        scrape_btn.clicked.connect(self.scraper_button_clicked)
        clear_btn.clicked.connect(self.clearButtonClickedEvent)
        self.search_bar.textChanged.connect(self.filter_listings)
        filter_btn.clicked.connect(self.filters_btn_clicked_event)
        filters_done_btn.clicked.connect(self.filters_done_btn_clicked_event)

    def filter_listings(self):
        search_text = self.search_bar.text().lower()
        found_any = False

        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            tile = self.list_widget.itemWidget(item)

            if search_text in tile.title_label.text().lower():
                item.setHidden(False)
                found_any = True
            else:
                item.setHidden(True)

            if not found_any and self.list_widget.count() > 0:
                self.placeholder_label.setText(
                    f"No results matching '{search_text}'")
                self.placeholder_label.show()
            elif self.list_widget.count() > 0:
                self.placeholder_label.hide()

    def showEvent(self, event):
        super().showEvent(event)
        self.placeholder_label.setGeometry(self.list_widget.contentsRect())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'placeholder_label'):
            self.placeholder_label.setGeometry(
                0, 0, self.list_widget.width(), self.list_widget.height())

    def center_placeholder(self):
        self.placeholder_label.resize(self.list_widget.size())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            current_item = self.list_widget.currentItem()
            if current_item:
                db_id = current_item.data(Qt.ItemDataRole.UserRole)
                self.delete_from_db(db_id)
                self.list_widget.takeItem(self.list_widget.row(current_item))
                self.load_tiles_from_db()

    def filters_btn_clicked_event(self):
        if self.filter_container.isHidden():
            self.filter_container.show()
        else:
            self.filter_container.hide()

    def filters_done_btn_clicked_event(self):
        minPrice = self.minPriceBox.text()
        maxPrice = self.maxPriceBox.text()
        order = self.OrderBox.currentText()
        if minPrice == '':
            minPrice == None
        if maxPrice == '':
            maxPrice = None
        self.filter_container.hide()
        print(minPrice, maxPrice, order)
        self.load_tiles_from_db(minPrice, maxPrice, order)

    def delete_from_db(self, db_id):
        DBremoveData(db_id)

    def clearButtonClickedEvent(self):
        self.dialog = ConfirmClearDialog()
        self.dialog.destroyed.connect(
            lambda obj: self.load_tiles_from_db()
        )
        self.dialog.exec()

    def scraper_button_clicked(self):
        self.scrape = ScrapeDialog()
        self.scrape.destroyed.connect(
            lambda obj: self.load_tiles_from_db()
        )
        self.scrape.exec()

    def load_tiles_from_db(self, min_p=None, max_p=None, s_by='Newest First'):
        self.list_widget.clear()
        data = DBloadData(min_p, max_p, s_by)
        size = len(data)
        self.sizeLabel.setText(f"{size} items in database")
        if size == 0:
            self.placeholder_label.show()
        else:
            self.placeholder_label.hide()
            for price, title, link, db_id in data:
                self.add_tile(price, title, link, db_id)
        return size

    def add_tile(self, price, title, link, db_id):
        tile = ListingTile(price, title, link)
        item = QListWidgetItem(self.list_widget)
        item.setSizeHint(tile.sizeHint())
        item.setData(Qt.ItemDataRole.UserRole, db_id)

        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, tile)


class ConfirmClearDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setWindowTitle("Confirm")
        self.setWindowFlag(Qt.WindowType.Tool)
        layout = QVBoxLayout()
        text = QLabel(
            "Do you wish to remove all the records from the database? \nTHIS CANNOT BE REVERSED!!!")
        hleyout = QHBoxLayout()
        confirm_btn = QPushButton("Confirm")
        cancel_btn = QPushButton("Cancel")
        hleyout.addWidget(confirm_btn)
        hleyout.addWidget(cancel_btn)

        layout.addWidget(text)
        layout.addLayout(hleyout)

        self.setLayout(layout)

        confirm_btn.clicked.connect(self.confirmClickedEvent)
        cancel_btn.clicked.connect(self.cancelClickedEvent)

        QApplication.beep()

    def confirmClickedEvent(self):
        DBclear()
        self.close()

    def cancelClickedEvent(self):
        self.close()


class ListingTile(QWidget):
    def __init__(self, price, title, link):
        super().__init__()
        layout = QHBoxLayout()

        # Style them based on your sketch
        self.price_label = QLabel(f"<b>{price}</b>")
        self.title_label = QLabel(title)
        self.link_btn = QPushButton("Link")

        layout.addWidget(self.price_label)
        layout.addWidget(self.title_label)
        layout.addStretch()  # Pushes the link button to the right
        layout.addWidget(self.link_btn)
        self.link = link
        self.link_btn.clicked.connect(self.open_link)

        self.setLayout(layout)

    def open_link(self):
        if self.link:
            webbrowser.open(self.link)


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


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
