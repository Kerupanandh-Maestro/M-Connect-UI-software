import time
import random
from PyQt6.QtWidgets import (QApplication, QGraphicsOpacityEffect,QGraphicsDropShadowEffect, QComboBox, QCompleter, QVBoxLayout,QHBoxLayout,QFormLayout,QMessageBox, QPushButton, QGraphicsDropShadowEffect, QSizePolicy, QLabel, QDialog, QLineEdit)
from PyQt6.QtGui import QColor, QPixmap, QFont
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, Qt, QThread, pyqtSignal, QTimer
import requests
from datetime import datetime
import os
from core import security 
from core.config import settings

#Globals
name = None
code = None
check_in = None

# Current directory
cur_directory = os.path.dirname(__file__)
print(cur_directory)

# Worker Thread
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

# Date Time
def date_time(date_time_label):
    current_date = datetime.now().strftime("%A %d-%m-%Y")
    current_time = datetime.now().strftime("%H : %M : %S")
    date_time_label.setText(f"{current_date}\n{current_time}") 
        
def handle_checkin(combo, window, stack, main, work_start_time, emp_name, emp_code):
    global name, code, check_in
    idx = combo.currentIndex()
    if idx <= 0:
        msg_box = QMessageBox(window)
        msg_box.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        msg_box.setText("\nSelect Employee to Check In\n")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

        # Dynamically size based on screen
        screen = QApplication.primaryScreen().geometry()
        screen_w, screen_h = screen.width(), screen.height()
        msg_box.resize(int(screen_w * 0.4), int(screen_h * 0.2))

        # Center on screen
        x = (screen_w - msg_box.width()) // 2
        y = (screen_h - msg_box.height()) // 2
        msg_box.move(x, y)

        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #1E1E1E;
                color: white;
                border: 3px solid red;
                border-radius: 15px;
                font-size: 30px;
                padding: 25px;
            }

            QLabel {
                color: white;
                font-size: 26px;
            }

            QPushButton {
                background-color: #00bcd4;
                color: white;
                font-size: 22px;
                font-weight: bold;
                border-radius: 10px;
                padding: 15px 45px;
                border: 2px solid #00bcd4;
            }

            QPushButton:hover {
                background-color: #0097a7;
            }

            QPushButton:pressed {
                background-color: #006064;
            }
        """)

        opacity_effect = QGraphicsOpacityEffect()
        msg_box.setGraphicsEffect(opacity_effect)

        fade_anim = QPropertyAnimation(opacity_effect, b"opacity")
        fade_anim.setDuration(250)
        fade_anim.setStartValue(0)
        fade_anim.setEndValue(1)
        fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        msg_box.setWindowOpacity(0)
        msg_box.show()
        msg_box.resize(
            int(msg_box.width() * 0.95),
            int(msg_box.height() * 0.95)
        )
        fade_anim.start()

        for step in range(1, 6):
            msg_box.resize(
            int(msg_box.width() * 1.02),
            int(msg_box.height() * 1.02)
        )
            msg_box.setWindowOpacity(step / 5)
            QApplication.processEvents()
            QThread.msleep(25)

        msg_box.exec()
        return

    name = combo.currentText().split(" [")[0]
    code = combo.currentData()
    workstart_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    work_start_time.setText(f"Check In : {workstart_time}")
    emp_name.setText(f"Employee : {name}")
    emp_code.setText(f"Employee Code : {code}")
    stack.setCurrentWidget(main)
    return

def handle_workorder(combo, window, work_order_activity):
    idx = combo.currentIndex()
    if idx <= 0:
        msg_box = QMessageBox(window)
        msg_box.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        msg_box.setText("\nWork Order Not Selected. Select Your Work Order\n")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

        # Dynamically size based on screen
        screen = QApplication.primaryScreen().geometry()
        screen_w, screen_h = screen.width(), screen.height()
        msg_box.resize(int(screen_w * 0.4), int(screen_h * 0.2))

        # Center on screen
        x = (screen_w - msg_box.width()) // 2
        y = (screen_h - msg_box.height()) // 2
        msg_box.move(x, y)

        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #1E1E1E;
                color: white;
                border: 3px solid red;
                border-radius: 15px;
                font-size: 30px;
                padding: 25px;
            }

            QLabel {
                color: white;
                font-size: 26px;
            }

            QPushButton {
                background-color: #00bcd4;
                color: white;
                font-size: 22px;
                font-weight: bold;
                border-radius: 10px;
                padding: 15px 45px;
                border: 2px solid #00bcd4;
            }

            QPushButton:hover {
                background-color: #0097a7;
            }

            QPushButton:pressed {
                background-color: #006064;
            }
        """)

        opacity_effect = QGraphicsOpacityEffect()
        msg_box.setGraphicsEffect(opacity_effect)

        fade_anim = QPropertyAnimation(opacity_effect, b"opacity")
        fade_anim.setDuration(250)
        fade_anim.setStartValue(0)
        fade_anim.setEndValue(1)
        fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        msg_box.setWindowOpacity(0)
        msg_box.show()
        msg_box.resize(
            int(msg_box.width() * 0.95),
            int(msg_box.height() * 0.95)
        )
        fade_anim.start()

        for step in range(1, 6):
            msg_box.resize(
            int(msg_box.width() * 1.02),
            int(msg_box.height() * 1.02)
        )
            msg_box.setWindowOpacity(step / 5)
            QApplication.processEvents()
            QThread.msleep(25)

        msg_box.exec()
        return
    else:
        work_order_activity = True
        return work_order_activity
