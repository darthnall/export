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

'''
def touch(logpath):
    with open(logpath, 'w'):
        os.utime(logpath, None)


current_datetime = datetime.datetime.now()
logpath = f"logs/{current_datetime}.log"
touch(logpath)

logging.basicConfig(level=logging.DEBUG,
                    filename=logpath,
                    format='%(asctime)s :: %(levelname)s :: %(message)s'
                    )
version_number = get_version()
logging.info('--- Application boot ---\n\nMOTD: \n-----\n"Welcome to ShowBox Exhibits POS System"\n-----\n')
logging.info(f'Version number {version_number} loaded')
'''

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

        # Pull image
        self.pixmap = QtGui.QPixmap('assets/main-screen/main-screen.png')
        self.setAutoFillBackground(True)

    def resizeEvent(self, event):
        # Resize background when window is altered
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(self.pixmap)
        palette.setBrush(QtGui.QPalette.Background, brush)
        self.setPalette(palette)
    
class CheckOutWindow(QtWidgets.QDialog):
    windowClosed = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.price = 0.0
        self.payment = 0.0
        self.setGeometry(560, 140, 400, 400)
        self.setWindowTitle('Checkout Window')

        self.message = QtWidgets.QLabel("Thank you for shopping with us!", self)

        self.total_price = QtWidgets.QLabel(f"Total: ${self.price:.2f}", self)

        self.pay_button = QtWidgets.QPushButton("Pay", self)
        self.pay_button.clicked.connect(self.open_keypad)

        self.keypad = QtWidgets.QDialog(self)
        layout = QtWidgets.QGridLayout(self.keypad)

        self.input_display = QtWidgets.QLineEdit(self.keypad)
        layout.addWidget(self.input_display, 0, 0, 1, 4)  # place it at the top row
        keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '.', '0', 'Enter', 'Clear']
        positions = [(i, j) for i in range(1, 5) for j in range(3)] + [(5, 0, 1, 3), (6, 0, 1, 3)]
        for position, key in zip(positions, keys):
            if key == 'Clear':
                button = QtWidgets.QPushButton(key)
                button.clicked.connect(self.clear_payment)
            elif key == 'Enter':
                button = QtWidgets.QPushButton(key)
                button.clicked.connect(self.calculate_change)
            else:  # digit key
                button = QtWidgets.QPushButton(key)
                button.clicked.connect(self.digit_pressed)
                button.setFixedHeight(60)  # increase button size
                button.setFixedWidth(60)
                button.setStyleSheet("font-size: 20px")  # increase font size
            layout.addWidget(button, *position)

        self.keypad.setLayout(layout)
        self.keypad.hide()

        self.change_label = QtWidgets.QLabel("Change: $0.00", self)

        self.close_button = QtWidgets.QPushButton("Close", self)
        self.close_button.clicked.connect(self.close_checkout_window)
        
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.message)
        self.layout.addWidget(self.total_price)
        self.layout.addWidget(self.pay_button)
        self.layout.addWidget(self.change_label)
        self.layout.addWidget(self.close_button)
        self.setLayout(self.layout)
        
        self.hide()

    def open_checkout_window(self, price):
        self.price = price
        self.total_price.setText(f"Total: ${self.price:.2f}")
        self.show()

    def close_checkout_window(self):
        self.hide()
        self.windowClosed.emit()

    def open_keypad(self):
        self.parent().barcodeInput.setAlwaysFocus(False)
        self.keypad.exec_()

    def digit_pressed(self):
        button = self.sender()
        new_text = self.input_display.text() + button.text()
        self.input_display.setText(new_text)

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
        self.change_label.setText(f"Change: ${change:.2f}")
        self.keypad.hide()

    def clear_payment(self):
        self.payment = 0.0
        self.input_display.clear()

    def open_checkout_window(self, price):
        self.price = price
        self.total_price.setText(f"Total: ${self.price:.2f}")
        self.show()

    def close_checkout_window(self):
        self.hide()
        self.windowClosed.emit()

    def open_keypad(self):
        self.keypad.exec_()

    def digit_pressed(self):
        button = self.sender()
        if button.text() == '.' and '.' in self.input_display.text():
            return
        new_text = self.input_display.text() + button.text()
        try:
            self.payment = float(new_text)
        except ValueError:
            self.payment = 0.0

    def clear_payment(self):
        self.payment = 0.0
        self.input_display.clear()

    def calculate_change(self):
        if self.payment < self.price:
            QtWidgets.QMessageBox.warning(self, "Payment Error", "Insufficient payment.")
            return
        change = self.payment - self.price
        self.change_label.setText(f"Change: ${change:.2f}")
        self.keypad.hide()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, data):
        super().__init__()
        self.closeInt = 0
        self.scannedItems = []
        self.data = data
        self.itemData = []
        self.background = BackgroundImage(self)
        self.background.setGeometry(self.rect())
        '''
        self.scanIndicator = QtWidgets.QLabel(self)
        self.scanIndicator.setStyleSheet("""
        color: red;
        border-style: flat;
        border-width: 5px;
        font-size: 36px;
        """)
        self.scanIndicator.setGeometry(170, 720, 561, 50)
        self.scanIndicator.setText("Scanning.")
        self.scanIndicatorTimer = QtCore.QTimer()
        self.scanIndicatorTimer.timeout.connect(self.scanning_indicator)
        self.scanIndicatorTimer.start(1000)
        '''

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
        '''
        def scanning_indicator(self):
            text = self.scanIndicator.text()
            if text == 'Scanning...':
                self.scanIndicator.setText('Scanning.')
            else:
                self.scanIndicator.setText(text + '.')
        '''

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
        # Create button
        self.deleteLastButton = make_button(self, "deleteLast")
        self.clearAllButton   = make_button(self, "clearAll")
        self.checkOutButton   = make_button(self, "checkOut")
        self.closeButton      = make_button(self, "close")
        #self.secretMenuButton = make_button(self, "secretMenu")

        # Map button function
        self.deleteLastButton.clicked.connect(self.delete_last)
        self.clearAllButton.clicked.connect(self.clear_all)
        self.checkOutButton.clicked.connect(self.check_out)
        self.closeButton.clicked.connect(self.close_app)
        self.closeButton.setStyleSheet("background-color: transparent; border: none;")
        #self.secretMenuButton.clicked.connect(self.activate_secret_menu)

    def scan_item(self):
        # logging.debug(f'Recieved input: {self.barcodeInput.text()}')
        scannerInput = self.barcodeInput.text()
        barcode = ''.join(char for char in scannerInput if char.isdigit())
        # logging.debug(f'Input modified from {scannerInput} -> {barcode}')
        if barcode in self.data:
            item_name = self.data[barcode]['name']
            path = self.data[barcode]['image_path']
            price = self.data[barcode]['price']
            #logging.debug(f'Barcode scanned: {barcode} :: Item name: {item_name}')
            try:
                pixmap = QtGui.QPixmap(path)
                self.itemScannedImage.setPixmap(pixmap.scaled(700, 700, QtCore.Qt.KeepAspectRatio))
            except Exception:
                #logging.warning(f'Image could not be found for {barcode} :: {item_name}')
                pass
            self.itemScanned.setText(item_name.upper())
            self.itemScanned.setStyleSheet(style)
            itemData = [str(1), str(item_name).title(), str(price)]
            self.scannedItems.append(itemData)
            if self.item_exists(itemData):
                pass
            else:
                self.insert_row(itemData)
            # logging.info(f'Successful scan flow achieved: {barcode} :: {item_name}')
        else:
            # logging.warning(f'Unrecgonized barcode: "{barcode}"')
            print("Nice")
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
                new_price = QtGui.QStandardItem(str(round(float(old_price) + float(itemData[2]), 2)))
                self.set_font(new_price)
                self.itemTableModel.setItem(row, 0, new_qty)
                self.itemTableModel.setItem(row, 2, new_price)
                self.update_total()
                logging.debug(f"Changed table values according to {itemData}")
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
        logging.debug(f"Added to table: {itemData}")
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
                    new_price_val = round(float(old_price) - float(lastItemPrice), 2)
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
            logging.debug(f"Row {row} data: {row_data}")


def main(DEBUG_MODE_ENABLED=False):
    if DEBUG_MODE_ENABLED:
        app = QtWidgets.QApplication([])
        window = MainWindow(data)
        window.showFullScreen()
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
