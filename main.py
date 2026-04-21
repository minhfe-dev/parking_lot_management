import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt

# 👉 SERVICE
from src.services import nhanvien_service, taikhoan_service, auth_service


STYLE = """
QWidget {
    background-color: #0f2027;
    color: white;
    font-family: Segoe UI;
}
QPushButton {
    padding: 15px;
    border-radius: 25px;
    background-color: #1c2b36;
}
QPushButton:hover { background-color: #2c3e50; }
"""


# ===== LOGIN =====
class LoginWindow(QWidget):
    def __init__(self, switch_to_main):
        super().__init__()
        self.switch_to_main = switch_to_main

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # CARD
        card = QFrame()
        card.setProperty("class", "card")
        card.setFixedWidth(350)

        card_layout = QVBoxLayout()
        card_layout.setSpacing(15)

        # TITLE
        title = QLabel("ĐĂNG NHẬP")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold;")

        # INPUT
        self.user = QLineEdit()
        self.user.setPlaceholderText("Username")

        self.pw = QLineEdit()
        self.pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.pw.setPlaceholderText("Password")

        # BUTTON
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

        # ENTER để login
        self.user.returnPressed.connect(self.login)
        self.pw.returnPressed.connect(self.login)

        # ADD
        card_layout.addWidget(title)
        card_layout.addWidget(self.user)
        card_layout.addWidget(self.pw)
        card_layout.addWidget(btn)

        card.setLayout(card_layout)
        layout.addWidget(card)

        self.setLayout(layout)

    # CHỈ THAY LOGIC Ở ĐÂY
    def login(self):
        result = auth_service.login(
            self.user.text(),
            self.pw.text()
        )

        if result:
            role = result[0]
            self.switch_to_main(role)
        else:
            QMessageBox.warning(self, "Lỗi", "Sai tài khoản hoặc mật khẩu!")

    def clear_fields(self):
        self.user.clear()
        self.pw.clear()


# ===== TEMPLATE =====
class FeatureScreen(QWidget):
    def __init__(self, title, app):
        super().__init__()
        self.app = app

        layout = QVBoxLayout()
        label = QLabel(title)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        back = QPushButton("← Quay lại")
        back.clicked.connect(lambda: self.app.setCurrentIndex(1))

        layout.addWidget(label)
        layout.addWidget(back)
        self.setLayout(layout)


# ===== STAFF =====
class StaffScreen(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app

        layout = QVBoxLayout()

        self.name = QLineEdit()
        self.phone = QLineEdit()
        self.position = QLineEdit()

        add_btn = QPushButton("Thêm")
        update_btn = QPushButton("Sửa")
        delete_btn = QPushButton("Xoá")

        self.search = QLineEdit()
        search_btn = QPushButton("Tìm")

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Tên", "SĐT", "Chức vụ"])

        layout.addWidget(self.name)
        layout.addWidget(self.phone)
        layout.addWidget(self.position)
        layout.addWidget(add_btn)
        layout.addWidget(update_btn)
        layout.addWidget(delete_btn)
        layout.addWidget(self.search)
        layout.addWidget(search_btn)
        layout.addWidget(self.table)

        back = QPushButton("← Quay lại")
        back.clicked.connect(lambda: self.app.setCurrentIndex(1))
        layout.addWidget(back)

        self.setLayout(layout)

        add_btn.clicked.connect(self.add_staff)
        update_btn.clicked.connect(self.update_staff)
        delete_btn.clicked.connect(self.delete_staff)
        search_btn.clicked.connect(self.search_staff)
        self.table.cellClicked.connect(self.fill_form)

        self.load_data()

    def load_data(self):
        rows = nhanvien_service.get_all()
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))

    def add_staff(self):
        nhanvien_service.add(self.name.text(), self.phone.text(), self.position.text())
        self.load_data()

    def update_staff(self):
        row = self.table.currentRow()
        if row < 0: return
        staff_id = self.table.item(row, 0).text()

        nhanvien_service.update(
            staff_id,
            self.name.text(),
            self.phone.text(),
            self.position.text()
        )
        self.load_data()

    def delete_staff(self):
        row = self.table.currentRow()
        if row < 0: return
        staff_id = self.table.item(row, 0).text()

        nhanvien_service.delete(staff_id)
        self.load_data()

    def search_staff(self):
        rows = nhanvien_service.search(self.search.text())
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))

    def fill_form(self, row, col):
        self.name.setText(self.table.item(row, 1).text())
        self.phone.setText(self.table.item(row, 2).text())
        self.position.setText(self.table.item(row, 3).text())


