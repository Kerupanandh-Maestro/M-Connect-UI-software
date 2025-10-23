import time
import random
from PyQt6.QtWidgets import (QApplication, QGraphicsOpacityEffect, QGraphicsDropShadowEffect, QFrame, QComboBox, QCompleter, QVBoxLayout,QHBoxLayout,QFormLayout,QMessageBox, QPushButton, QGraphicsDropShadowEffect, QSizePolicy, QLabel, QDialog, QLineEdit)
from PyQt6.QtGui import QColor, QPixmap, QFont
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, Qt, QThread, pyqtSignal, QTimer
import requests
from datetime import datetime
import os
from core import security 
from core.config import settings

#Globals
# machine = {}
workorder_id = None
operation_id = None

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

#Employee checkIn Handeling
def handle_checkin(machine, stack, main, emp_combo, window):     
    idx = emp_combo.currentIndex()
    if idx <= 0:
        show_warning(window, "\n⚠️  Select Employee to Check In")
        return
    employee_code = emp_combo.currentData()
    check_in(employee_code, machine['machineId'])
    stack.setCurrentWidget(main)
    return

def check_in(employee_code, machine_id):
    CheckIn = "https://mconnect.themaestro.in/client_mconnect/employee_action/employeeCheckin_checkout"
    device_code = settings.DEVICE_CODE
    auth_code = security.check_authcode(device_code)
    print(auth_code, device_code)
    payload = {
        "auth_code": auth_code,
        "device_code": device_code,
        "machine_id": machine_id,
        "employee_code": employee_code,
        "actionStatus": 1,
        }
    try:
        res = requests.post(CheckIn, data=payload, headers={"accept": "application/json"}, timeout=5)
        result = res.json()
        print("\nCheckIn result\n", result)
        if result['status'] == 1:
            print("\nCheckIn Successfull\n")
        else:
            print(f"\nFailed to CheckIn. Status code: {result['status']} Message: {result['msg']}\n")
    except Exception as e:
        print("\nError Checking In: ", e)   

def select_workorder(machine, default_widget, work_order_widget):
    work_order_widget.hide()
    default_widget.show()
    workorder = "https://mconnect.themaestro.in/client_mconnect/employee_action/workorder_entry_multi"
    device_code = settings.DEVICE_CODE
    auth_code = security.check_authcode(device_code)
    print(auth_code, device_code)
    payload = {
        "auth_code": auth_code,
        "device_code": device_code, 
        "machine_id": machine['machineId'],
        "workId": workorder_id,
        "empId": machine['EmployeeId'],
        "action_status": 1,  
        "operation_id": operation_id,
    }
    try:
        res = requests.post(workorder, data=payload, headers={"accept": "application/json"}, timeout=5)
        result = res.json()
        print("\nWorkorder result\n", result)
        if result['status'] == 1:
            workorder = result.get("data", {})
            print("\nWorkOrder Selected Successfully\n")
            work_order_widget.hide()
            default_widget.show()
        else:
            print(f"\nFailed to select workorder. Status code: {result['status']} Message: {result['msg']}\n")
    except Exception as e:
        print("\nError Selecting WorkOrder :", e)
        
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

# machine_details
def get_machine():
    device_code = settings.DEVICE_CODE
    auth_code = security.check_authcode(device_code)
    machine_url = "https://mconnect.themaestro.in/client_mconnect/masters/device-get-details"
    # url = "http://192.168.4.48:8001/masters/device-get-details"
    payload = {
        "authcode": auth_code,
        "device_code": device_code       
    }

    try:
        res = requests.post(machine_url, data=payload, headers={"accept": "application/json"}, timeout=5)
        result = res.json()
        print("\nmachine result\n", result)
        if result['status'] == 1:
            mac = result.get("data", {})
            print("machine data\n", mac)
            return mac
        else:
            print(f"Failed to fetch machine. Status code: {result['status']} Message: {result['msg']}")
            return {'error':result['msg']}
    except Exception as e:
        print("Error loading machine:", e)
        return {'error':e}
    
def check_machine(parent):
    mac = get_machine()
    while mac.get('error'):
        show_warning(parent, f"\n⚠️  Error Loading Machine. {mac['error']}\n\n")
        mac = get_machine()
    return mac

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
    
