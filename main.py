import sys
import requests
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QComboBox, QPushButton, QDialog, QFormLayout, QLineEdit, QTextEdit)
from PySide6.QtCore import Qt

class CatDetailDialog(QDialog):
    def __init__(self, cat_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Подробная информация о коте")
        self.setModal(True)
        self.cat_data = cat_data
        self.is_editing = False
        
        layout = QFormLayout()
        self.name_edit = QLineEdit(cat_data.get('name', ''))
        self.origin_edit = QLineEdit(cat_data.get('origin', ''))
        self.temperament_edit = QTextEdit(cat_data.get('temperament', ''))
        self.description_edit = QTextEdit(cat_data.get('description', ''))
        
        layout.addRow("Название породы:", self.name_edit)
        layout.addRow("Происхождение:", self.origin_edit)
        layout.addRow("Темперамент:", self.temperament_edit)
        layout.addRow("Описание:", self.description_edit)
        
        self.edit_button = QPushButton("Редактировать")
        self.edit_button.clicked.connect(self.toggle_edit)
        layout.addWidget(self.edit_button)
        
        self.setLayout(layout)
        self.set_fields_readonly(True)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                font-family: Arial;
            }
            QLineEdit, QTextEdit {
                background-color: #3c3f41;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
                font-size: 14px;
                color: #ffffff;
            }
            QLineEdit:disabled, QTextEdit:disabled {
                background-color: #333;
                color: #aaaaaa;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLabel {
                font-size: 14px;
                color: #e0e0e0;
            }
        """)

    def toggle_edit(self):
        self.is_editing = not self.is_editing
        self.set_fields_readonly(not self.is_editing)
        self.edit_button.setText("Сохранить" if self.is_editing else "Редактировать")

    def set_fields_readonly(self, readonly):
        self.name_edit.setReadOnly(readonly)
        self.origin_edit.setReadOnly(readonly)
        self.temperament_edit.setReadOnly(readonly)
        self.description_edit.setReadOnly(readonly)

class CatApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cat Breeds")
        self.setGeometry(100, 100, 800, 600)
        
        self.cat_data = self.fetch_cat_data()
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        self.origin_filter = QComboBox()
        self.origin_filter.addItem("Все страны")
        origins = sorted(set(cat.get('origin', '') for cat in self.cat_data))
        self.origin_filter.addItems(origins)
        self.origin_filter.currentTextChanged.connect(self.filter_table)
        layout.addWidget(self.origin_filter)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Название", "Происхождение", "Темперамент"])
        self.table.doubleClicked.connect(self.show_details)
        layout.addWidget(self.table)
        
        self.delete_button = QPushButton("Удалить выбранную породу")
        self.delete_button.clicked.connect(self.delete_selected)
        layout.addWidget(self.delete_button)
        
        self.update_table()
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                font-family: Arial;
            }
            QComboBox {
                background-color: #3c3f41;
                border: 1px solid #555;
                padding: 5px;
                border-radius: 4px;
                font-size: 14px;
                color: #ffffff;
            }
            QComboBox:hover {
                border: 1px solid #777;
            }
            QComboBox::drop-down {
                border: none;
            }
            QTableWidget {
                background-color: #2b2b2b;
                border: 1px solid #444;
                border-radius: 4px;
                font-size: 13px;
                color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #404040;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #333;
                padding: 5px;
                border: 1px solid #444;
                font-size: 14px;
                color: #e0e0e0;
            }
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)

    def fetch_cat_data(self):
        response = requests.get("https://api.thecatapi.com/v1/breeds")
        return response.json()

    def update_table(self):
        self.table.setRowCount(0)
        current_origin = self.origin_filter.currentText()
        
        filtered_data = self.cat_data
        if current_origin != "Все страны":
            filtered_data = [cat for cat in self.cat_data 
                           if cat.get('origin', '') == current_origin]
            
        self.table.setRowCount(len(filtered_data))
        for row, cat in enumerate(filtered_data):
            self.table.setItem(row, 0, QTableWidgetItem(cat.get('name', '')))
            self.table.setItem(row, 1, QTableWidgetItem(cat.get('origin', '')))
            self.table.setItem(row, 2, QTableWidgetItem(cat.get('temperament', '')))
            self.table.item(row, 0).setData(Qt.UserRole, cat)
        self.table.resizeColumnsToContents()

    def filter_table(self):
        self.update_table()

    def show_details(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            cat_data = self.table.item(current_row, 0).data(Qt.UserRole)
            dialog = CatDetailDialog(cat_data, self)
            dialog.exec()

    def delete_selected(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            del self.cat_data[current_row]
            self.update_table()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet("QApplication { background-color: #1e1e1e; }")
    window = CatApp()
    window.show()
    sys.exit(app.exec())