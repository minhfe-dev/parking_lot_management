import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt

#SERVICE
from src.services import nhanvien_service, taikhoan_service, auth_service


STYLE = """
QWidget {
    background-color: #0f2027;
    color: white;
    font-family: Segoe UI;
}
/*bo tròn các button*/
QPushButton {
    padding: 12px;
    border-radius: 18px;
    background-color: #1c2b36;
    color: white;
    font-weight: bold;
    border: 1px solid #2c3e50;
}

/* hover */
QPushButton:hover {
    background-color: #2c3e50;
}

/* click */
QPushButton:pressed {
    background-color: #34495e;
}
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
        self.name.setPlaceholderText("Nhập họ và tên: ")
        self.phone = QLineEdit()
        self.phone.setPlaceholderText("Nhập mật khẩu: ")
        self.position = QLineEdit()
        self.position.setPlaceholderText("Chức vụ: ")

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
        self.username.setPlaceholderText("Nhập tên tài khoản...")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Nhập mật khẩu...")

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


# ===== THẺ GỬI THÁNG =====
class MonthlyPassScreen(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app

        layout = QVBoxLayout()

        # --- TIÊU ĐỀ ---
        title = QLabel("QUẢN LÝ THẺ GỬI THÁNG")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        # --- KHU VỰC NHẬP LIỆU ---
        form_layout = QFormLayout()

        self.customer_name = QLineEdit()
        self.customer_name.setPlaceholderText("Nhập tên chủ xe...")

        self.license_plate = QLineEdit()
        self.license_plate.setPlaceholderText("Nhập biển số xe...")

        self.vehicle_type = QComboBox()
        self.vehicle_type.addItems(["Xe máy", "Ô tô"])  # Phân loại xe

        self.duration = QSpinBox()  # Ô chọn số lượng (tháng)
        self.duration.setMinimum(1)
        self.duration.setMaximum(24)
        self.duration.setSuffix(" tháng")

        # Thêm các field vào form
        form_layout.addRow("Tên khách hàng:", self.customer_name)
        form_layout.addRow("Biển số xe:", self.license_plate)
        form_layout.addRow("Loại phương tiện:", self.vehicle_type)
        form_layout.addRow("Thời gian đăng ký/gia hạn:", self.duration)

        layout.addLayout(form_layout)

        # --- KHU VỰC NÚT CHỨC NĂNG ---
        btn_layout = QHBoxLayout()  # Xếp các nút nằm ngang

        register_btn = QPushButton("Đăng ký vé mới")
        extend_btn = QPushButton("Gia hạn vé")
        cancel_btn = QPushButton("Hủy vé")

        btn_layout.addWidget(register_btn)
        btn_layout.addWidget(extend_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

        # --- BẢNG HIỂN THỊ DỮ LIỆU ---
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID Thẻ", "Khách hàng", "Biển số", "Loại xe", "Ngày hết hạn", "Trạng thái"])

        # Giãn cột cuối cho vừa màn hình
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        # --- NÚT QUAY LẠI ---
        back = QPushButton("← Quay lại")
        back.clicked.connect(lambda: self.app.setCurrentIndex(1))
        layout.addWidget(back)

        self.setLayout(layout)

        # Kết nối sự kiện cho các nút (Bạn sẽ cần viết logic xử lý DB sau)
        register_btn.clicked.connect(self.register_pass)
        extend_btn.clicked.connect(self.extend_pass)
        cancel_btn.clicked.connect(self.cancel_pass)

    # --- CÁC HÀM XỬ LÝ LOGIC (Placeholder) ---
    def register_pass(self):
        # Lấy dữ liệu từ form để test
        name = self.customer_name.text()
        plate = self.license_plate.text()
        v_type = self.vehicle_type.currentText()
        months = self.duration.value()
        print(f"Đăng ký: {name} | Biển: {plate} | Loại: {v_type} | Số tháng: {months}")
        # TODO: Gọi file service (vd: thethang_service.add(...)) và load lại bảng

    def extend_pass(self):
        print("Gia hạn thẻ...")
        # TODO: Lấy ID từ dòng đang chọn trên bảng và gọi service update ngày hết hạn

    def cancel_pass(self):
        print("Hủy thẻ...")
        # TODO: Lấy ID từ dòng đang chọn và gọi service đổi trạng thái thành "Đã hủy"


# ===== HỆ THỐNG VÀO / RA =====
class InOutScreen(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app

        layout = QVBoxLayout()

        # --- TIÊU ĐỀ ---
        title = QLabel("HỆ THỐNG XE VÀO / RA")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        # --- KHU VỰC CAMERA/ĐỌC ẢNH ---
        cam_layout = QHBoxLayout()

        # 1. Lối Vào
        in_layout = QVBoxLayout()
        in_label = QLabel("📷 Đường dẫn ảnh LỐI VÀO:")
        self.in_image_path = QLineEdit()
        self.in_image_path.setPlaceholderText("Nhập hoặc chọn ảnh xe vào...")

        in_browse_btn = QPushButton("Chọn ảnh")
        in_browse_btn.clicked.connect(lambda: self.browse_image(self.in_image_path))

        in_input_layout = QHBoxLayout()
        in_input_layout.addWidget(self.in_image_path)
        in_input_layout.addWidget(in_browse_btn)

        in_layout.addWidget(in_label)
        in_layout.addLayout(in_input_layout)

        # 2. Lối Ra
        out_layout = QVBoxLayout()
        out_label = QLabel("📷 Đường dẫn ảnh LỐI RA:")
        self.out_image_path = QLineEdit()
        self.out_image_path.setPlaceholderText("Nhập hoặc chọn ảnh xe ra...")

        out_browse_btn = QPushButton("Chọn ảnh")
        out_browse_btn.clicked.connect(lambda: self.browse_image(self.out_image_path))

        out_input_layout = QHBoxLayout()
        out_input_layout.addWidget(self.out_image_path)
        out_input_layout.addWidget(out_browse_btn)

        out_layout.addWidget(out_label)
        out_layout.addLayout(out_input_layout)

        cam_layout.addLayout(in_layout)
        cam_layout.addLayout(out_layout)
        layout.addLayout(cam_layout)

        # --- KHU VỰC NHẬP THỦ CÔNG ---
        manual_layout = QFormLayout()
        self.manual_plate = QLineEdit()
        self.manual_plate.setPlaceholderText("VD: 29A-123.45")
        self.manual_plate.setStyleSheet("font-size: 16px; padding: 8px;")
        manual_layout.addRow("Nhập biển số thủ công (Nếu lỗi ảnh):", self.manual_plate)
        layout.addLayout(manual_layout)

        # --- NÚT CHỨC NĂNG VÀO / RA ---
        btn_layout = QHBoxLayout()

        self.btn_in = QPushButton("⬇ CHO XE VÀO")
        self.btn_in.setStyleSheet("background-color: #27ae60; font-size: 16px; padding: 15px;")

        self.btn_out = QPushButton("⬆ CHO XE RA")
        self.btn_out.setStyleSheet("background-color: #e74c3c; font-size: 16px; padding: 15px;")

        btn_layout.addWidget(self.btn_in)
        btn_layout.addWidget(self.btn_out)
        layout.addLayout(btn_layout)

        # --- LOG THÔNG BÁO ---
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFixedHeight(120)
        self.log_area.setPlaceholderText("Thông báo hệ thống sẽ hiển thị tại đây...")
        layout.addWidget(self.log_area)

        # --- NÚT QUAY LẠI ---
        back = QPushButton("← Quay lại")
        back.clicked.connect(lambda: self.app.setCurrentIndex(1))
        layout.addWidget(back)

        self.setLayout(layout)

        # Kết nối sự kiện nút Vào/Ra
        self.btn_in.clicked.connect(self.process_entry)
        self.btn_out.clicked.connect(self.process_exit)

    # --- CÁC HÀM XỬ LÝ LÔ-GIC ---
    def browse_image(self, line_edit):
        # Mở hộp thoại chọn file ảnh
        fname, _ = QFileDialog.getOpenFileName(self, "Chọn ảnh biển số", "", "Images (*.png *.jpg *.jpeg)")
        if fname:
            line_edit.setText(fname)
            self.log_area.append(f"Đã tải ảnh: {fname}. Đang đọc OCR...")
            # Giả lập OCR đọc thành công và gán vào ô nhập thủ công
            self.manual_plate.setText("30A-12345")

    def process_entry(self):
        plate = self.manual_plate.text().strip()
        if not plate:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng scan ảnh hoặc nhập biển số!")
            return

        # TODO: Gọi DB lưu thông tin xe vào
        self.log_area.append(f"✅ [VÀO BÃI] - Xe mang biển số {plate} đã vào.")
        self.clear_inputs()

    def process_exit(self):
        plate = self.manual_plate.text().strip()
        if not plate:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng scan ảnh hoặc nhập biển số!")
            return

        # TODO: Kiểm tra DB, tính tiền và cho xe ra
        self.log_area.append(f"📤 [RỜI BÃI] - Xe mang biển số {plate} đã ra.")
        self.clear_inputs()

    def clear_inputs(self):
        self.in_image_path.clear()
        self.out_image_path.clear()
        self.manual_plate.clear()


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
            "CÀI ĐẶT GIÁ": 6,
            "THỐNG KÊ": 7,
            "HỆ THỐNG XE VÀO/RA": 8
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
        self.month = MonthlyPassScreen(self)
        self.history = FeatureScreen("LỊCH SỬ XE", self)
        self.price = FeatureScreen("CÀI ĐẶT GIÁ", self)
        self.report1 = FeatureScreen("THỐNG KÊ", self)
        self.inout = InOutScreen(self)
        self.addWidget(self.login)   # 0
        self.addWidget(self.main)    # 1
        self.addWidget(self.staff)   # 2
        self.addWidget(self.account) # 3
        self.addWidget(self.month)
        self.addWidget(self.history)
        self.addWidget(self.price)
        self.addWidget(self.report1)
        self.addWidget(self.inout)  # 8

        self.setCurrentIndex(0)

    def show_main(self, role):
        self.setCurrentIndex(1)


# ===== RUN =====
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)

    window = App()
    window.setWindowTitle("Phần mềm Quản lý Bãi đỗ xe")
    window.resize(1000, 600)
    window.show()

    sys.exit(app.exec())