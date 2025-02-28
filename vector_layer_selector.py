# vector_layer_selector.py
import fiona  # For listing layers in a GeoPackage
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QListWidgetItem, QDialogButtonBox
from PyQt5.QtCore import Qt

class VectorLayerSelectorDialog(QDialog):
    def __init__(self, file_path):
        super().__init__()
        self.setWindowTitle("Select Layers from GeoPackage")
        self.selected_layers = []
        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        self.populate_layers(file_path)
        layout.addWidget(self.list_widget)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def populate_layers(self, file_path):
        try:
            layers = fiona.listlayers(file_path)
            for layer_name in layers:
                item = QListWidgetItem(layer_name)
                item.setCheckState(Qt.Unchecked)
                self.list_widget.addItem(item)
        except Exception as e:
            print(f"Error listing layers: {e}")

    def get_selected_layers(self):
        selected = []
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            if item.checkState() == Qt.Checked:
                selected.append(item.text())
        return selected
