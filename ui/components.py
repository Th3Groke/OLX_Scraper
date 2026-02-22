import webbrowser
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QPushButton)
from PyQt6.QtCore import Qt

from database_handling import DBclear


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


class ConfirmClearDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setWindowTitle("Confirm")
        self.setWindowFlag(Qt.WindowType.Tool)
        layout = QVBoxLayout()
        text = QLabel(
            "Do you wish to remove all the records from the database? \nTHIS CANNOT BE REVERSED!!!")
        hLayout = QHBoxLayout()
        confirm_btn = QPushButton("Confirm")
        cancel_btn = QPushButton("Cancel")
        hLayout.addWidget(confirm_btn)
        hLayout.addWidget(cancel_btn)

        layout.addWidget(text)
        layout.addLayout(hLayout)

        self.setLayout(layout)

        confirm_btn.clicked.connect(self.confirmClickedEvent)
        cancel_btn.clicked.connect(self.cancelClickedEvent)

        QApplication.beep()

    def confirmClickedEvent(self):
        DBclear()
        self.close()

    def cancelClickedEvent(self):
        self.close()
