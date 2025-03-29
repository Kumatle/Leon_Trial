import sys
import uuid
import os
import random
import subprocess
import requests
import re
from datetime import datetime
from mitmproxy import http
from PyQt5.QtCore import Qt, QSettings, QDateTime, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QFontMetrics
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, 
    QMessageBox, QProgressBar, QFrame, QHBoxLayout, QCheckBox, QDialog
)
import socket
import threading
import pyuac  

def request_admin_permission():
    """ตรวจสอบและขอสิทธิ์ Administrator หากยังไม่ได้รับสิทธิ์"""
    if not pyuac.isUserAdmin():
        pyuac.runAsAdmin()  
        sys.exit() 

request_admin_permission()  

def install_package(package):
    """ติดตั้งแพ็กเกจโดยใช้ pip ถ้ายังไม่ได้ติดตั้ง"""
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.Popen([sys.executable, "-m", "pip", "show", package], stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
        print(f"{package} ได้ถูกติดตั้งแล้ว")
    except subprocess.CalledProcessError:
        try:
            subprocess.Popen([sys.executable, "-m", "pip", "install", package], stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
            print(f"{package} ติดตั้งเรียบร้อยแล้ว")
        except subprocess.CalledProcessError:
            print(f"ไม่สามารถติดตั้ง {package}")

def install_sdelete():
    """ดาวน์โหลดและติดตั้ง sdelete (หากไม่ติดตั้งผ่าน pip)"""
    sdelete_url = "https://download.sysinternals.com/files/SDelete.zip"
    zip_path = "SDelete.zip"
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.Popen(["curl", "-O", sdelete_url], stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
        subprocess.Popen(["powershell", "Expand-Archive", zip_path, "-DestinationPath", "."], stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
        print("ติดตั้ง SDelete เรียบร้อยแล้ว")
    except subprocess.CalledProcessError:
        print("ไม่สามารถติดตั้ง SDelete")

packages = ["selenium", "mitmproxy", "plyer", "requests", "pycryptodome", "pyuac"]
for package in packages:
    install_package(package)

install_sdelete()  

def get_all_drives():
    """ค้นหาไดรฟ์ทั้งหมดที่มีในระบบ Windows"""
    drives = []
    for drive in range(65, 91): 
        drive_letter = chr(drive) + ":\\" 
        if os.path.exists(drive_letter):
            drives.append(drive_letter)
    return drives

def sdelete_all_drives(progress_callback=None):
    """ใช้คำสั่ง sdelete กับทุกไดรฟ์ที่พบในระบบและอัปเดตสถานะผ่าน progress_callback"""
    drives = get_all_drives()
    total_drives = len(drives)
    for idx, drive in enumerate(drives):
        print(f"💥 กำลังทำลายข้อมูลใน {drive}")
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.Popen(["sdelete", "-p", "3", drive], stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
            print(f"✔️ ทำลายข้อมูลใน {drive} สำเร็จ")
            if progress_callback:
                progress_callback((idx + 1) / total_drives * 100)
        except subprocess.CalledProcessError as e:
            print(f"❌ ไม่สามารถทำลายข้อมูลใน {drive}: {e}")
            if progress_callback:
                progress_callback(((idx + 1) / total_drives) * 100)

class WelcomeWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Leon")
        self.setGeometry(100, 100, 600, 300)
        self.center_window()

        self.settings = QSettings("YourCompany", "YourApp")
        self.serial_numbers = [
            "lK3z4bZAEI", "30PpGmqnix", "u09AFFVaKN", "ToTL51Tp0S", "KsnHhX1EAA", "q3B3eOvHle",
            "E32ediaT9o", "EujrtTlOiw", "DNT1o9VqQM", "GLq0nIQ1Rw", "akCtddQU9t", "x7RrI8Bawx",
            "GfLMfVw3G0", "BbuSPiLPKO", "5g7xUyJ1HD", "76imhKr3VW", "guUOYDEa8u", "38R69zGf7i",
            "U7RP1f4uxv", "l0uRfLn5qW", "RWTSsYMvBW", "04beqWKznN", "AqsZ4zAgZ6", "wr21mToyao",
            "n6W0FEFL5c", "kGF1RjxGDx", "CglX4p0N6e", "gTehJIhQb9", "FcwbJP4sEE", "dZm3sqYAdR",
            "UImfH0643l", "l0fk2Q7pQI", "uF0XtoEAfC", "Ef19rHkENo", "wS7ZFb69SM", "DlTeQmOahN",
            "J4mYtSylGr", "B3IxK56s3g", "XD8cPHItdc", "VeVEXpN6lP", "MoAhWHKE0S", "nELhkrXQ0I",
            "000", "001", "002"
        ]
        stored_serial = self.settings.value("serial_number", "").strip()

        layout = QVBoxLayout()
        
        welcome_label = QLabel("Welcome to Leon!\nโปรแกรมที่จะทำให้คุณปลอดภัยมากขึ้น!", self)
        welcome_label.setFont(QFont("Arial", 20, QFont.Bold))
        welcome_label.setAlignment(Qt.AlignCenter)

        self.serial_label = QLabel("กรุณากรอก Serial Number:", self)
        self.serial_input = QLineEdit(self)
        self.serial_input.setPlaceholderText("กรอก Serial Number ที่นี่")
        self.serial_input.setFont(QFont("Arial", 20))

        self.try_button = QPushButton("ยืนยัน", self)
        self.try_button.setStyleSheet("font-size: 18px; background-color: lightblue;")
        self.try_button.clicked.connect(self.verify_serial_and_open)

        layout.addWidget(welcome_label)
        layout.addWidget(self.serial_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.serial_input)
        layout.addWidget(self.try_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

        if stored_serial in self.serial_numbers and not self.is_serial_expired(stored_serial):
            print("Serial number valid, opening main window.")
            QTimer.singleShot(100, self.open_main_window)
        else:
            self.show()

    def center_window(self):
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)

    def get_hardware_id(self):
        return str(uuid.UUID(int=uuid.getnode()))

    def verify_serial_and_open(self):
        serial_number = self.serial_input.text().strip()

        if serial_number not in self.serial_numbers:
            QMessageBox.warning(self, "ข้อผิดพลาด", "Serial Number ไม่ถูกต้อง, โปรดลองใหม่อีกครั้ง.")
            return

        if self.is_serial_expired(serial_number):
            QMessageBox.warning(self, "หมดอายุ", f"Serial Number {serial_number} หมดอายุแล้ว กรุณาลงทะเบียนใหม่.")
            return

        if self.is_serial_used(serial_number):
            QMessageBox.warning(self, "ไม่สามารถใช้งานได้", f"Serial Number {serial_number} ถูกใช้ไปแล้ว.")
            return

        hardware_id = self.get_hardware_id()
        stored_hardware_id = self.settings.value(f"{serial_number}_hardware_id", "").strip()

        if stored_hardware_id and stored_hardware_id != hardware_id:
            QMessageBox.warning(self, "ไม่สามารถใช้งานได้", f"Serial Number {serial_number} ถูกใช้งานกับเครื่องอื่นแล้ว.")
            return

        self.settings.setValue("serial_number", serial_number)
        self.settings.setValue(f"{serial_number}_hardware_id", hardware_id)
        self.settings.setValue(f"{serial_number}_start_date", QDateTime.currentDateTime().toString(Qt.ISODate))
        self.settings.setValue(f"{serial_number}_used", True)

        self.open_main_window()

    def is_serial_expired(self, serial_number):
        current_date = QDateTime.currentDateTime()
        start_date_str = self.settings.value(f"{serial_number}_start_date", None)

        if not start_date_str:
            return False

        start_date = QDateTime.fromString(start_date_str, Qt.ISODate)

        if not start_date.isValid():
            return False

        seconds_diff = start_date.secsTo(current_date)
        return seconds_diff >= 259200

    def is_serial_used(self, serial_number):
        return self.settings.value(f"{serial_number}_used", False)

    def open_main_window(self):
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()

class WorkerThread(QThread):
    update_status = pyqtSignal(bool)

    def run(self):
        for i in range(5):
            self.update_status.emit(True)
            self.msleep(1000)
        self.update_status.emit(False)

class PasswordDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ยืนยันรหัสผ่าน")
        self.setFixedSize(300, 150)

        layout = QVBoxLayout()

        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("กรุณากรอกรหัสผ่าน")

        self.confirm_button = QPushButton("ยืนยัน", self)
        self.confirm_button.clicked.connect(self.on_confirm)

        layout.addWidget(self.password_input)
        layout.addWidget(self.confirm_button)

        self.setLayout(layout)

    def on_confirm(self):
        if self.password_input.text() == "DESTROY":
            self.accept()  # ปิดหน้าต่างนี้
            self.show_countdown()
        else:
            QMessageBox.warning(self, "รหัสผ่านผิด", "กรุณากรอกรหัสผ่านใหม่อีกครั้ง.")

    def show_countdown(self):
        countdown_dialog = CountdownDialog()
        countdown_dialog.exec_()

class CountdownDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Countdown")
        self.setGeometry(100, 100, 400, 200)
        self.setFixedSize(400, 200)
        self.center_window()

        self.countdown_label = QLabel("Time Remaining: 60")
        self.countdown_label.setFont(QFont("Arial", 20))
        self.countdown_label.setAlignment(Qt.AlignCenter)

        self.confirm_button = QPushButton("ยืนยัน")
        self.confirm_button.setStyleSheet("background-color: red; color: white; font-size: 18px;")
        self.confirm_button.clicked.connect(self.skip_countdown)

        self.cancel_button = QPushButton("ยกเลิก")
        self.cancel_button.setStyleSheet("background-color: white; color: black; font-size: 18px;")
        self.cancel_button.clicked.connect(self.stop_countdown)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.confirm_button)
        button_layout.addWidget(self.cancel_button)

        layout = QVBoxLayout()
        layout.addWidget(self.countdown_label)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.remaining_time = 60  # เปลี่ยนจาก 10 เป็น 60 วินาที

        self.start_countdown()

    def center_window(self):
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)

    def start_countdown(self):
        self.timer.start(1000)
        self.confirm_button.setEnabled(True)
        self.cancel_button.setEnabled(True)

    def skip_countdown(self):
        self.timer.stop()
        self.confirm_destruction()  # เรียกฟังก์ชันยืนยันการทำลายข้อมูล

    def stop_countdown(self):
        self.timer.stop()
        self.close()  # ปิดหน้าต่าง countdown ทันทีเมื่อกด "ยกเลิก"

    def update_countdown(self):
        self.remaining_time -= 1
        self.countdown_label.setText(f"Time Remaining: {self.remaining_time}")
        if self.remaining_time == 0:
            self.timer.stop()
            self.show_progress_bar()

    def show_progress_bar(self):
        self.progress_window = ProgressWindow()
        self.progress_window.start_destruction()  # เริ่มทำลายข้อมูล
        self.progress_window.exec_()
        self.close()

class ProgressWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Progress Bar")
        self.setGeometry(100, 100, 400, 120)
        self.setFixedSize(400, 120)
        self.center_window()

        layout = QVBoxLayout()

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self.info_label = QLabel("กำลังทำลายข้อมูล", self)
        self.info_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.progress_bar)
        layout.addWidget(self.info_label)

        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.progress_value = 0
        self.timer.start(100)

        self.total_steps = 100
        self.current_step = 0

    def center_window(self):
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)

    def update_progress(self, progress=None):
        """อัปเดตสถานะของ Progress Bar"""
        if progress is not None:
            self.progress_value = progress
        else:
            self.progress_value += 1

        self.progress_bar.setValue(self.progress_value)
        self.info_label.setText(f"กำลังทำลายข้อมูล... {self.progress_value:.2f}%")

        if self.progress_value >= 100:
            self.timer.stop()
            self.info_label.setText("ข้อมูลถูกทำลายเรียบร้อยแล้ว!")
            self.close()  # ปิดหน้าต่างเมื่อ Progress Bar เสร็จ

    def start_destruction(self):
        """เริ่มกระบวนการทำลายข้อมูล"""
        sdelete_all_drives(self.update_progress)

class ConfirmationDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Settings")
        self.setFixedSize(300, 150)

        self.settings = QSettings("YourCompany", "YourApp")

        layout = QVBoxLayout()

        self.checkbox = QCheckBox("คุณต้องการตั้งค่าอุปกรณ์นี้เป็นเครื่องแม่หรือไม่", self)

        self.checkbox.setChecked(self.settings.value("terms_accepted", False, type=bool))

        confirm_button = QPushButton("Confirm", self)
        confirm_button.clicked.connect(self.on_confirm)

        layout.addWidget(self.checkbox)
        layout.addWidget(confirm_button)

        self.setLayout(layout)

        self.center()

    def on_confirm(self):
        if self.checkbox.isChecked():
            QMessageBox.information(self, "Settings", "อุปกรณ์นี้เป็นเครื่องแม่")
            self.device_type = "master"
            self.setup_network_connection()
        else:
            QMessageBox.information(self, "Settings", "อุปกรณ์นี้เป็นเครื่องลูก")
            self.device_type = "slave"
            self.setup_network_connection()

        self.settings.setValue("terms_accepted", self.checkbox.isChecked())
        self.accept()

    def center(self):
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        window_geometry = self.geometry()
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2
        self.move(x, y)

    def setup_network_connection(self):
        if self.device_type == "master":
            threading.Thread(target=self.listen_for_connections, daemon=True).start()
        elif self.device_type == "slave":
            self.connect_to_master()

    def listen_for_connections(self):
        host = '0.0.0.0'  
        port = 5000 

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        print("กำลังรอการเชื่อมต่อจากเครื่องลูก...")

        client_socket, client_address = server_socket.accept()
        print(f"เชื่อมต่อกับเครื่องลูกที่ {client_address}")

    def connect_to_master(self):
        host = '192.168.1.100'
        port = 5000 

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        print(f"เชื่อมต่อกับเครื่องแม่ที่ {host}:{port}")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Leon")
        self.setFixedSize(600, 400)

        main_layout = QVBoxLayout()

        frame_a = QFrame(self)
        frame_a.setFrameShape(QFrame.NoFrame)
        frame_a.setStyleSheet("background-color: #e5e8e8;")

        label = QLabel("Leon", self)
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Arial", 26, QFont.Bold))

        frame_a_layout = QVBoxLayout()
        frame_a_layout.addWidget(label)
        frame_a.setLayout(frame_a_layout)

        frame_b = QFrame(self)
        frame_b.setFrameShape(QFrame.StyledPanel)
        frame_b.setStyleSheet("background-color: #aed6f1; border: 2px solid black;")
        frame_b.setMinimumHeight(80)

        frame_c = QFrame(self)
        frame_c.setFrameShape(QFrame.StyledPanel)
        frame_c.setStyleSheet("background-color: lightblue; border: 2px solid black;")
        frame_c.setMinimumHeight(80)

        frame_d = QFrame(self)
        frame_d.setFrameShape(QFrame.StyledPanel)
        frame_d.setStyleSheet("background-color: lightcoral; border: 2px solid black;")
        frame_d.setMinimumHeight(80)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(frame_b)
        bottom_layout.addWidget(frame_c)
        bottom_layout.addWidget(frame_d)

        main_layout.addWidget(frame_a)
        main_layout.addLayout(bottom_layout)

        self.status_dot = QLabel(self)
        self.status_dot.setFixedSize(10, 10)
        self.status_dot.setStyleSheet("background-color: red; border-radius: 5px;")
        self.status_dot.move(570, 12)

        button_size = int(70 * 2.25)

        self.circle_button_c = QPushButton("ตั้งค่า", self)
        self.circle_button_d = QPushButton("ทำลายข้อมูล", self)

        self.circle_button_c.setFixedSize(button_size, button_size)
        self.circle_button_d.setFixedSize(button_size, button_size)

        self.circle_button_c.setStyleSheet(f"""
            QPushButton {{
                background-color: rgb(174, 214, 241);
                border-radius: {button_size // 2}px;
                border: 2px solid black;
                font-size: 20px;
            }}
            QPushButton:pressed {{
                background-color: rgb(144, 184, 211);
                border: 2px solid black;
                padding-top: 3px;
            }}
        """)

        self.circle_button_d.setStyleSheet(f"""
            QPushButton {{
                background-color: red;
                border-radius: {button_size // 2}px;
                border: 2px solid black;
                font-size: 20px;
                color: white;
            }}
            QPushButton:pressed {{
                background-color: darkred;
                border: 2px solid black;
                padding-top: 3px;
            }}
        """)

        frame_c_layout = QVBoxLayout()
        frame_c_layout.addWidget(self.circle_button_c, alignment=Qt.AlignCenter)
        frame_c.setLayout(frame_c_layout)

        frame_d_layout = QVBoxLayout()
        frame_d_layout.addWidget(self.circle_button_d, alignment=Qt.AlignCenter)
        frame_d.setLayout(frame_d_layout)

        self.setLayout(main_layout)

        self.circle_button_c.clicked.connect(self.show_confirmation_dialog)
        self.circle_button_d.clicked.connect(self.show_destroy_confirmation)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_and_update_ip)
        self.timer.start(1000)

        self.frame_b_label = QLabel(self)
        self.frame_b_label.setAlignment(Qt.AlignTop | Qt.AlignCenter)

        frame_b_layout = QVBoxLayout()
        frame_b_layout.addWidget(self.frame_b_label)
        frame_b.setLayout(frame_b_layout)

        self.update_ip_in_frame_b(get_fake_ip())

    def show_confirmation_dialog(self):
        dialog = ConfirmationDialog()
        dialog.exec_()

    def show_destroy_confirmation(self):
        reply = QMessageBox.question(self, "ยืนยันการทำลายข้อมูล", "คุณต้องการทำลายข้อมูลใช่หรือไม่?", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.show_password_dialog()

    def show_password_dialog(self):
        dialog = PasswordDialog()
        dialog.exec_()

    def check_and_update_ip(self):
        now = datetime.now()
        if now.hour == 0 and now.minute == 1:
            fake_ip = get_fake_ip()
            self.update_ip_in_frame_b(fake_ip)

    def update_ip_in_frame_b(self, fake_ip):
        ip_info = f"IP Address\nปัจจุบันคือ\n{fake_ip['ip']}\nLocation\n{fake_ip['city']}, {fake_ip['country']}"
        font = QFont("Arial", 12)
        font_metrics = QFontMetrics(font)
        max_width = self.frame_b_label.width() - 20
        if font_metrics.boundingRect(ip_info).width() > max_width:
            font.setPointSize(10)

        self.frame_b_label.setFont(font)
        self.frame_b_label.setText(ip_info)

ip_ranges = {
    "China": [{"ip": "218.107.132.66", "country": "China", "city": "Beijing"}],
    "Japan": [{"ip": "59.184.138.210", "country": "Japan", "city": "Tokyo"}],
    "Lao": [{"ip": "202.137.156.83", "country": "Lao", "city": "Viangchan"}],
    "Cambodia": [{"ip": "202.58.98.130", "country": "Cambodia", "city": "Phnom Penh"}],
    "Myanmar": [{"ip": "116.206.139.101", "country": "Myanmar", "city": "Yangon"}],
    "Russia": [{"ip": "46.17.46.213", "country": "Russia", "city": "Moscow"}],
    "United Arab Emirates": [{"ip": "110.83.110.250", "country": "United Arab Emirates", "city": "Dubai"}],
    "Cuba": [{"ip": "190.6.66.92", "country": "Cuba", "city": "Havana"}],
    "Singapore": [{"ip": "128.199.129.174", "country": "Singapore", "city": "Singapore"}],
    "Malaysia": [{"ip": "219.93.183.103", "country": "Malaysia", "city": "Kuala Lumpur"}]
}

def get_fake_ip():
    country = random.choice(list(ip_ranges.keys()))
    fake_ip = random.choice(ip_ranges[country])
    return fake_ip

def spoof_ipconfig():
    fake_ip = get_fake_ip()
    result = subprocess.run(['ipconfig'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = re.sub(r'\d+\.\d+\.\d+\.\d+', fake_ip['ip'], result.stdout)
    print(output)
    print(f"📢 ข้อมูล IP ปลอมที่แสดง: {fake_ip['ip']}")
    print(f"📍 ตำแหน่ง: {fake_ip['city']}, {fake_ip['country']}")
    return fake_ip

def send_request_with_ssl_bypass(url):
    try:
        response = requests.get(url, verify=False)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        return None

def request(flow: http.HTTPFlow) -> None:
    fake_ip = get_fake_ip()
    if flow.request.host in ["example.com", "test.com"]: 
        flow.response = http.Response.make(
            200,  
            f"IP ปลอม: {fake_ip['ip']}, ประเทศ: {fake_ip['country']}, เมือง: {fake_ip['city']}".encode(),  
            {"Content-Type": "text/plain"} 
        )

def simulate_ping_traceroute(command):
    fake_ip = get_fake_ip()
    if 'ping' in command or 'traceroute' in command:
        result = f"PING {fake_ip['ip']} ({fake_ip['ip']}) 56(84) bytes of data.\n"
        result += f"64 bytes from {fake_ip['ip']}: icmp_seq=1 ttl=64 time=0.045 ms\n"
        result += f"--- {fake_ip['ip']} ping statistics ---\n"
        result += f"1 packets transmitted, 1 received, 0% packet loss, time 0ms\n"
        result += f"rtt min/avg/max/mdev = 0.045/0.045/0.045/0.000 ms\n"
        print(result)
    return fake_ip

def update_fake_ip_at_midnight():
    now = datetime.now()
    if now.hour == 0 and now.minute == 0:
        get_fake_ip() 
        print("IP ปลอมถูกอัปเดตแล้ว")

if __name__ == '__main__':
    spoof_ipconfig()  
    simulate_ping_traceroute("ping")  
    send_request_with_ssl_bypass("https://example.com") 

    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
