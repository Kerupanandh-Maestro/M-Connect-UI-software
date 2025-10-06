import sys
import time
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QComboBox, QCompleter, QVBoxLayout,QHBoxLayout,QFormLayout,QMessageBox, QPushButton, QStackedWidget, QGraphicsDropShadowEffect, QSizePolicy, QLabel, QDialog, QLineEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QPixmap, QFont
import requests

app = QApplication(sys.argv)
main_window = QMainWindow()
main_window.setWindowTitle("M-Connect")
main_window.setMinimumSize(720, 1280) 
stack = QStackedWidget()
main_window.setCentralWidget(stack)

# Worker thread
class Worker(QThread):
    signal = pyqtSignal(dict)
    def run(self):
        pins = [1,2,3,4,5,6,7]
        states = {p:0 for p in pins}
        while True:
            for p in pins:
                new_state = random.choice([0,1])
                if new_state!=states[p]:
                    states[p]=new_state
            self.signal.emit(states)
            time.sleep(30)

# Button Shadow
def btn_shadow(btn):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(30)
    shadow.setXOffset(4)
    shadow.setYOffset(4)
    shadow.setColor(QColor(0,0,0,160))
    btn.setGraphicsEffect(shadow)

# Arrow Navigation 
class ClickableIcon(QLabel):
    def __init__(self, path, index):
        super().__init__()
        self.index = index 
        pixmap = QPixmap(path)
        self.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
        self.setStyleSheet("cursor: pointer;")

    def mousePressEvent(self, event):
        stack.setCurrentIndex(self.index)  

employee = []
# machine_details
token = "rIS8Ls675h7ksIV3YNjTEIDCqDOGjw"
url = "https://mconnect.themaestro.in/client_mconnect/masters/list_machine_work?page=1&size=10"

payload = {
    "token": token,
    "machineName": "",       
    "machineGroupId": 230,
    "machine_id": 0
}

try:
    res = requests.post(url, data=payload, headers={"accept": "application/json"}, timeout=5)
    if res.status_code == 200:
        result = res.json()
        for machine in result.get("data", {}).get("items", []):
            if machine.get("employeeName"):
                employee.append((machine.get("employeeCode"), machine.get("employeeName")))
        # Sort by employee name
        employee.sort(key=lambda x: x[1].lower())
        print(employee)
    else:
        print("Failed to fetch machines. Status code:", res.status_code, res.text)
except Exception as e:
    print("Error loading machines:", e)


def check_in():
    dialog = CheckInDialog(employee)
    if dialog.exec():
        emp = dialog.get_selected_employee()
        if emp:
            print("Employee checked in: ", emp)
            stack.setCurrentWidget(option)
            check_in_btn.hide()
            check_out_btn.show()
            forward_btn.show()


# Check IN DialogBox
class CheckInDialog(QDialog):
    def __init__(self, employees):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setMinimumSize(600, 500)
        self.setStyleSheet("background-color: #1E1E1E; border-radius: 15px;")


        layout = QVBoxLayout()
        layout.setSpacing(50)
        label = QLabel("Select Employee:")
        label.setStyleSheet("font-size: 28px; color: white;")
        layout.addWidget(label)
        # ComboBox with search enabled
        self.combo = QComboBox()
        self.combo.setEditable(True)  # makes it a search box
        self.combo.setFont(QFont("Arial", 25))
        self.combo.setStyleSheet("""
            QComboBox {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 2px solid #1E88E5;
                border-radius: 10px;
                padding: 10px;
                font-size: 25px;
            }
            QComboBox QAbstractItemView {
                background-color: #3c3f41;
                color: #ffffff;
                selection-background-color: #1E88E5;
                selection-color: white;
            }
        """)


        layout.addWidget(self.combo)
        layout.addSpacing(300)

        self.combo.addItem(None, None)
        # Add employees to combo box
        for code, name in employees:
            self.combo.addItem(name, code)

        # Add completer for search filter
        model = self.combo.model()
        completer = QCompleter(model, self.combo)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.combo.setCompleter(completer)

        # Buttons
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        for btn in [ok_btn, cancel_btn]:
            btn.setFont(QFont("Arial", 20, QFont.Weight.Bold))
            btn.setMinimumSize(200, 80)

        ok_btn.setStyleSheet("background-color: #1E88E5; color: white; border-radius: 15px;")
        cancel_btn.setStyleSheet("background-color: #F44336; color: white; border-radius: 15px;")

        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

    def get_selected_employee(self):
        idx = self.combo.currentIndex()
        if idx > 0:
            return {
                "id": self.combo.currentData(),
                "name": self.combo.currentText()
            }
        return None

