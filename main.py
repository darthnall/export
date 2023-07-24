#!/home/pos/showbox-pos/venv/bin/python3

import sys
import json
import logging
import os
import datetime
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QBrush
from libs.buttons.button import make_button
from version import get_version

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

with open("data.json", "r") as f:
    data = json.load(f)
    

style = """
                color: black;
                background-color: white;
                border-style: flat;
                border-color: white;
                border-width: 5px;
                font-size: 72px;
        """

class AlwaysFocusedLineEdit(QtWidgets.QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.always_focus = True

    def focusOutEvent(self, e):
        super().focusOutEvent(e)
        if self.always_focus:
            QtCore.QTimer.singleShot(0, self.setFocus)

    def setAlwaysFocus(self, always_focus):
        self.always_focus = always_focus

class BackgroundImage(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.pixmap = QtGui.QPixmap('assets/main-screen/main-screen.png')
        self.setAutoFillBackground(True)

    def resizeEvent(self, event):
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(self.pixmap)
        palette.setBrush(QtGui.QPalette.Background, brush)
        self.setPalette(palette)
    
class CheckOutWindow(QtWidgets.QDialog):
    windowClosed = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.price   = 0.0
        self.payment = 0.0
        self.font = QtGui.QFont()
        self.font.setPointSize(32)

        self.message = QtWidgets.QLabel("Select payment option", self)
        self.message.setFont(self.font)
        self.message.setStyleSheet("color: #000000;")
        self.message.setAlignment(QtCore.Qt.AlignCenter)

        #self.total_price = QtWidgets.QLabel(f"Your total: ${self.price:.2f}", self)
        #self.total_price.setStyleSheet("color: #000000;")
        #self.total_price.setFont(self.font)

        self.pay_button = QtWidgets.QPushButton("Cash", self)
        self.pay_button.setStyleSheet("background-color: #FCDF1C; color: #000000;")
        self.pay_button.setFont(self.font)
        self.pay_button.setFixedHeight(50)
        self.pay_button.setFixedWidth(350)

        self.keypad = QtWidgets.QDialog(self)

        inner_vbox   = QtWidgets.QVBoxLayout()
        self.thanks = QtWidgets.QLabel(f"Input cash amount")
        self.thanks.setAlignment(QtCore.Qt.AlignCenter)
        self.thanks.setFont(self.font)
        inner_vbox.addWidget(self.thanks)
        self.keypad_total = QtWidgets.QLabel(f"Amount due: ${self.price:.2f}", self)
        self.keypad_total.setAlignment(QtCore.Qt.AlignCenter)
        self.keypad_total.setFont(self.font)
        inner_vbox.addWidget(self.keypad_total)
        inner_grid   = QtWidgets.QGridLayout()
        layout       = QtWidgets.QVBoxLayout(self.keypad)
        
        self.input_display = QtWidgets.QLineEdit(self.keypad)
        self.input_display.setFont(self.font)
        inner_grid.addWidget(self.input_display, 0, 0, 1, 4)
        keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'C', '0', '$']
        positions = [(i, j) for i in range(1, 5) for j in range(3)]
        for position, key in zip(positions, keys):
            button = QtWidgets.QPushButton(key)
            button.setFixedHeight(90)
            button.setFixedWidth(90)
            font = QtGui.QFont()
            font.setPointSize(28)
            button.setFont(font)
            if key == 'C':
                button.clicked.connect(self.clear_payment)
                button.setStyleSheet("background-color: #FCDF1C; color: #000000;")
            elif key == '$':
                button.clicked.connect(self.calculate_change)
                button.setStyleSheet("background-color: #FCDF1C; color: #000000;")
            else:
                button.clicked.connect(self.digit_pressed)
                button.setStyleSheet("background-color: #FFFFFF; color: #000000;")
            inner_grid.addWidget(button, *position)

        layout.addLayout(inner_vbox)
        layout.addLayout(inner_grid)
        self.keypad.setLayout(layout)
        self.keypad.setStyleSheet("background-color: #52B648;")

        self.keypad.hide()

        self.change_label = QtWidgets.QLabel("Change: $0.00", self)
        self.change_label.setStyleSheet("color: #000000;")
        self.change_label.setFont(self.font)
        self.change_label.setAlignment(QtCore.Qt.AlignCenter)

        self.close_button = QtWidgets.QPushButton("Close", self)
        self.close_button.setStyleSheet("background-color: #FCDF1C; color: #000000;")
        self.close_button.clicked.connect(self.close_checkout_window)
        self.close_button.setFixedHeight(50)
        self.close_button.setFixedWidth(350)
        self.close_button.setFont(self.font)
        self.pay_button.clicked.connect(self.open_keypad)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.message)
        #self.layout.addWidget(self.total_price)
        self.layout.addWidget(self.pay_button)
        self.layout.addWidget(self.change_label)
        self.layout.addWidget(self.close_button)
        self.setLayout(self.layout)

        self.setStyleSheet("background-color: #52B648;")
        
        self.hide()

    def open_checkout_window(self, price):
        self.price = price
        #self.total_price.setText(f"Total: ${self.price:.2f}")
        self.message.setText("Select payment option")
        self.pay_button.setStyleSheet("background-color: #FCDF1C; color: #000000;")
        self.pay_button.setEnabled(True)
        self.close_button.setStyleSheet("background-color: #444654; color: #000000;")
        self.close_button.setEnabled(False)
        self.show()

    def close_checkout_window(self):
        self.hide()
        self.windowClosed.emit()

    def clear_payment(self):
        self.payment = 0.0
        self.input_display.clear()

    def open_keypad(self):
        print("pay_clicked event recieved in open_keypad method.")
        self.keypad_total.setText(f"Amount due: ${self.price:.2f}")
        self.change_label.setText(f"Change: $0.00")
        self.input_display.setText("")
        self.parent().barcodeInput.setAlwaysFocus(False)
        self.keypad.exec_()
        self.clear_payment

    def calculate_change(self):
        try:
            self.payment = float(self.input_display.text())
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Payment Error", "Invalid payment.")
            return
        if self.payment < self.price:
            QtWidgets.QMessageBox.warning(self, "Payment Error", "Invalid payment.")
            return
        change = self.payment - self.price
        self.message.setText("Thank you! Collect change")
        self.change_label.setText(f"Change: ${change:.2f}")
        self.pay_button.setEnabled(False)
        self.pay_button.setStyleSheet("background-color: #444654; color: #000000;")
        self.close_button.setEnabled(True)
        self.close_button.setStyleSheet("background-color: #FCDF1C; color: #000000;")
        self.keypad.hide()

    def digit_pressed(self):
        button = self.sender()
        new_text = self.input_display.text() + button.text()
        try:
            self.payment = float(new_text)
        except ValueError:
            self.payment = 0.0
        self.input_display.setText(new_text)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, data):
        super().__init__()
        self.closeInt = 0
        self.scannedItems = []
        self.data = data
        self.itemData = []
        self.background = BackgroundImage(self)
        self.background.setGeometry(self.rect())

        self.barcodeInput = AlwaysFocusedLineEdit(self)
        self.barcodeInput.setGeometry(10, 10, 200, 40)
        self.barcodeInput.returnPressed.connect(self.scan_item)
        self.barcodeInput.setGeometry(0, 0, 1, 1)

        self.itemScanned = QtWidgets.QLabel(self)
        self.itemScanned.setStyleSheet(style)
        self.itemScanned.setAlignment(Qt.AlignCenter)
        self.itemScanned.setGeometry(130, 810, 561, 141)

        self.itemScannedImage = QtWidgets.QLabel(self.background)
        self.itemScannedImage.setGeometry(60, 130, 561, 561)

        self.itemTable = QtWidgets.QTableView(self)
        self.itemTable.setGeometry(830, 130, 954, 461)
        self.itemTableModel = QtGui.QStandardItemModel(self)
        self.itemTable.setModel(self.itemTableModel)
        self.set_table_to_default()

        self.totalPrice = QtWidgets.QLabel(self)
        self.totalPrice.setStyleSheet(style)
        self.totalPrice.setAlignment(Qt.AlignCenter)
        self.totalPrice.setGeometry(1480, 610, 291, 80)
        self.totalPrice.setText("$0.00")

        self.checkOutWindow = CheckOutWindow(self)
        self.checkOutWindow.windowClosed.connect(self.clear_all)
        self.checkOutWindow.windowClosed.connect(self.enable_main_window)

        self.init_buttons()

        self.background.lower()
        self.setCentralWidget(self.background)

        self.setEnabled(True)
    def disable_main_window(self):
        self.setEnabled(False)

    def enable_main_window(self):
        self.setEnabled(True)
        self.barcodeInput.setAlwaysFocus(True)
        self.barcodeInput.clear()
        self.barcodeInput.setFocus()

    def set_table_to_default(self):
        self.itemTableModel.setHorizontalHeaderLabels(["Qty.", "Name", "Price"])
        self.itemTable.setColumnWidth(0, 50)
        self.itemTable.setColumnWidth(1, 671)
        self.itemTable.setColumnWidth(2, 200)
        self.itemTable.setStyleSheet("""
        background-color: white;
        selection-background-color: #999999;
        color: black;
        """)
        self.itemTable.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.itemTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

    def set_font(self, index):
        font = QtGui.QFont()
        font.setPointSize(28)
        index.setFont(font)

    def resizeEvent(self, event):
        self.background.setGeometry(self.rect())
        super().resizeEvent(event)

    def init_buttons(self):
        self.deleteLastButton = make_button(self, "deleteLast")
        self.clearAllButton   = make_button(self, "clearAll")
        self.checkOutButton   = make_button(self, "checkOut")
        self.closeButton      = make_button(self, "close")
        #self.secretMenuButton = make_button(self, "secretMenu")

        self.deleteLastButton.clicked.connect(self.delete_last)
        self.clearAllButton.clicked.connect(self.clear_all)
        self.checkOutButton.clicked.connect(self.check_out)
        self.closeButton.clicked.connect(self.close_app)
        self.closeButton.setStyleSheet("background-color: transparent; border: none;")
        #self.secretMenuButton.clicked.connect(self.activate_secret_menu)

    def scan_item(self):
        scannerInput = self.barcodeInput.text()
        print(f"Input :: {scannerInput}")
        barcode = ''.join(char for char in scannerInput if char.isdigit())
        if barcode in self.data:
            item_name = self.data[barcode]['name']
            path = self.data[barcode]['image_path']
            price = self.data[barcode]['price']
            try:
                pixmap = QtGui.QPixmap(path)
                self.itemScannedImage.setPixmap(pixmap.scaled(700, 700, QtCore.Qt.KeepAspectRatio))
            except Exception:
                pass
            self.itemScanned.setText(item_name.upper())
            self.itemScanned.setStyleSheet(style)
            itemData = [str(1), str(item_name).title(), str(price)]
            self.scannedItems.append(itemData)
            if self.item_exists(itemData):
                pass
            else:
                self.insert_row(itemData)
        else:
            self.barcodeInput.clear()
        self.barcodeInput.clear()

    def item_exists(self, itemData):
        for row in range(self.itemTableModel.rowCount()):
            index = self.itemTableModel.index(row, 1)
            if self.itemTableModel.data(index) == itemData[1]:
                old_qty_item = self.itemTableModel.item(row, column=0)
                old_price_item = self.itemTableModel.item(row, column=2)
                old_qty = old_qty_item.data(Qt.DisplayRole)
                old_price = old_price_item.data(Qt.DisplayRole)
                new_qty = QtGui.QStandardItem(str(int(old_qty) + 1))
                self.set_font(new_qty)
                new_price = QtGui.QStandardItem(f"{float(float(old_price) + float(itemData[2])):.2f}")
                self.set_font(new_price)
                self.itemTableModel.setItem(row, 0, new_qty)
                self.itemTableModel.setItem(row, 2, new_price)
                self.update_total()
                print(f"Changed table values according to {itemData}")
                return True
        return False

    def insert_row(self, itemData):
        self.log_table_state()
        row = self.itemTableModel.rowCount()
        self.itemTableModel.insertRow(row)
        for column, value in enumerate(itemData):
            item = QtGui.QStandardItem(str(value))
            item.setData(str(value), Qt.DisplayRole)
            self.set_font(item)
            self.itemTableModel.setItem(row, column, item)
        self.itemTable.verticalHeader().setDefaultSectionSize(30)
        self.update_total()
        print(f"Added to table: {itemData}")
        self.log_table_state()

    def update_total(self):
        total = 0
        for row in range(self.itemTableModel.rowCount()):
            price_index = self.itemTableModel.item(row, column=2)
            total += round(float(price_index.data(Qt.DisplayRole)), 2)
        self.totalPrice.setText(f"${total:.2f}")
        if int(total) == 0:
            self.itemScanned.clear()
            self.itemScannedImage.clear()

    def delete_last(self):
        if self.scannedItems:
            lastItem = self.scannedItems.pop()
            lastItemName = lastItem[1]
            lastItemPrice = lastItem[2]
            for row in range(self.itemTableModel.rowCount()):
                index = self.itemTableModel.index(row, 1)
                if self.itemTableModel.data(index) == lastItemName:
                    old_qty_item = self.itemTableModel.item(row, column=0)
                    old_price_item = self.itemTableModel.item(row, column=2)
                    old_qty = old_qty_item.data(Qt.DisplayRole)
                    old_price = old_price_item.data(Qt.DisplayRole)
                    new_qty_val = int(old_qty) - 1
                    new_price_val = f"{(float(old_price) - float(lastItemPrice)):.2f}"
                    if new_qty_val == 0:
                        self.itemTableModel.removeRow(row)
                    else:
                        new_qty = QtGui.QStandardItem(str(new_qty_val))
                        new_price = QtGui.QStandardItem(str(f"{new_price_val:.2f}"))
                        self.set_font(new_qty)
                        self.set_font(new_price)
                        self.itemTableModel.setItem(row, 0, new_qty)
                        self.itemTableModel.setItem(row, 2, new_price)
                    self.update_total()

    def clear_all(self):
        self.itemTableModel.clear()
        self.set_table_to_default()
        self.totalPrice.setText("$0.00")
        self.itemScanned.clear()
        self.itemScannedImage.clear()

    def check_out(self):
        total_price = float(self.totalPrice.text().replace('$', ''))
        self.checkOutWindow.open_checkout_window(total_price)
        self.clear_all()

    def close_app(self):
        if self.closeInt < 3:
            self.closeInt += 1
        else:
            sys.exit()

    def activate_secret_menu(self):
        pass

    def log_table_state(self):
        for row in range(self.itemTableModel.rowCount()):
            row_data = [self.itemTableModel.item(row, column).data(Qt.DisplayRole) for column in range(self.itemTableModel.columnCount())]
            print(f"Row {row} data: {row_data}")


def main(DEBUG_MODE_ENABLED=False):
    if DEBUG_MODE_ENABLED:
        app = QtWidgets.QApplication([])
        window = MainWindow(data)
        window.show()
    else:
        app = QtWidgets.QApplication([])
        app.setOverrideCursor(Qt.BlankCursor)
        window = MainWindow(data)
        window.showFullScreen()
        window.show()
    
    app.exec_()

if __name__ == '__main__':
    main(DEBUG_MODE_ENABLED=True)
