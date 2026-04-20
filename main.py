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
            "SELECT role FROM users WHERE username=%s AND password=%s",
            (self.user.text(), self.pw.text())
        )

        result = cursor.fetchone()

        if result:
            role = result[0]  # lấy role
            self.switch_to_main(role)  # truyền role
        else:
            QMessageBox.warning(self, "Lỗi", "Sai tài khoản hoặc mật khẩu!")

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
class StaffScreen(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app

        layout = QVBoxLayout()

        form = QHBoxLayout()

        self.name = QLineEdit()
        self.name.setPlaceholderText("Tên")

        self.phone = QLineEdit()
        self.phone.setPlaceholderText("SĐT")

        self.position = QLineEdit()
        self.position.setPlaceholderText("Chức vụ")

        form.addWidget(self.name)
        form.addWidget(self.phone)
        form.addWidget(self.position)
        layout.addLayout(form)

        btn_layout = QHBoxLayout()

        add_btn = QPushButton("Thêm")
        update_btn = QPushButton("Sửa")
        delete_btn = QPushButton("Xoá")

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(update_btn)
        btn_layout.addWidget(delete_btn)
        layout.addLayout(btn_layout)

        search_layout = QHBoxLayout()

        self.search = QLineEdit()
        self.search.setPlaceholderText("Tìm theo tên")

        search_btn = QPushButton("Tìm")

        search_layout.addWidget(self.search)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Tên", "SĐT", "Chức vụ"])

        layout.addWidget(self.table)

        back = QPushButton("← Quay lại")
        back.clicked.connect(lambda: self.app.setCurrentIndex(1))
        layout.addWidget(back)

        self.setLayout(layout)

        # EVENT
        add_btn.clicked.connect(self.add_staff)
        update_btn.clicked.connect(self.update_staff)
        delete_btn.clicked.connect(self.delete_staff)
        search_btn.clicked.connect(self.search_staff)
        self.table.cellClicked.connect(self.fill_form)

        self.load_data()

    # ===== ĐỂ RA NGOÀI __init__ =====

    def load_data(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees")
        rows = cursor.fetchall()
        conn.close()
        self.show_data(rows)

    def show_data(self, rows):
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))

    def add_staff(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO employees (name, phone, position) VALUES (%s,%s,%s)",
            (self.name.text(), self.phone.text(), self.position.text())
        )

        conn.commit()
        conn.close()
        self.load_data()

    def update_staff(self):
        row = self.table.currentRow()
        if row < 0:
            return

        staff_id = self.table.item(row, 0).text()

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE employees SET name=%s, phone=%s, position=%s WHERE id=%s",
            (self.name.text(), self.phone.text(), self.position.text(), staff_id)
        )

        conn.commit()
        conn.close()
        self.load_data()

    def delete_staff(self):
        row = self.table.currentRow()
        if row < 0:
            return

        staff_id = self.table.item(row, 0).text()

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM employees WHERE id=%s", (staff_id,))
        conn.commit()
        conn.close()
        self.load_data()

    def search_staff(self):
        keyword = self.search.text()

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM employees WHERE name LIKE %s",
            (f"%{keyword}%",)
        )

        rows = cursor.fetchall()
        conn.close()
        self.show_data(rows)

    def fill_form(self, row, col):
        self.name.setText(self.table.item(row, 1).text())
        self.phone.setText(self.table.item(row, 2).text())
        self.position.setText(self.table.item(row, 3).text())

class AccountScreen(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app

        layout = QVBoxLayout()

        # ===== FORM =====
        form = QHBoxLayout()

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")

        self.role = QComboBox()
        self.role.addItems(["admin", "staff"])

        self.employee = QComboBox()

        form.addWidget(self.username)
        form.addWidget(self.password)
        form.addWidget(self.role)
        form.addWidget(self.employee)

        layout.addLayout(form)

        # ===== BUTTON =====
        btn_layout = QHBoxLayout()

        add_btn = QPushButton("Thêm")
        delete_btn = QPushButton("Xoá")

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(delete_btn)

        layout.addLayout(btn_layout)

        # ===== TABLE =====
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "User", "Role", "Nhân viên", "EmpID"])

        layout.addWidget(self.table)

        # BACK
        back = QPushButton("← Quay lại")
        back.clicked.connect(lambda: self.app.setCurrentIndex(1))
        layout.addWidget(back)

        self.setLayout(layout)

        # EVENT
        add_btn.clicked.connect(self.add_user)
        delete_btn.clicked.connect(self.delete_user)

        self.load_employees()
        self.load_data()
    def load_employees(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, name FROM employees")
        rows = cursor.fetchall()

        self.employee.clear()
        for r in rows:
            self.employee.addItem(r[1], r[0])

        conn.close()
    def load_data(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT u.id, u.username, u.role, e.name, u.employee_id
            FROM users u
            LEFT JOIN employees e ON u.employee_id = e.id
        """)

        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))
    def add_user(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, password, role, employee_id) VALUES (%s,%s,%s,%s)",
            (
                self.username.text(),
                self.password.text(),
                self.role.currentText(),
                self.employee.currentData()
            )
        )

        conn.commit()
        conn.close()
        self.load_data()
    def delete_user(self):
        row = self.table.currentRow()
        if row < 0:
            return

        user_id = self.table.item(row, 0).text()

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
        conn.commit()
        conn.close()

        self.load_data()


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

        self.buttons = {}  # 👈 THÊM DÒNG NÀY

        for pos, name in zip(positions, self.features):
            btn = QPushButton(name)

            self.buttons[name] = btn  # 👈 THÊM DÒNG NÀY (QUAN TRỌNG)

            btn.setMinimumHeight(120)
            btn.clicked.connect(lambda _, n=name: self.open_feature(n))

            grid.addWidget(btn, *pos)
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
            self.app.login.clear_fields()
            self.app.setCurrentIndex(0)
        else:
            self.app.setCurrentIndex(mapping[name])

    def set_role(self, role):
        if role != "admin":
            self.buttons["QUẢN LÝ NHÂN VIÊN"].hide()
            self.buttons["QUẢN LÝ TÀI KHOẢN"].hide()


# ===== APP =====
class App(QStackedWidget):
    def __init__(self):
        super().__init__()

        self.login = LoginWindow(self.show_main)
        self.main = MainWindow(self)

        self.parking = ParkingScreen(self)
        self.staff = StaffScreen(self)
        self.account = AccountScreen(self)
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

    def show_main(self, role):
        self.main.set_role(role)  # truyền role xuống menu
        self.setCurrentIndex(1)


# ===== RUN =====
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)

window = App()
window.show()
sys.exit(app.exec())