def check_out():
    dialog = CheckOutDialog()
    if dialog.exec():
        prod_qty, rej_qty = dialog.get_values()
        print("Production Qty:", prod_qty)
        print("Rejected Qty:", rej_qty)
        check_out_btn.hide()
        forward_btn.hide()
        check_in_btn.show()

# Check OUT DialogBox
class CheckOutDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setMinimumSize(600, 500)

        layout = QVBoxLayout()
        layout.addSpacing(40)
        form_layout = QFormLayout()
        self.prod_input = QLineEdit()
        self.rej_input = QLineEdit()
        
        for line_edit in [self.prod_input, self.rej_input]:
            line_edit.setFont(QFont("Arial", 24))
            line_edit.setStyleSheet("""
                QLineEdit {
                    border: 3px solid #1E88E5;
                    border-radius: 15px;
                    padding: 10px;
                    background-color: white;
                }
                QLineEdit:focus {
                    border: 3px solid #1565C0;
                }
            """)
        form_layout.setSpacing(40)
        prod_label = QLabel("Production Quantity :")
        prod_label.setStyleSheet("font-size: 30px; color: white")
        form_layout.addRow(prod_label, self.prod_input)

        rej_label = QLabel("Rejected Quantity :")
        rej_label.setStyleSheet("font-size: 30px; color: white")
        form_layout.addRow(rej_label, self.rej_input)

        layout.addLayout(form_layout)
        layout.addSpacing(60)
        
        # Buttons
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        for btn in [ok_btn, cancel_btn]:
            btn.setFont(QFont("Arial", 25, QFont.Weight.Bold))
            btn.setMinimumSize(80, 80)
            btn.setStyleSheet("""
                QPushButton {
                    color: white;
                    border-radius: 40px;
                }
            """)

        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E88E5;
                border-radius: 30px;
                color: white;
            }
            QPushButton:hover { background-color: #1565C0; }
            QPushButton:pressed { background-color: #0D47A1; }
        """)

        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                border-radius: 30px;
                color: white;
            }
            QPushButton:hover { background-color: #D32F2F; }
            QPushButton:pressed { background-color: #B71C1C; }
        """)

        ok_btn.clicked.connect(self.validate_inputs)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout = QVBoxLayout()
        btn_layout.addWidget(ok_btn)
        btn_layout.addSpacing(40)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        layout.addSpacing(40)
        
        self.setLayout(layout)
        self.result_values = None

        # Shadow for dialog
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 150))
        self.setGraphicsEffect(shadow)

    def validate_inputs(self):
        prod = self.prod_input.text().strip()
        rej = self.rej_input.text().strip()
        if not prod or not rej:
            show_warning(main_window, "Missing Input, Both fields are required!")
            return
        if not prod.isdigit() or not rej.isdigit():
            show_warning(main_window, "Invalid Input, Enter numeric values only!")
            return
        self.result_values = (int(prod), int(rej))
        self.accept()

    def get_values(self):
        return self.result_values

# warning box
def show_warning(parent, message):
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle("Warning")
    msg_box.setText(message)
    msg_box.setStyleSheet("""
        QMessageBox {
            background-color: lightgray;
            color: white;
            font-size: 28px;
            font-weight: bold;
        }
        QPushButton {
            background-color: #1E88E5;
            color: white;
            font-size: 25px;
            padding: 30px 60px;
            border-radius: 15px;
        }
        QPushButton:hover {
            background-color: #1565C0;
        }
        QPushButton:pressed {
            background-color: #0D47A1;
        }
    """)

    msg_box.exec()


