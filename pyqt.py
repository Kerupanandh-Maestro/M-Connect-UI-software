import sys
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget,QGraphicsDropShadowEffect, QComboBox, QCompleter,QFrame,QProgressBar, QVBoxLayout,QHBoxLayout, QPushButton, QStackedWidget, QGraphicsDropShadowEffect, QSizePolicy, QLabel)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPixmap, QFont
from utility import*
from core.config import settings

#__________GLOBALS__________
machine = {}
check_in_activity = False
work_order_activity = False
#__________APP__________
app = QApplication(sys.argv)
window = QMainWindow()
window.setWindowTitle("M-Connect")
window.setMinimumSize(800, 480) 
stack = QStackedWidget()
window.setCentralWidget(stack)

#__________1.HOME PAGE__________
home = QWidget()

def update_machine():
    global machine, check_in_activity, work_order_activity
    machine = check_machine(home)
    check_in_activity = True if machine['EmployeeId'] else False
    # check_in_activity = True
    # work_order_activity = True if machine['workId'] else False
    work_order_activity = True
update_machine()
machine_timer = QTimer()
machine_timer.timeout.connect(update_machine)
machine_timer.start(30000)

print("\nCHECKIN, WORKORDER, MACHINE ", check_in_activity, work_order_activity, machine)
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
# home_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
home_layout.setSpacing(0)
home_layout.setContentsMargins(50, 20, 50, 20)
date_time_label = QLabel()
date_time_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
date_time_label.setStyleSheet("font-size: 25px; color: white;")
datetime_timer = QTimer()
datetime_timer.timeout.connect(lambda:date_time(date_time_label))
datetime_timer.start(1000)
home_layout.addWidget(date_time_label)
home_layout.addSpacing(50)
mac_block = QFrame()
mac_block.setMinimumSize(100, 100)
mac_block.setStyleSheet("""
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
mac_layout = QVBoxLayout()
mac_layout.setSpacing(20)
        
machine_label = QLabel(f"Machine       :  {machine['machineName']}")
machine_code = QLabel(f"Machine Code  :  {machine['machineNumber']}")
device_code = QLabel(f"Device Code   :  {settings.DEVICE_CODE}")
mac_layout.addWidget(machine_label)
mac_layout.addWidget(machine_code)
mac_layout.addWidget(device_code)
mac_block.setLayout(mac_layout)
home_layout.addWidget(mac_block)
home_layout.addSpacing(50)
title = QLabel("Employee Check-In")
title.setAlignment(Qt.AlignmentFlag.AlignCenter)
title.setStyleSheet("font-size: 60px; color: white; font-weight: bold;")
home_layout.addWidget(title)
home_layout.addSpacing(75)

# --- Search Label ---
label = QLabel("Select Employee :")
label.setStyleSheet("font-size: 35px; color: white;")
home_layout.addWidget(label)
home_layout.addSpacing(10)

# --- Search Box ---
emp_combo = QComboBox()
emp_combo.setEditable(True)
emp_combo.setFont(QFont("Arial", 28))
arrow_path = f"{cur_directory}/asserts/down-arrow.png"
emp_combo.setStyleSheet(f"""
QComboBox {{
    background-color: #2b2b2b;
    color: #ffffff;
    border: 2px solid #1E88E5;
    border-radius: 12px;
    padding: 15px;
    font-size: 28px;
}}

QComboBox QAbstractItemView {{
    background-color: #3c3f41;
    color: #ffffff;
    selection-background-color: #1E88E5;
    selection-color: white;
}}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 75px;                     
    border-left: 2px solid #1E88E5;
    background-color: #1E88E5;
    border-top-right-radius: 12px;
    border-bottom-right-radius: 12px;
}}

QComboBox::down-arrow {{
    width: 50px;
    height: 50px;
    image: url({arrow_path});
}}

