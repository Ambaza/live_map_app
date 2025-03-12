# spss_viewer.py
import os  # For file path operations
import pyreadstat  # To read SPSS .sav files
from PyQt5.QtWidgets import (
    QDialog, QTabWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
)  # Import necessary PyQt5 widgets

class SPSSViewerDialog(QDialog):
    def __init__(self, file_path):
        super().__init__()
        self.setWindowTitle(f"SPSS Viewer - {os.path.basename(file_path)}")
        self.resize(800, 600)
        # Read SPSS file using pyreadstat
        self.dataframe, self.meta = pyreadstat.read_sav(file_path)
        
        # Create tab widget to hold Data View and Variable View
        self.tabs = QTabWidget()
        self.data_view_tab = QTableWidget()
        self.variable_view_tab = QTableWidget()
        
        # Populate the tabs
        self.populate_data_view()
        self.populate_variable_view()
        
        self.tabs.addTab(self.data_view_tab, "Data View")
        self.tabs.addTab(self.variable_view_tab, "Variable View")
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.tabs)
        
    def populate_data_view(self):
        # Set number of rows and columns based on dataframe
        df = self.dataframe
        self.data_view_tab.setRowCount(len(df))
        self.data_view_tab.setColumnCount(len(df.columns))
        self.data_view_tab.setHorizontalHeaderLabels(df.columns.tolist())
        # Fill table with data values
        for row in range(len(df)):
            for col in range(len(df.columns)):
                value = str(df.iat[row, col])
                self.data_view_tab.setItem(row, col, QTableWidgetItem(value))
        self.data_view_tab.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
    def populate_variable_view(self):
        meta = self.meta
        # Define headers for variable view: Name, Type, Width, Decimals, Label, Values, Measure
        headers = ["Name", "Type", "Width", "Decimals", "Label", "Values", "Measure"]
        self.variable_view_tab.setColumnCount(len(headers))
        self.variable_view_tab.setHorizontalHeaderLabels(headers)
        num_vars = len(meta.column_names)
        self.variable_view_tab.setRowCount(num_vars)
        for i, col_name in enumerate(meta.column_names):
            # Name
            self.variable_view_tab.setItem(i, 0, QTableWidgetItem(col_name))
            # Type
            var_type = meta.column_types.get(col_name, "") if hasattr(meta, 'column_types') else ""
            self.variable_view_tab.setItem(i, 1, QTableWidgetItem(str(var_type)))
            # Width
            width = meta.column_widths.get(col_name, "") if hasattr(meta, 'column_widths') else ""
            self.variable_view_tab.setItem(i, 2, QTableWidgetItem(str(width)))
            # Decimals
            decimals = meta.column_decimals.get(col_name, "") if hasattr(meta, 'column_decimals') else ""
            self.variable_view_tab.setItem(i, 3, QTableWidgetItem(str(decimals)))
            # Label
            label = meta.column_labels[i] if hasattr(meta, 'column_labels') and len(meta.column_labels) > i else ""
            self.variable_view_tab.setItem(i, 4, QTableWidgetItem(str(label)))
            # Values
            if hasattr(meta, 'variable_value_labels') and col_name in meta.variable_value_labels:
                vl_key = meta.variable_value_labels[col_name]
                values_dict = meta.value_labels.get(vl_key, {}) if hasattr(meta, 'value_labels') else {}
                values_str = ", ".join(f"{k}: {v}" for k, v in values_dict.items())
            else:
                values_str = ""
            self.variable_view_tab.setItem(i, 5, QTableWidgetItem(values_str))
            # Measure: if variable_measure is a dict, use col_name as key
            if hasattr(meta, 'variable_measure'):
                if isinstance(meta.variable_measure, dict):
                    measure = meta.variable_measure.get(col_name, "")
                else:
                    measure = meta.variable_measure[i] if len(meta.variable_measure) > i else ""
            else:
                measure = ""
            self.variable_view_tab.setItem(i, 6, QTableWidgetItem(str(measure)))
        self.variable_view_tab.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