def checkout_quantity_box(machine, combo, stack, home, window ):
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

        checkout = "https://mconnect.themaestro.in/client_mconnect/employee_action/employeeCheckin_checkout"
        device_code = settings.DEVICE_CODE
        auth_code = security.check_authcode(device_code)
        print(auth_code, device_code)
        payload = {
            "auth_code": auth_code,
            "device_code": device_code,
            "machine_id": machine['machineId'],
            "employee_code": machine['EmployeeCode'],
            "actionStatus": 2,
            "rejected_qty": rej_qty,
            "production_qty": prod_qty
            }
        print(payload)
        try:
            res = requests.post(checkout, data=payload, headers={"accept": "application/json"}, timeout=5)
            result = res.json()
            print("\nCheckout result\n", result)
            if result['status'] == 1:
                print("Checkout Successfull")
            else:
                print(f"Failed to CheckOut. Status code: {result['status']} Message: {result['msg']}")
        except Exception as e:
            print("Error in Checking Out:", e)

def workorder_quantity_box(machine, window, default_widget, work_order_widget):
    dialog = QuantityDialog(window)
    if dialog.exec():
        prod_qty, rej_qty = dialog.get_values()
        print("Production Qty:", prod_qty)
        print("Rejected Qty:", rej_qty)
        default_widget.hide()
        work_order_widget.show()
        workorder = "https://mconnect.themaestro.in/client_mconnect/employee_action/workorder_entry_multi"
        device_code = settings.DEVICE_CODE
        auth_code = security.check_authcode(device_code)
        print(auth_code, device_code)
        payload = {
            "auth_code": auth_code,
            "device_code": device_code, 
            "machine_id": machine['machineId'],
            "workId": machine['workId'],
            "empId": machine['EmployeeId'],
            "action_status": 2,  
            "qty": machine['totalQuantity'],
            "operation_id": machine['operation_id'],
            "qty_completed": prod_qty,
            "rejected_qty": rej_qty,
            "close_state": 1
        }
        try:
            res = requests.post(workorder, data=payload, headers={"accept": "application/json"}, timeout=5)
            result = res.json()
            print("\nworkorder result\n", result)
            if result['status'] == 1:
                workorder = result.get("data", {}).get("items", [])
                print("\nWorkOrder Closed Successfully\n")
                default_widget.hide()
                work_order_widget.show()
            else:
                print(f"\nFailed to close workorder. Status code: {result['status']} Message: {result['msg']}\n")
        except Exception as e:
            print("\nError Closing WorkOrder :", e)
class QuantityDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # -------- Window Setup (Frameless) --------
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Dialog
        )
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setMinimumSize(500, 350)

        # -------- Main Frame with Shadow --------
        frame = QFrame()
        frame.setStyleSheet("background-color: #1e1e1e; border-radius: 15px;")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 0)
        frame.setGraphicsEffect(shadow)

        # -------- Layouts --------
        layout = QVBoxLayout()
        layout.setSpacing(20)
        frame_layout = QVBoxLayout()
        frame_layout.addLayout(layout)
        frame.setLayout(frame_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(frame)
        self.setLayout(main_layout)

        # -------- Form Inputs --------
        form_layout = QFormLayout()
        form_layout.setSpacing(30)

        self.prod_input = QLineEdit()
        self.rej_input = QLineEdit("0")

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
                    color: black;
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

        layout.addLayout(form_layout)

        # -------- Buttons --------
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(25)
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        for btn in [ok_btn, cancel_btn]:
            btn.setFont(QFont("Arial", 20))
            btn.setMinimumSize(150, 90)

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

        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.result_values = None

        # -------- Center over parent --------
        self.center_over_parent(parent)

    def center_over_parent(self, parent):
        if parent is not None:
            parent_rect = parent.frameGeometry()
            parent_center = parent_rect.center()
            self_rect = self.frameGeometry()
            self_rect.moveCenter(parent_center)
            self.move(self_rect.topLeft())
        else:
            # Center on screen if no parent
            screen = self.screen().availableGeometry()
            self.move(
                (screen.width() - self.width()) // 2,
                (screen.height() - self.height()) // 2
            )

    def validate_inputs(self):
        prod = self.prod_input.text().strip()
        rej = self.rej_input.text().strip()
        if not prod or not rej:
            show_warning(self.parentWidget(), f"\n⚠️  Missing Input. Both fields are required!\n")
            return
        if not prod.isdigit() or not rej.isdigit():
            show_warning(self.parentWidget(), f"\n⚠️  Invalid Input. Enter numeric values only!\n")
            return
        self.result_values = (int(prod), int(rej))
        self.accept()

    def get_values(self):
        return self.result_values

# Warning DialogBox
def show_warning(parent, message):
    msg_box = QMessageBox(parent)
    msg_box.setText(message)
    msg_box.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
    msg_box.setFont(QFont("Segoe UI", 20))
    msg_box.setIcon(QMessageBox.Icon.NoIcon)
    msg_box.setStandardButtons(QMessageBox.StandardButton.NoButton)
    msg_box.setMinimumSize(150, 150)

    # Add OK button
    ok_btn = msg_box.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
    ok_btn.setFont(QFont("Segoe UI", 30, QFont.Weight.Bold))
    ok_btn.setMinimumSize(300, 100)

    msg_box.setStyleSheet("""
        QMessageBox {
            background-color: #1E1E2F;
            border-radius: 25px;
            padding: 35px;
        }
        QLabel {
            color: #FFFFFF;
            font-size: 30px;   
            font-weight: bold;
            padding: 20px;
            background: transparent;
        }
        QPushButton {
            background-color: #2979FF;
            color: white;
            font-size: 35px;  
            font-weight: bold;
            border-radius: 15px;
            padding: 20px 60px;
            border: none;
        }
        QPushButton:hover { background-color: #448AFF; }
        QPushButton:pressed { background-color: #1565C0; }
    """)

    # Shadow effect
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(50)
    shadow.setColor(QColor(68, 138, 255, 180))
    shadow.setOffset(0, 0)
    msg_box.setGraphicsEffect(shadow)

    # Center the dialog over parent
    if parent:
        parent_rect = parent.frameGeometry()
        msg_box_rect = msg_box.frameGeometry()
        msg_box.move(
            parent_rect.center().x() - msg_box_rect.width() // 2,
            parent_rect.center().y() - msg_box_rect.height() // 2
        )
    else:
        screen = msg_box.screen().availableGeometry()
        msg_box.move(
            (screen.width() - msg_box.width()) // 2,
            (screen.height() - msg_box.height()) // 2
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

def update_operation(workorder_btn, operation_combo, workorder_combo, operation_label, machine_id):
    global workorder_id
    workorder_id = workorder_combo.currentData()
    operation_combo.blockSignals(True)
    operation_combo.clear()
    operation_combo.addItem(None, None)
    operation_combo.blockSignals(False)
    operations = get_operation(workorder_id, machine_id)
    if operations:
        for operation in operations:
            operation_label.show()
            operation_combo.show()
            display_text = f"{operation['name']}"
            operation_combo.addItem(display_text, operation['id'])
    operation_combo.currentIndexChanged.connect(lambda:on_operation_selected(operation_combo, workorder_btn))
def on_operation_selected(operation_combo, workorder_btn):
    global operation_id
    if operation_combo.currentIndex()>0:
        operation_id = operation_combo.currentData()
        workorder_btn.setEnabled(True)
        workorder_btn.setStyleSheet(button_style2(button_status=True))
    else:
        workorder_btn.setStyleSheet(button_style2(button_status=False))
    
def get_operation(workorder_id, machine_id):
    operation_url = "https://mconnect.themaestro.in/client_mconnect/dropdown/dropdown-operation-machine-mapping"
    device_code = settings.DEVICE_CODE
    auth_code = security.check_authcode(device_code)
    print(auth_code, device_code, workorder_id, machine_id)
    payload = {
        "auth_code": auth_code,
        "device_code": device_code,
        "work_order_id": workorder_id,
        "machine_id": machine_id     
    }
    try:
        res = requests.post(operation_url, data=payload, headers={"accept": "application/json"}, timeout=5)
        result = res.json()
        print("\nOperation result\n", result)
        if result['status'] == 1:
            operation = result.get("data", {})
            print("\nOperation\n", operation)
            return operation
        else:
            print(f"\nFailed to fetch operation. Status code: {result['status']} Message: {result['msg']}\n")
            return None
    except Exception as e:
        print("\nError loading operation:", e)
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
def get_employee_list():
    dropdown_employee = "https://mconnect.themaestro.in/client_mconnect/dropdown/dropDownEmployeeApp"
    device_code = settings.DEVICE_CODE
    auth_code = security.check_authcode(device_code)
    print(auth_code, device_code)
    payload = {
        "auth_code": auth_code,
        "device_code": device_code,   
    }
    try:
        res = requests.post(dropdown_employee, data=payload, headers={"accept": "application/json"}, timeout=5)
        print("dropdown_employee res", res)
        result = res.json()
        print("\ndropdown_employee result\n", result)
        if result['status'] == 1:
            dropdown_employee = result.get("data", {}).get("items", [])
            print("dropdown_employee\n", dropdown_employee)
            return dropdown_employee
        else:
            print(f"Failed to fetch dropdown_employee. Status code: {result['status']} Message: {result['msg']}")
            return None
    except Exception as e:
        print("Error loading dropdown_employee:", e)
        return None