QComboBox::down-arrow:on {{
    top: 1px;
    left: 1px;
}}
""")

dropdown_employees = get_employee_list()
emp_combo.addItem(None, None)
for dropdown_employee in dropdown_employees:
        emp_combo.addItem(f"{dropdown_employee['employeeName']} [{dropdown_employee['employeeCode']}]", dropdown_employee["employeeCode"])

# Autocomplete
completer = QCompleter([emp_combo.itemText(i) for i in range(emp_combo.count())])
completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
completer.setFilterMode(Qt.MatchFlag.MatchContains)
emp_combo.setCompleter(completer)
home_layout.addWidget(emp_combo)
home_layout.addSpacing(50) 

# --- Check-In Button ---
checkin_btn = ClickableIcon(f"{cur_directory}/asserts/checkin.png", s1=250, s2=250, callback=lambda: [handle_checkin(machine, stack, main, emp_combo, window), update_machine()])
checkin_btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
checkin_label = QLabel("Check In")
checkin_label.setStyleSheet("font-size: 40px; color: #00bcd4; font-weight: bold; font-family: 'Segoe UI', 'Arial';")
checkin_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
home_layout.addWidget(checkin_btn)
home_layout.addSpacing(10)
home_layout.addWidget(checkin_label)
# home_layout.addSpacing(300)
home.setLayout(home_layout)

#__________2.MAIN PAGE__________
main = QWidget()
main_layout = QVBoxLayout()
main_layout.setSpacing(20)

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

profile_layout = QHBoxLayout()
profile_layout.setContentsMargins(20,20,20,0)
profile_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

# Avatar
avatar_layout = QVBoxLayout()
avatar_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

avatar = QLabel()
pixmap = QPixmap(f"{cur_directory}/asserts/user.png").scaled(
    125, 125,
    Qt.AspectRatioMode.KeepAspectRatio,
    Qt.TransformationMode.SmoothTransformation
)
avatar.setPixmap(pixmap)
avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
avatar_layout.addWidget(avatar)
profile_layout.addLayout(avatar_layout)

# Employee Info
emp_layout = QVBoxLayout()  
emp_layout.setSpacing(20)
emp_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

work_start_time = QLabel(f"Check In : {machine['work_start_duration']}")
work_start_time.setStyleSheet("""
    font-size: 25px;
    font-weight: bold;
    color: white;
""")
work_start_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
emp_layout.addWidget(work_start_time)

emp_name = QLabel(f"Employee : {machine['EmployeeName']}")
emp_name.setStyleSheet("""
    font-size: 25px;
    font-weight: bold;
    color: white;
""")
emp_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
emp_layout.addWidget(emp_name)

emp_code = QLabel(f"Employee Code : {machine['EmployeeCode']}")
emp_code.setStyleSheet("""
    font-size: 25px;
    font-weight: bold;
    color: white;
""")
emp_code.setAlignment(Qt.AlignmentFlag.AlignCenter)
emp_layout.addWidget(emp_code)

profile_layout.addLayout(emp_layout)

#Check Out
checkout_layout = QVBoxLayout()
checkout_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
checkout_btn = ClickableIcon(f"{cur_directory}/asserts/checkout.png", s1=100, s2=100, callback=lambda: [checkout_quantity_box(machine, emp_combo, stack, home, window), update_machine()])
checkout_btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
checkout_btn.setStyleSheet("""
    QLabel {
        background-color: #292929;
        border-radius: 15px; 
        padding: 10px;
    }
    QLabel:hover {
        background-color: #00bcd4;
    }
""")
checkout_layout.addWidget(checkout_btn)

checkout_label = QLabel("Check Out")
checkout_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
checkout_label.setStyleSheet("font-size: 20px; color: #00bcd4; font-weight: bold; font-family: 'Segoe UI', 'Arial';")
checkout_layout.addWidget(checkout_label)

profile_layout.addLayout(checkout_layout)
main_layout.addLayout(profile_layout)
# main_layout.addSpacing(25)
    
# MACHINE SECONDARY DATA
# Work Order Selection MAIN
workorders = get_work_order()
work_order_widget = QWidget()
work_order_layout = QVBoxLayout(work_order_widget)
work_order_layout.setSpacing(0)
# work_order_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
work_order_layout.addSpacing(55)
work_order_layout.setContentsMargins(50, 20, 50, 20)

# --- Work Order Search Label ---
workorder_label = QLabel("Work Order :")
workorder_label.setStyleSheet("font-size: 35px; color: white;")
work_order_layout.addWidget(workorder_label)
work_order_layout.addSpacing(10)

# --- Work Order Search Box ---
workorder_combo = QComboBox()
workorder_combo.setEditable(True)
workorder_combo.setFont(QFont("Arial", 28))
workorder_combo.setStyleSheet(f"""
QComboBox {{
    background-color: #2b2b2b;
    color: #ffffff;
    border: 2px solid #1E88E5;
    border-radius: 12px;
    padding: 15px;
    font-size: 28px;
}}

