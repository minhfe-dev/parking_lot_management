import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QGridLayout, QMessageBox, QStackedWidget, QFrame
)
from PyQt6.QtCore import Qt


# ===== STYLE =====
STYLE = """
QWidget {
    background-color: #0f2027;
    color: white;
    font-size: 14px;
}

QLineEdit {
    padding: 8px;
    border-radius: 8px;
    background: #2c3e50;
    color: white;
}

QPushButton {
    padding: 10px;
    border-radius: 15px;
    background-color: #1c2b36;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #2c3e50;
}

.card {
    background-color: #1c2b36;
    border-radius: 20px;
    padding: 20px;
}
"""


# ===== LOGIN =====
class LoginWindow(QWidget):
    def __init__(self, switch_to_main):
        super().__init__()
        self.switch_to_main = switch_to_main
        self.setWindowTitle("Đăng nhập")
        self.resize(1000, 700)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setFixedWidth(350)
        card.setProperty("class", "card")

        card_layout = QVBoxLayout()

        title = QLabel("ĐĂNG NHẬP HỆ THỐNG")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.user = QLineEdit()
        self.user.setPlaceholderText("Tên đăng nhập")

        self.passwd = QLineEdit()
        self.passwd.setPlaceholderText("Mật khẩu")
        self.passwd.setEchoMode(QLineEdit.EchoMode.Password)

        btn = QPushButton("ĐĂNG NHẬP")
        btn.clicked.connect(self.login)

        self.user.returnPressed.connect(self.login)
        self.passwd.returnPressed.connect(self.login)

        card_layout.addWidget(title)
        card_layout.addWidget(self.user)
        card_layout.addWidget(self.passwd)
        card_layout.addWidget(btn)

        card.setLayout(card_layout)
        main_layout.addWidget(card)

        self.setLayout(main_layout)

    def login(self):
        if self.user.text() == "admin" and self.passwd.text() == "123":
            self.switch_to_main()
        else:
            QMessageBox.warning(self, "Lỗi", "Đăng nhập không thành công")


# ===== MAIN =====
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Parking System")
        self.resize(1000, 700)

        grid = QGridLayout()

        features = [
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

        for pos, text in zip(positions, features):
            btn = QPushButton(text)
            btn.setMinimumHeight(120)

            btn.clicked.connect(lambda _, t=text: self.open_feature(t))

            grid.addWidget(btn, *pos)

        self.setLayout(grid)

    def open_feature(self, name):
        QMessageBox.information(self, "Chức năng", f"Bạn chọn: {name}")


# ===== APP =====
class App(QStackedWidget):
    def __init__(self):
        super().__init__()

        self.login = LoginWindow(self.show_main)
        self.main = MainWindow()

        self.addWidget(self.login)
        self.addWidget(self.main)

        self.setCurrentWidget(self.login)

    def show_main(self):
        self.setCurrentWidget(self.main)


# ===== RUN =====
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)

    window = App()
    window.show()

    sys.exit(app.exec())    