#Update Employee
def update_emp(work_start_time,emp_name, emp_code, stack, main):
    work_start_time.setText(f"Check In : {machine['work_start_duration']}")
    emp_name.setText(f"Employee : {machine['EmployeeName']}")
    emp_code.setText(f"Employee Code : {machine['EmployeeCode']}")
    stack.setCurrentWidget(main)
    return
        
# CheckOut Navigation 
class ClickableIcon(QLabel):
    def __init__(self, pixmap_path, s1, s2, callback=None):
        super().__init__()
        self.callback = callback
        pixmap = QPixmap(pixmap_path)
        self.setPixmap(pixmap.scaled(s1, s2, Qt.AspectRatioMode.KeepAspectRatio))
        self.setCursor(Qt.CursorShape.PointingHandCursor) 

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.callback:
            self.callback()

machine = None
# machine_details
def get_machine():
    global machine
    device_code = settings.DEVICE_CODE
    auth_code = security.check_authcode(device_code)
    machine_url = "https://mconnect.themaestro.in/client_mconnect/masters/device-get-details"
    # url = "http://192.168.4.48:8001/masters/device-get-details"
    # print(auth_code)
    payload = {
        "authcode": auth_code,
        "device_code": device_code       
    }

    try:
        res = requests.post(machine_url, data=payload, headers={"accept": "application/json"}, timeout=5)
        print("machine res ", res)
        result = res.json()
        print("\nmachine result\n", result)
        if result['status'] == 1:
            machine = result.get("data", {})
            print("machine\n", machine)
            return machine
        else:
            print(f"Failed to fetch machine. Status code: {result['status']} Message: {result['msg']}")
            return {'error':result['msg']}
    except Exception as e:
        print("Error loading machine:", e)
        return {'error':e}
    
def check_machine(parent):
    machine = get_machine()
    while machine.get('error'):
        show_warning(parent, f"Error Loading Machine. {machine['error']}")
        machine = get_machine()
    return machine

