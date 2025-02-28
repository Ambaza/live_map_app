# layer_preview.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QDialogButtonBox

class LayerPreviewDialog(QDialog):
    def __init__(self, layer_data, layer_name):
        super().__init__()
        self.setWindowTitle(f"Preview - {layer_name}")
        layout = QVBoxLayout(self)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        # Display the layer data as text (e.g., GeoJSON string or summary)
        self.text_edit.setPlainText(layer_data)
        layout.addWidget(self.text_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