QComboBox QAbstractItemView {{
    background-color: #3c3f41;
    color: #ffffff;
    selection-background-color: #1E88E5;
    selection-color: white;
}}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 75px;                     
    border-left: 2px solid #1E88E5;
    background-color: #1E88E5;
    border-top-right-radius: 12px;
    border-bottom-right-radius: 12px;
}}

QComboBox::down-arrow {{
    width: 50px;
    height: 50px;
    image: url({arrow_path});
}}

QComboBox::down-arrow:on {{
    top: 1px;
    left: 1px;
}}
""")

workorder_combo.addItem(None, None)
for workorder in workorders:
    workorder_combo.addItem(f"{workorder['work_name']}", workorder["work_id"])

# Work Order Autocomplete
completer = QCompleter([workorder_combo.itemText(i) for i in range(workorder_combo.count())])
completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
completer.setFilterMode(Qt.MatchFlag.MatchContains)
workorder_combo.setCompleter(completer)
work_order_layout.addWidget(workorder_combo)
work_order_layout.addSpacing(50)

# --- Operation Search Label ---
operation_label = QLabel("Operation :")
operation_label.hide()
operation_label.setStyleSheet("font-size: 35px; color: white;")
work_order_layout.addWidget(operation_label)
work_order_layout.addSpacing(10)

# --- Operation Search Box ---
operation_combo = QComboBox()
operation_combo.hide()
operation_combo.setEditable(True)
operation_combo.setFont(QFont("Arial", 28))
operation_combo.setStyleSheet(f"""
QComboBox {{
    background-color: #2b2b2b;
    color: #ffffff;
    border: 2px solid #1E88E5;
    border-radius: 12px;
    padding: 15px;
    font-size: 28px;
}}

QComboBox QAbstractItemView {{
    background-color: #3c3f41;
    color: #ffffff;
    selection-background-color: #1E88E5;
    selection-color: white;
}}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 75px;                     
    border-left: 2px solid #1E88E5;
    background-color: #1E88E5;
    border-top-right-radius: 12px;
    border-bottom-right-radius: 12px;
}}

QComboBox::down-arrow {{
    width: 50px;
    height: 50px;
    image: url({arrow_path});
}}