def get_work_order():
    workorder_url = "https://mconnect.themaestro.in/client_mconnect/dropdown/workorder_dropdown_app"
    device_code = settings.DEVICE_CODE
    auth_code = security.check_authcode(device_code)
    print(auth_code, device_code)
    payload = {
        "auth_code": auth_code,
        "device_code": device_code       
    }
    try:
        res = requests.post(workorder_url, data=payload, headers={"accept": "application/json"}, timeout=5)
        print("workorder res", res)
        result = res.json()
        print("\nworkorder result\n", result)
        if result['status'] == 1:
            workorder = result.get("data", {}).get("items", [])
            print("workorder\n", workorder)
            return workorder
        else:
            print(f"Failed to fetch Work Order. Status code: {result['status']} Message: {result['msg']}")
            return None
    except Exception as e:
        print("Error loading workorder:", e)
        return None
    
def checkout_quantity_box(combo, stack, home, window):
    dialog = QuantityDialog(window)
    if dialog.exec():
        prod_qty, rej_qty = dialog.get_values()
        print("Production Qty:", prod_qty)
        print("Rejected Qty:", rej_qty)
        combo.setCurrentIndex(0)
        name = None
        code = None
        checkin_time = None
        stack.setCurrentWidget(home)

def workorder_quantity_box(window):
    dialog = QuantityDialog(window)
    if dialog.exec():
        prod_qty, rej_qty = dialog.get_values()
        print("Production Qty:", prod_qty)
        print("Rejected Qty:", rej_qty)

class QuantityDialog(QDialog):
    def __init__(self, window):
        super().__init__()
        # self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

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
        layout.addSpacing(25)
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

        ok_btn.clicked.connect(lambda:self.validate_inputs(window))
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

    def validate_inputs(self, window):
        prod = self.prod_input.text().strip()
        rej = self.rej_input.text().strip()
        if not prod or not rej:
            show_warning(window, "Missing Input, Both fields are required!")
            return
        if not prod.isdigit() or not rej.isdigit():
            show_warning(window, "Invalid Input, Enter numeric values only!")
            return
        self.result_values = (int(prod), int(rej))
        self.accept()

    def get_values(self):
        return self.result_values

# Warning DialogBox
def show_warning(parent, message):
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle("⚠ Warning")
    msg_box.setText(f"⚠️  {message}")
    msg_box.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
    msg_box.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
    msg_box.setIcon(QMessageBox.Icon.NoIcon)
    msg_box.setStandardButtons(QMessageBox.StandardButton.NoButton)

    ok_btn = msg_box.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
    ok_btn.setShortcut(Qt.Key.Key_unknown)

    # --- Blue color scheme ---
    msg_box.setStyleSheet("""
        QMessageBox {
            background-color: #1E1E2F;        /* dark navy background */
            border: 3px solid #2979FF;        /* bright blue border */
            border-radius: 20px;
            padding: 25px;
        }

        QLabel {
            color: #FFFFFF;
            font-size: 26px;
            font-weight: bold;
            padding: 10px;
            background: transparent;
        }

        QPushButton {
            background-color: #2979FF;
            color: white;
            font-size: 22px;
            font-weight: bold;
            border-radius: 10px;
            padding: 12px 40px;
            border: none;
            text-decoration: none;
        }

        QPushButton:hover {
            background-color: #448AFF;
        }

        QPushButton:pressed {
            background-color: #1565C0;
        }

        QPushButton:focus {
            outline: none;
            border: none;
            text-decoration: none;
        }
    """)

    # --- Blue Glow Shadow ---
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(50)
    shadow.setColor(QColor(68, 138, 255, 180))  # same hue as button hover
    shadow.setOffset(0, 0)
    msg_box.setGraphicsEffect(shadow)

    # --- Fade-in Animation ---
    opacity_effect = QGraphicsOpacityEffect()
    msg_box.setGraphicsEffect(opacity_effect)
    anim = QPropertyAnimation(opacity_effect, b"opacity")
    anim.setDuration(400)
    anim.setStartValue(0)
    anim.setEndValue(1)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    QTimer.singleShot(0, anim.start)

    # --- Center on parent ---
    if parent:
        geo = parent.geometry()
        msg_box.move(
            geo.center().x() - msg_box.width() // 2,
            geo.center().y() - msg_box.height() // 2
        )

    msg_box.exec()



