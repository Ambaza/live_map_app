# icon_selector.py
import os  # For file and directory operations
from PyQt5.QtWidgets import QDialog, QListWidget, QVBoxLayout, QListWidgetItem, QPushButton, QHBoxLayout
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize

class IconSelectorDialog(QDialog):
    def __init__(self, icons_folder):
        super().__init__()
        self.setWindowTitle("Select an Icon")
        self.selected_icon_path = None
        self.icons_folder = icons_folder

        # Main layout for the dialog
        self.layout = QVBoxLayout(self)

        # List widget to display icons
        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(64, 64))
        self.populate_icons()
        self.layout.addWidget(self.list_widget)

        # Buttons layout
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(button_layout)

        # Connect selection signal
        self.list_widget.itemClicked.connect(self.icon_selected)

    def populate_icons(self):
        # Recursively search for .svg and .png files in the icons folder
        for root, dirs, files in os.walk(self.icons_folder):
            for file in files:
                if file.lower().endswith((".svg", ".png")):
                    full_path = os.path.join(root, file)
                    item = QListWidgetItem(QIcon(full_path), file)
                    item.setData(1000, full_path)  # Store file path in item data
                    self.list_widget.addItem(item)

    def icon_selected(self, item):
        # Store the selected icon path
        self.selected_icon_path = item.data(1000)

    def get_selected_icon(self):
        return self.selected_icon_path
