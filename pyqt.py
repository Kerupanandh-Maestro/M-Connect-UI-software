import sys
import time
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QComboBox, QCompleter,QFrame, QVBoxLayout,QHBoxLayout,QFormLayout,QMessageBox, QPushButton, QStackedWidget, QGraphicsDropShadowEffect, QSizePolicy, QLabel, QDialog, QLineEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QPixmap, QFont
import requests
from datetime import datetime

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
        machines = result.get("data", {}).get("items", [])
        # Sort by employee name
        machines.sort(key=lambda x: (x.get("employeeName") or "").lower())
        print(machines)
    else:
        print("Failed to fetch machines. Status code:", res.status_code, res.text)
except Exception as e:
    print("Error loading machines:", e)


def check_in():
    dialog = CheckInDialog(machines)
    if dialog.exec():
        emp = dialog.get_selected_employee()
        if emp:
            print(f'Employee Name: {emp["name"]}, Employee ID: {emp["id"]}, CheckIN: {emp["check_in"]}')
            stack.setCurrentWidget(main)
            check_in_btn.hide()
            check_out_btn.show()
            forward_btn.show()

# Check IN DialogBox
class CheckInDialog(QDialog):
    def __init__(self, machines):
        super().__init__()
        # self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setMinimumSize(600, 500)
        self.setStyleSheet("background-color: #1E1E1E; border-radius: 15px;")


        layout = QVBoxLayout()
        label = QLabel("Select Employee:")
        label.setStyleSheet("font-size: 28px; color: white;")
        layout.addSpacing(25)
        layout.addWidget(label)
        self.combo = QComboBox()      # ComboBox with search enabled
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

        layout.addSpacing(10)
        layout.addWidget(self.combo)
        layout.addStretch(1)
        self.combo.addItem(None, None)
        # Add employees to combo box
        for i in machines:
            if i['employeeName']:
                display_text = f"{i['employeeName']} [{i['employeeID']}]"
                self.combo.addItem(display_text, i["employeeID"])

        self.checkin_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Completer for filtering by name or id
        completer = QCompleter([self.combo.itemText(i) for i in range(self.combo.count())])
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.combo.setCompleter(completer)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(25)
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        for btn in [ok_btn, cancel_btn]:
            btn.setFont(QFont("Arial", 20, QFont.Weight.Bold))
            btn.setMinimumSize(200, 80)

        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E88E5;
                border-radius: 10px;
                color: white;
            }
            QPushButton:hover { background-color: #1565C0; }
            QPushButton:pressed { background-color: #0D47A1; }
        """)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                border-radius: 10px;
                color: white;
            }
            QPushButton:hover { background-color: #D32F2F; }
            QPushButton:pressed { background-color: #B71C1C; }
        """)

        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        layout.addSpacing(20)

        self.setLayout(layout)

        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

    def get_selected_employee(self):
        idx = self.combo.currentIndex()
        if idx > 0:
            return {
                "name": self.combo.currentText().split(" (")[0],
                "id": self.combo.currentData(), 
                "check_in": self.checkin_time
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

class CheckOutDialog(QDialog):
    def __init__(self):
        super().__init__()
        # self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setMinimumSize(600, 500)
        self.setStyleSheet("background-color: #1E1E1E; border-radius: 15px;")

        layout = QVBoxLayout()

        # Form layout for inputs
        form_layout = QFormLayout()
        form_layout.setSpacing(40)

        self.prod_input = QLineEdit()
        self.rej_input = QLineEdit()

        for line_edit in [self.prod_input, self.rej_input]:
            line_edit.setFixedHeight(60) 
            line_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            line_edit.setFont(QFont("Arial", 22))
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

        prod_label = QLabel("Production Quantity :")
        prod_label.setStyleSheet("font-size: 26px; color: white;")
        form_layout.addRow(prod_label, self.prod_input)

        rej_label = QLabel("Rejected Quantity :")
        rej_label.setStyleSheet("font-size: 26px; color: white;")
        form_layout.addRow(rej_label, self.rej_input)
        layout.addSpacing(25)
        layout.addLayout(form_layout)
        layout.addStretch(1)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(25)
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        for btn in [ok_btn, cancel_btn]:
            btn.setFont(QFont("Arial", 20, QFont.Weight.Bold))
            btn.setMinimumSize(200, 80)

        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E88E5;
                border-radius: 10px;
                color: white;
            }
            QPushButton:hover { background-color: #1565C0; }
            QPushButton:pressed { background-color: #0D47A1; }
        """)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                border-radius: 10px;
                color: white;
            }
            QPushButton:hover { background-color: #D32F2F; }
            QPushButton:pressed { background-color: #B71C1C; }
        """)

        ok_btn.clicked.connect(self.validate_inputs)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        layout.addSpacing(20)

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
home.setStyleSheet("""
    QWidget {
        background-color: #121212;
        color: #f0f0f0;
        font-family: 'Segoe UI', 'Arial';
    }
    QLabel {
        font-size: 20px;
        color: #f0f0f0;
    }
    QLabel#sectionTitle {
        font-size: 24px;
        font-weight: bold;
        color: #00bcd4;
    }
""")
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

forward_btn = ClickableIcon("/home/maestro/m-connect/back.png", 1)
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

main = QWidget()
main_layout = QVBoxLayout()

# ===================== GLOBAL STYLES =====================
main.setStyleSheet("""
    QWidget {
        background-color: #121212;
        color: #f0f0f0;
        font-family: 'Segoe UI', 'Arial';
    }
    QLabel {
        font-size: 20px;
        color: #f0f0f0;
    }
    QLabel#sectionTitle {
        font-size: 24px;
        font-weight: bold;
        color: #00bcd4;
    }
""")

# ===================== PROFILE LAYOUT =====================
main_layout.addSpacing(20)
profile_layout = QHBoxLayout()
profile_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

# Avatar
avatar_layout = QVBoxLayout()
avatar_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

avatar = QLabel()
pixmap = QPixmap("/home/maestro/m-connect/avatar.png").scaled(
    100, 100,
    Qt.AspectRatioMode.KeepAspectRatio,
    Qt.TransformationMode.SmoothTransformation
)
avatar.setPixmap(pixmap)
avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
avatar.setStyleSheet("""
    QLabel {
        border-radius: 50px;
        border: 3px solid #00bcd4;
        background-color: #00bcd4;
        padding: 5px;
    }
""")
avatar_layout.addWidget(avatar)
profile_layout.addLayout(avatar_layout)

# Employee info
emp_layout = QVBoxLayout()
emp_layout.setSpacing(20)
emp_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

checkin_label = QLabel(f"Check In: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
checkin_label.setStyleSheet("""
    font-size: 25px;
    font-weight: bold;
    color: white;
""")
checkin_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
emp_layout.addWidget(checkin_label)

emp_name = QLabel("Employee: Gopal")
emp_name.setStyleSheet("""
    font-size: 25px;
    font-weight: bold;
    color: white;
""")


emp_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
emp_layout.addWidget(emp_name)

emp_id = QLabel("Emp ID: 20eea14")
emp_id.setStyleSheet("""
    font-size: 25px;
    font-weight: bold;
    color: white;
""")
emp_id.setAlignment(Qt.AlignmentFlag.AlignCenter)
emp_layout.addWidget(emp_id)

profile_layout.addLayout(emp_layout)

# Checkout
back_layout = QVBoxLayout()
back_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
back_btn = ClickableIcon("/home/maestro/m-connect/checkout.png", 0)
back_btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
back_btn.setStyleSheet("""
    QLabel {
        background-color: #292929;
        border-radius: 15px;
        padding: 10px;
    }
    QLabel:hover {
        background-color: #00bcd4;
    }
""")
back_layout.addWidget(back_btn)

checkout_label = QLabel("Check Out")
checkout_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
checkout_label.setFont(QFont("Arial", 20))
checkout_label.setStyleSheet("color: #00bcd4; font-weight: bold;")
back_layout.addWidget(checkout_label)

profile_layout.addLayout(back_layout)
main_layout.addLayout(profile_layout)

# ===================== MACHINE DATA =====================
def create_block(element1, element2 = None):
    block = QFrame()
    block.setMinimumSize(250, 100)
    block.setStyleSheet("""
        QFrame {
            background-color: #1e1e1e;
            border-radius: 15px;
        }
        QLabel {
            font-size: 25px;
            font-weight: bold;
            color: white;
        }
    """)
    if element2:
        layout = QHBoxLayout()
        name_label = QLabel(element1)
        code_label = QLabel(element2)
        layout.addWidget(name_label)
        layout.addWidget(code_label)

    else:
        layout = QVBoxLayout()
        name_label = QLabel(element1)
        layout.addWidget(name_label)
    block.setLayout(layout)
    return block

# Create individual blocks
work_block = create_block("Work Name: Plumbing", "Work Code: W5484")
part_block = create_block("Part Name: Part", "Part Code: P5548")
work_type_block = create_block("Work Type: QcPoduction")
operation_block = create_block("Operation: Smoothing", "Operation Code: O5456")
quantity_block = create_block("Target Quantity: 9999", "Produced Quantity: 5452")

# Arrange blocks in a grid-like layout
layout = QVBoxLayout()
layout.addWidget(work_block)
layout.addWidget(part_block)
layout.addWidget(work_type_block)
layout.addWidget(operation_block)
layout.addWidget(quantity_block)

main_layout.addLayout(layout)

main.setLayout(main_layout)
stack.addWidget(home)
stack.addWidget(main)

worker = Worker()
worker.signal.connect(lambda states: print(states))
worker.start()

main_window.show()
sys.exit(app.exec())