# ===== ACCOUNT =====
class AccountScreen(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app

        layout = QVBoxLayout()

        self.username = QLineEdit()
        self.password = QLineEdit()

        self.role = QComboBox()
        self.role.addItems(["admin", "staff"])

        self.employee = QComboBox()

        add_btn = QPushButton("Thêm")
        delete_btn = QPushButton("Xoá")

        self.table = QTableWidget()
        self.table.setColumnCount(5)

        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(self.role)
        layout.addWidget(self.employee)
        layout.addWidget(add_btn)
        layout.addWidget(delete_btn)
        layout.addWidget(self.table)

        back = QPushButton("← Quay lại")
        back.clicked.connect(lambda: self.app.setCurrentIndex(1))
        layout.addWidget(back)

        self.setLayout(layout)

        add_btn.clicked.connect(self.add_user)
        delete_btn.clicked.connect(self.delete_user)

        self.load_employees()
        self.load_data()

    def load_employees(self):
        rows = taikhoan_service.get_employees()
        self.employee.clear()
        for r in rows:
            self.employee.addItem(r[1], r[0])

    def load_data(self):
        rows = taikhoan_service.get_all()
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))

    def add_user(self):
        taikhoan_service.add(
            self.username.text(),
            self.password.text(),
            self.role.currentText(),
            self.employee.currentData()
        )
        self.load_data()

    def delete_user(self):
        row = self.table.currentRow()
        if row < 0: return
        user_id = self.table.item(row, 0).text()

        taikhoan_service.delete(user_id)
        self.load_data()


# ===== MAIN MENU =====
class MainWindow(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app

        grid = QGridLayout()

        features = [
            "HỆ THỐNG XE VÀO/RA",
            "QUẢN LÝ NHÂN VIÊN",
            "QUẢN LÝ TÀI KHOẢN",
            "THẺ GỬI THÁNG",
            "LỊCH SỬ XE",
            "CÀI ĐẶT GIÁ",
            "THỐNG KÊ"
        ]

        for i, name in enumerate(features):
            btn = QPushButton(name)
            btn.clicked.connect(lambda _, n=name: self.open_feature(n))
            grid.addWidget(btn, i // 3, i % 3)

        self.setLayout(grid)

    def open_feature(self, name):
        mapping = {
            "QUẢN LÝ NHÂN VIÊN": 2,
            "QUẢN LÝ TÀI KHOẢN": 3,
            "THẺ GỬI THÁNG": 4,
            "LỊCH SỬ XE": 5,
            "CÀI ĐẶT GIÁ":6,
            "THỐNG KÊ":7,
        }
        if name in mapping:
            self.app.setCurrentIndex(mapping[name])


# ===== APP =====
class App(QStackedWidget):
    def __init__(self):
        super().__init__()

        self.login = LoginWindow(self.show_main)
        self.main = MainWindow(self)
        self.staff = StaffScreen(self)
        self.account = AccountScreen(self)

        # placeholder cho các màn khác
        self.month = FeatureScreen("THẺ GỬI THÁNG", self)
        self.history = FeatureScreen("LỊCH SỬ XE", self)
        self.price = FeatureScreen("CÀI ĐẶT GIÁ", self)
        self.report1 = FeatureScreen("THỐNG KÊ", self)

        self.addWidget(self.login)   # 0
        self.addWidget(self.main)    # 1
        self.addWidget(self.staff)   # 2
        self.addWidget(self.account) # 3
        self.addWidget(self.month)
        self.addWidget(self.history)
        self.addWidget(self.price)
        self.addWidget(self.report1)


        self.setCurrentIndex(0)

    def show_main(self, role):
        self.setCurrentIndex(1)


# ===== RUN =====
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)

    window = App()
    window.show()

    sys.exit(app.exec())