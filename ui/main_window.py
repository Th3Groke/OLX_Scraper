from PyQt6.QtWidgets import (
    QComboBox, QLabel, QLineEdit, QListWidget, QListWidgetItem, QMainWindow, QPushButton, QHBoxLayout, QVBoxLayout, QWidget)

from PyQt6.QtCore import QTimer, Qt

from PyQt6.QtGui import QIntValidator

from database_handling import DBloadData, DBremoveData
from ui.components import ConfirmClearDialog, ListingTile
from ui.scrape_dialog import ScrapeDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OLX Scraper Dashboard")
        self.setMinimumSize(800, 600)

        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(300)
        self.search_timer.timeout.connect(self.filter_listings)

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
        self.search_bar.textChanged.connect(self.reset_search_timer)
        filter_btn.clicked.connect(self.filters_btn_clicked_event)
        filters_done_btn.clicked.connect(self.filters_done_btn_clicked_event)

    def reset_search_timer(self):
        self.search_timer.start()

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