QComboBox::down-arrow:on {{
    top: 1px;
    left: 1px;
}}
""")

# Operation Autocomplete
completer = QCompleter([operation_combo.itemText(i) for i in range(operation_combo.count())])
completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
completer.setFilterMode(Qt.MatchFlag.MatchContains)
operation_combo.setCompleter(completer)
work_order_layout.addWidget(operation_combo)
work_order_layout.addSpacing(100)

workorder_combo.currentTextChanged.connect(lambda:update_operation(workorder_btn,operation_combo, workorder_combo, operation_label, machine['machineId']))

button_style = """
QPushButton {
    color: white;
    font-size: 40px;
    font-weight: bold;
    border-radius: 75px;
    padding: 20px 40px;
}
QPushButton:hover {
    opacity: 0.9;
}
QPushButton:pressed {
    transform: scale(0.98);
}
"""

# Work Order button
btn_layout = QVBoxLayout()
btn_layout.setContentsMargins(100,0,100,0)
workorder_btn = QPushButton("Select Work Order")
workorder_btn.setEnabled(False)
workorder_btn.setMinimumSize(100, 150)
workorder_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
workorder_btn.setStyleSheet(button_style2(button_status=False))
btn_shadow(workorder_btn)
btn_layout.addWidget(workorder_btn, stretch=1)
work_order_layout.addLayout(btn_layout)
work_order_layout.addSpacing(200)
workorder_btn.clicked.connect(lambda: [select_workorder(machine, default_widget, work_order_widget), update_machine()])

# work_order_layout.addSpacing(500)
main_layout.addWidget(work_order_widget)
work_order_widget.hide()

# Work Order exists MAIN
default_widget = QWidget()
default_layout = QVBoxLayout(default_widget)
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
# Create individual blocks
work_layout = create_block(f"Work Order : {machine['workName']}", f"Code : {machine['WorkCode']}")
part_layout = create_block(f"Part : {machine['part_name']}", f"Code : {machine['part_code']}")
work_type_layout = create_block(f"Work Type : {machine['work_type_name']}")
operation_layout = create_block(f"Operation : {machine['operation_name']}", f"Code : {machine['operation_sequence']}")

# Arrange blocks in a grid-like layout
block_layout = QVBoxLayout()
block_layout.addLayout(work_layout)
block_layout.addLayout(part_layout)
block_layout.addLayout(operation_layout)
block_layout.addLayout(work_type_layout)

block.setLayout(block_layout)

default_layout.addWidget(block)
default_layout.addSpacing(35)

# BUTTONS

option_layout = QHBoxLayout()
# option_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
option_layout.setSpacing(30) 

button_style = """
QPushButton {
    color: white;
    font-size: 30px;
    font-weight: bold;
    border-radius: 75px;
    padding: 20px 40px;
}
QPushButton:hover {
    opacity: 0.9;
}
QPushButton:pressed {
    transform: scale(0.98);
}
"""

# Work Order button
workorder_btn2 = QPushButton("Close Work Order")
workorder_btn2.setMinimumSize(300, 150)
workorder_btn2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
workorder_btn2.setStyleSheet(button_style + """
    QPushButton {
        background-color: #FF9800;  /* Amber orange */
        border: 3px solid #E65100;
    }
    QPushButton:hover { background-color: #FB8C00; }
    QPushButton:pressed { background-color: #EF6C00; }
""")
btn_shadow(workorder_btn2)
option_layout.addWidget(workorder_btn2, stretch=1)
workorder_btn2.clicked.connect(lambda:workorder_quantity_box(machine, window, default_widget, work_order_widget))


# Down Time button
downtime_btn = QPushButton("Down Time")
downtime_btn.setMinimumSize(300, 150)
downtime_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
downtime_btn.setStyleSheet(button_style + """
    QPushButton {
        background-color: #009688; /* Teal green */
        border: 3px solid #004D40;
    }
    QPushButton:hover { background-color: #00897B; }
    QPushButton:pressed { background-color: #00695C; }
""")
btn_shadow(downtime_btn)
option_layout.addWidget(downtime_btn, stretch=1)

default_layout.addLayout(option_layout)
default_layout.addSpacing(25)

# PRODUCTION PROGRESS
progress_layout = QHBoxLayout()
qty_layout = QVBoxLayout()
qty_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

# Title
title = QLabel("Production Progress")
title.setStyleSheet("font-size: 25px; color: white; font-weight: bold;")
title.setAlignment(Qt.AlignmentFlag.AlignCenter)

# Progress Bar
progress = QProgressBar()
progress.setMinimum(0)
progress.setMaximum(machine['totalQuantity'] if machine['totalQuantity'] else 0)
progress.setValue(machine['quantityDone'] if machine['totalQuantityDone'] else 0)
# progress.setMaximum(55555)
# progress.setValue(55555)
progress.setTextVisible(True)
progress.setFormat("Quantity : %v / %m")
progress.setAlignment(Qt.AlignmentFlag.AlignCenter)

progress.setStyleSheet("""
    QProgressBar {
        border: 3px solid #333;
        border-radius: 20px;
        background-color: #1e1e1e;
        text-align: center;
        color: white;
        font-size: 25px;
        font-weight: bold;
        padding: 10px;
        height: 50px;
    }
    QProgressBar::chunk {
        background-color: #00bcd4;
        border-radius: 20px;
    }
""")

qty_layout.addWidget(title)
qty_layout.addSpacing(10)
qty_layout.addWidget(progress)
progress_layout.addLayout(qty_layout)
progress_layout.addSpacing(20)

qty_layout2 = QVBoxLayout()
qty_layout2.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
shift_production = QLabel(f"Shift_Quantity : 4578")
shift_production.setStyleSheet("font-size: 20px; color: white; font-weight: bold;")
remaining_productoin = QLabel(f"Pending_Quantity : {machine['totalQuantity'] if machine['totalQuantity'] else 0 - machine['quantityDone'] if machine['quantityDone'] else 0}")
remaining_productoin.setStyleSheet("font-size: 20px; color: white; font-weight: bold;")
qty_layout2.addWidget(shift_production)
qty_layout2.addSpacing(10)
qty_layout2.addWidget(remaining_productoin)
progress_layout.addLayout(qty_layout2)

default_layout.addLayout(progress_layout)
default_layout.addSpacing(25)

# MACHINE PRIMARY DATA
machine_layout = QHBoxLayout()
machine_communication_layout = QVBoxLayout()
machine_communication_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
machine_communication_layout.setSpacing(20)
machine_status_layout = QHBoxLayout()
machine_status_layout.setSpacing(15)
machine_status_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
label = QLabel("Machine Status ")
label.setStyleSheet("font-size: 25px; color: white; font-weight: bold;")
colour =random.choice(["#00FF00", "#FFEB3B", "#FF0000"])
status = QLabel()
status.setFixedSize(40, 40)
status.setStyleSheet(f"""
    background-color: {colour}; 
    border-radius: 20px;       
""")

# Glow effect
glow = QGraphicsDropShadowEffect()
glow.setBlurRadius(40)
glow.setColor(QColor(colour))
glow.setOffset(0)
status.setGraphicsEffect(glow)
machine_status_layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignLeft)
machine_status_layout.addWidget(status, alignment=Qt.AlignmentFlag.AlignLeft)
machine_status_layout.addStretch(1)
last_communication = QLabel(f"Last Communication : {machine['last_communication']}")
last_communication.setStyleSheet("font-size: 20px; color: white; font-weight: bold;")
machine_communication_layout.addLayout(machine_status_layout)
machine_communication_layout.addWidget(last_communication, alignment=Qt.AlignmentFlag.AlignLeft)
machine_layout.addLayout(machine_communication_layout)
duration_block = QFrame()
duration_block.setMinimumSize(250, 100)
duration_block.setStyleSheet("""
    QFrame {
        background-color: #1e1e1e;
        border-radius: 15px;
    }
    QLabel {
        font-size: 22px;
        font-weight: bold;
        color: white;
    }
""")
duration_layout = QVBoxLayout()
duration_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
run = QLabel(f"Total Running = {format_time(machine['pin1_duration'])}")
ideal = QLabel(f"Total Ideal = {format_time(machine['pin2_duration'])}")
downtime = QLabel(f"Total Downtime = {format_time(machine['downtime_duration'])}")
offtime = QLabel(f"Total Offtime = {format_time(machine['pin3_duration'])}")
duration_layout.addWidget(run)
duration_layout.addWidget(ideal)
duration_layout.addWidget(downtime)
duration_layout.addWidget(offtime)
duration_block.setLayout(duration_layout)
machine_layout.addWidget(duration_block, alignment=Qt.AlignmentFlag.AlignVCenter)
default_layout.addLayout(machine_layout)

default_layout.addSpacing(10)
main_layout.addWidget(default_widget)
default_widget.hide()

main.setLayout(main_layout)
stack.addWidget(home)
stack.addWidget(main)

if check_in_activity:
    stack.setCurrentWidget(main)
    
if work_order_activity:
    default_widget.show()
else:
    work_order_widget.show()

worker = Worker()
worker.signal.connect(lambda states: print(states))
worker.start()

window.show()
sys.exit(app.exec())