def create_block(element1, element2 = None):
    layout = QHBoxLayout()
    name_label = QLabel(element1)
    code_label = QLabel(element2)
    code_label.setAlignment(Qt.AlignmentFlag.AlignRight| Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(name_label)
    layout.addWidget(code_label)
    return layout

def check_in(stack, main):
    dialog = CheckInDialog(machine)
    if dialog.exec():
        emp = dialog.get_selected_employee()
        if emp:
            print(f'Employee Name: {emp["name"]}, Employee Code: {emp["code"]}, CheckIN: {emp["check_in"]}')
            stack.setCurrentWidget(main)

# Check IN DialogBox
class CheckInDialog(QDialog):
    def __init__(self, machine):
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
        if machine['EmployeeName']:
            display_text = f"{machine['EmployeeName']} [{machine['EmployeeCode']}]"
            self.combo.addItem(display_text, machine["EmployeeCode"])

        self.checkin_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Completer for filtering by name or code
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
                "name": self.combo.currentText().split(" [")[0],
                "code": self.combo.currentData(), 
                "check_in": self.checkin_time
            }
        return None
    
def format_time(total_seconds):
    try:
        total_seconds = int(float(total_seconds))
    except (ValueError, TypeError):
        return "0h:0m"
    hours, remainder = divmod(total_seconds, 3600)
    minutes = remainder // 60

    formatted_time = f"{hours:02d}:{minutes:02d}"
    return(formatted_time)

def update_operation(workorder_btn, operation_combo, workorder_combo, operation_label):
    operation_label.hide()
    operation_combo.hide()
    selected_workorder_id = workorder_combo.currentData()
    operation_combo.blockSignals(True)
    operation_combo.clear()
    operation_combo.addItem(None, None)
    operation_combo.blockSignals(False)
    operations = get_operation(selected_workorder_id)
    if operations:
        for operation in operations:
            operation_label.show()
            operation_combo.show()
            display_text = f"{operation['name']}"
            operation_combo.addItem(display_text)
    operation_combo.currentIndexChanged.connect(lambda:on_operation_selected(operation_combo, workorder_btn))
def on_operation_selected(operation_combo, workorder_btn):
    if operation_combo.currentIndex()>0:
        workorder_btn.setEnabled(True)
        workorder_btn.setStyleSheet(button_style2(button_status=True))
    else:
        button_style2(button_status=False)
        workorder_btn.setStyleSheet(button_style2(button_status=False))
    
def get_operation(workorder_id):
    operation_url = "https://mconnect.themaestro.in/client_mconnect/dropdown/dropdown-operation-machine-mapping"
    device_code = settings.DEVICE_CODE
    auth_code = security.check_authcode(device_code)
    print(auth_code, device_code, workorder_id, machine['machineId'])
    payload = {
        "auth_code": auth_code,
        "device_code": device_code,
        "work_order_id": workorder_id,
        "machine_id": machine['machineId']      
    }
    try:
        res = requests.post(operation_url, data=payload, headers={"accept": "application/json"}, timeout=5)
        print("operation res", res)
        result = res.json()
        print("\noperation result\n", result)
        if result['status'] == 1:
            operation = result.get("data", {})
            print("operation\n", operation)
            return operation
        else:
            print(f"Failed to fetch operation. Status code: {result['status']} Message: {result['msg']}")
            return None
    except Exception as e:
        print("Error loading operation:", e)
        return None
    
def button_style2(button_status):
    if not button_status:
        return """
        QPushButton {
            background-color: #3A3A50;
            color: gray;
            font-size: 40px;
            font-weight: bold;
            border-radius: 50px;
            padding: 12px 40px;
        }
        """
    else:
        return """
        QPushButton {
            background-color: #2979FF;
            color: white;
            font-size: 40px;
            font-weight: bold;
            border-radius: 50px;
            padding: 12px 40px;
        }
        QPushButton:hover {
            background-color: #448AFF;
        }
        QPushButton:pressed {
            background-color: #1565C0;
        }
        """