import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from data.connect_database import get_connection


# ===== STYLE =====
STYLE = """
QWidget {
    background-color: #0f2027;
    color: white;
    font-family: Segoe UI;
}

/* INPUT */
QLineEdit {
    padding: 10px;
    border-radius: 10px;
    background: #1c2b36;
    border: 1px solid #2c3e50;
}

/* BUTTON */
QPushButton {
    padding: 15px;
    border-radius: 20px;
    background-color: #1c2b36;
    font-weight: bold;
    border: 1px solid #2c3e50;
}

QPushButton:hover {
    background-color: #2c3e50;
}

QPushButton:pressed {
    background-color: #34495e;
}

/* CARD */
.card {
    background-color: #16232d;
    border-radius: 25px;
    padding: 25px;
}
"""


# ===== LOGIN =====
class LoginWindow(QWidget):
    def __init__(self, switch_to_main):
        super().__init__()
        self.switch_to_main = switch_to_main

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setProperty("class", "card")
        card.setFixedWidth(350)

        card_layout = QVBoxLayout()
        card_layout.setSpacing(15)

        title = QLabel("ĐĂNG NHẬP")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold;")

        self.user = QLineEdit()
        self.user.setPlaceholderText("Username")

        self.pw = QLineEdit()
        self.pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.pw.setPlaceholderText("Password")

        btn = QPushButton("ĐĂNG NHẬP")
        btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                border-radius: 12px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f618d;
            }
        """)
        btn.clicked.connect(self.login)

        self.user.returnPressed.connect(self.login)
        self.pw.returnPressed.connect(self.login)

        card_layout.addWidget(title)
        card_layout.addWidget(self.user)
        card_layout.addWidget(self.pw)
        card_layout.addWidget(btn)

        card.setLayout(card_layout)
        layout.addWidget(card)

        self.setLayout(layout)

    from data.connect_database import get_connection

    def login(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (self.user.text(), self.pw.text())
        )

        result = cursor.fetchone()

        if result:
            self.switch_to_main()
        else:
            QMessageBox.warning(self, "Lỗi", "Sai tài khoản hoặc mật khẩu! ")

        conn.close()

    def clear_fields(self):
        self.user.clear()
        self.pw.clear()


# ===== TEMPLATE =====
class FeatureScreen(QWidget):
    def __init__(self, title, app):
        super().__init__()
        self.app = app

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel(title)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 24px; font-weight: bold;")

        back = QPushButton("← Quay lại")
        back.clicked.connect(lambda: self.app.setCurrentIndex(1))

        layout.addWidget(label)
        layout.addWidget(back)

        self.setLayout(layout)


# ===== PARKING =====
class ParkingScreen(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setProperty("class", "card")
        card.setFixedSize(900, 600)

        card_layout = QVBoxLayout()
        card_layout.setSpacing(30)

        title = QLabel("HỆ THỐNG GỬI XE VÀO / RA")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")

        cam_layout = QGridLayout()
        cam_layout.setSpacing(40)

        cam1 = QLabel("CAMERA LÀN VÀO")
        cam1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cam1.setStyleSheet("background:black; border-radius:10px;")
        cam1.setFixedSize(300, 200)

        cam2 = QLabel("CAMERA LÀN RA")
        cam2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cam2.setStyleSheet("background:black; border-radius:10px;")
        cam2.setFixedSize(300, 200)

        cam_layout.addWidget(cam1, 0, 0)
        cam_layout.addWidget(cam2, 0, 1)

        btn_layout = QGridLayout()
        btn_layout.setSpacing(100)

        btn_in = QPushButton("VÀO")
        btn_in.setStyleSheet("background-color:#2ecc71;")

        btn_out = QPushButton("RA")
        btn_out.setStyleSheet("background-color:#e74c3c;")

        btn_layout.addWidget(btn_in, 0, 0)
        btn_layout.addWidget(btn_out, 0, 1)

        back = QPushButton("← Quay lại")
        back.clicked.connect(lambda: self.app.setCurrentIndex(1))

        card_layout.addWidget(title)
        card_layout.addLayout(cam_layout)
        card_layout.addLayout(btn_layout)
        card_layout.addWidget(back)

        card.setLayout(card_layout)
        layout.addWidget(card)

        self.setLayout(layout)


# ===== MAIN MENU =====
class MainWindow(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app

        grid = QGridLayout()
        grid.setSpacing(30)
        grid.setContentsMargins(40, 40, 40, 40)

        self.features = [
            "HỆ THỐNG XE VÀO/RA",
            "QUẢN LÝ NHÂN VIÊN",
            "QUẢN LÝ TÀI KHOẢN",
            "THẺ GỬI THÁNG",
            "THẺ GỬI NGÀY",
            "LỊCH SỬ XE",
            "CÀI ĐẶT GIÁ",
            "BÁO CÁO - THỐNG KÊ",
            "ĐĂNG XUẤT"
        ]

        positions = [(i, j) for i in range(3) for j in range(3)]

        for pos, name in zip(positions, self.features):
            btn = QPushButton(name)
            btn.setMinimumHeight(120)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1c2b36;
                    border-radius: 25px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #2c3e50;
                }
            """)
            btn.clicked.connect(lambda _, n=name: self.open_feature(n))
            grid.addWidget(btn, *pos)

        self.setLayout(grid)

    def open_feature(self, name):
        mapping = {
            "HỆ THỐNG XE VÀO/RA": 2,
            "QUẢN LÝ NHÂN VIÊN": 3,
            "QUẢN LÝ TÀI KHOẢN": 4,
            "THẺ GỬI THÁNG": 5,
            "THẺ GỬI NGÀY": 6,
            "LỊCH SỬ XE": 7,
            "CÀI ĐẶT GIÁ": 8,
            "BÁO CÁO - THỐNG KÊ": 9,
        }

        if name == "ĐĂNG XUẤT":
            self.app.login.clear_fields()  # xoá dữ liệu login
            self.app.setCurrentIndex(0)  # quay về login


# ===== APP =====
class App(QStackedWidget):
    def __init__(self):
        super().__init__()

        self.login = LoginWindow(self.show_main)
        self.main = MainWindow(self)

        self.parking = ParkingScreen(self)
        self.staff = FeatureScreen("QUẢN LÝ NHÂN VIÊN", self)
        self.account = FeatureScreen("QUẢN LÝ TÀI KHOẢN", self)
        self.month = FeatureScreen("THẺ GỬI THÁNG", self)
        self.day = FeatureScreen("THẺ GỬI NGÀY", self)
        self.history = FeatureScreen("LỊCH SỬ XE", self)
        self.price = FeatureScreen("CÀI ĐẶT GIÁ", self)
        self.report = FeatureScreen("BÁO CÁO - THỐNG KÊ", self)

        self.addWidget(self.login)   # 0
        self.addWidget(self.main)    # 1
        self.addWidget(self.parking) # 2
        self.addWidget(self.staff)   # 3
        self.addWidget(self.account) # 4
        self.addWidget(self.month)   # 5
        self.addWidget(self.day)     # 6
        self.addWidget(self.history) # 7
        self.addWidget(self.price)   # 8
        self.addWidget(self.report)  # 9

        self.setCurrentIndex(0)

    def show_main(self):
        self.setCurrentIndex(1)


# ===== RUN =====
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)

    window = App()
    window.show()

    sys.exit(app.exec())