home = QWidget()
home_layout = QVBoxLayout()
home_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
check_in_btn = QPushButton("Check In")
check_in_btn.setMinimumSize(500,500)
check_in_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
check_in_btn.setStyleSheet("""
    QPushButton {
        background-color: #1E88E5;
        color: white;
        font-size: 50px;
        font-weight: bold;
        border-radius: 250px;
        border: 2px solid #9C2700;

    }
    QPushButton:hover { background-color: #1565C0; }
    QPushButton:pressed { background-color: #0D47A1; }
""")
btn_shadow(check_in_btn)

check_out_btn = QPushButton("Check Out")
check_out_btn.setMinimumSize(500,500)
check_out_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
check_out_btn.setStyleSheet("""
    QPushButton {
        background-color: #F44336;  
        color: white;               
        font-size: 50px;
        font-weight: bold;
        border-radius: 250px;     
        border: 2px solid #0B3D91;
    }
    QPushButton:hover {
        background-color: #D32F2F;  
    }
    QPushButton:pressed {
        background-color: #B71C1C; 
    }
""")
btn_shadow(check_out_btn)
check_out_btn.hide()

forward_btn = ClickableIcon("/home/maestro/m-connect/frontward.png", 1)
forward_btn.hide()
home_layout.addSpacing(340)
home_layout.addWidget(check_in_btn, alignment=Qt.AlignmentFlag.AlignCenter)
home_layout.addWidget(check_out_btn, alignment=Qt.AlignmentFlag.AlignCenter)
home_layout.addSpacing(340)
nav_layout = QHBoxLayout()
nav_layout.addWidget(forward_btn, alignment=Qt.AlignmentFlag.AlignRight)
home_layout.addLayout(nav_layout)
home_layout.addSpacing(50)
home.setLayout(home_layout)
check_in_btn.clicked.connect (lambda: check_in())
check_out_btn.clicked.connect(lambda: check_out())

option = QWidget() 
option_layout = QVBoxLayout()
option_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
workorder_btn = QPushButton("Work Order")
workorder_btn.setMinimumSize(600,300)
workorder_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
workorder_btn.setStyleSheet("""
QPushButton {
    background-color: #FF9800;   /* Amber orange */
    color: white;
    font-size: 60px;
    font-weight: bold;
    border-radius: 85px;
    padding: 20px 40px;
    border: 3px solid #E65100;
}
QPushButton:hover { background-color: #FB8C00; }
QPushButton:pressed { background-color: #EF6C00; }
""")
btn_shadow(workorder_btn)

downtime_btn = QPushButton("Down Time")
downtime_btn.setMinimumSize(600,300)
downtime_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
downtime_btn.setStyleSheet("""
QPushButton {
    background-color: #009688;   /* Teal green */
    color: white;
    font-size: 60px;
    font-weight: bold;
    border-radius: 85px;
    padding: 20px 40px;
    border: 3px solid #004D40;
}
QPushButton:hover { background-color: #00897B; }
QPushButton:pressed { background-color: #00695C; }
""")
btn_shadow(downtime_btn)

back_btn = ClickableIcon("/home/maestro/m-connect/backward.png", 0)

option_layout.addSpacing(200)
option_layout.addWidget(workorder_btn, alignment=Qt.AlignmentFlag.AlignCenter)
option_layout.addSpacing(200)
option_layout.addWidget(downtime_btn, alignment=Qt.AlignmentFlag.AlignCenter)
option_layout.addSpacing(400)
option_layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignLeft)
option_layout.addSpacing(50)
option.setLayout(option_layout)
workorder_btn.clicked.connect(lambda: stack.setCurrentWidget(setting))
downtime_btn.clicked.connect(lambda: stack.setCurrentWidget(setting))

setting = QWidget()
setting_layout = QVBoxLayout()
setting.setLayout(setting_layout)

stack.addWidget(home)
stack.addWidget(option)
stack.addWidget(setting)

worker = Worker()
worker.signal.connect(lambda states:print(states))
worker.start()

main_window.show()
sys.exit(app.exec())