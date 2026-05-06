import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHeaderView, QGridLayout
from PyQt6.QtCore import QDate, QTime, QDateTime

from src.services import (
    nhanvien_service,
    taikhoan_service,
    auth_service,
    theguithang_service,
    ravao_service,
    lichsu_service,
    gia_service
)
from src.utils import img_processing

STYLE = """
QWidget {
    background-color: #0f2027;
    color: white;
    font-family: Segoe UI;
}

/* BUTTON */
QPushButton {
    padding: 10px;
    border-radius: 12px;
    background-color: #1c2b36;
    color: white;
    font-weight: bold;
    border: 1px solid #2c3e50;
}

QPushButton:hover {
    background-color: #2c3e50;
}

QPushButton:pressed {
    background-color: #34495e;
}

/* INPUT */
QLineEdit, QComboBox, QSpinBox {
    padding: 8px;
    border-radius: 8px;
    border: 1px solid #2c3e50;
    background-color: #1c2b36;
}

/* TABLE */
QTableWidget {
    background-color: #1c2b36;
    border-radius: 10px;
    gridline-color: #2c3e50;
}

QHeaderView::section {
    background-color: #2c3e50;
    padding: 5px;
    border: none;
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

        #title
        title = QLabel("ĐĂNG NHẬP")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold;")

        #input
        self.user = QLineEdit()
        self.user.setPlaceholderText("Username")

        self.pw = QLineEdit()
        self.pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.pw.setPlaceholderText("Password")

        #button
        btn = QPushButton("ĐĂNG NHẬP")
        btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 12px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #2c3e50;
            }
        """)

        btn.clicked.connect(self.login)

        self.user.returnPressed.connect(self.login)
        self.pw.returnPressed.connect(self.login)

        #thêm layout
        card_layout.addWidget(title)
        card_layout.addWidget(self.user)
        card_layout.addWidget(self.pw)
        card_layout.addWidget(btn)

        card.setLayout(card_layout)
        layout.addWidget(card)

        self.setLayout(layout)

    def login(self):
        result = auth_service.login(self.user.text(), self.pw.text())

        print(f"DEBUG: Kết quả từ DB: {result}")

        if result:
            role = result[0]
            print(f"DEBUG: Role lấy được: {role}")
            self.switch_to_main(role)
        else:
            print("DEBUG: Đăng nhập thất bại (result is None)")
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
        self.phone.setPlaceholderText("Nhập số điện thoại: ")
        self.position = QLineEdit()
        self.position.setPlaceholderText("Chức vụ: ")

        add_btn = QPushButton("Thêm")
        update_btn = QPushButton("Sửa")
        delete_btn = QPushButton("Xoá")

        self.search = QLineEdit()
        self.search.setPlaceholderText("Nhập họ tên hoặc số điện thoại")
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
        self.clear_inputs()

    def update_staff(self):
        row = self.table.currentRow()
        if row < 0: return
        staff_id = self.table.item(row, 0).text()

        nhanvien_service.update(staff_id, self.name.text(), self.phone.text(), self.position.text())
        self.load_data()
        self.clear_inputs()

    def delete_staff(self):
        row = self.table.currentRow()
        if row < 0: return
        staff_id = self.table.item(row, 0).text()

        nhanvien_service.delete(staff_id)
        self.load_data()
        self.clear_inputs()

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

    def clear_inputs(self):
        self.name.clear()
        self.phone.clear()
        self.position.clear()


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
        self.table.setHorizontalHeaderLabels(["ID", "Username", "Password", "Quyền"])

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
        self.username.clear()
        self.password.clear()

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

        title = QLabel("QUẢN LÝ THẺ GỬI THÁNG")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        form_layout = QFormLayout()

        self.customer_name = QLineEdit()
        self.customer_name.setPlaceholderText("Nhập tên chủ xe...")

        self.license_plate = QLineEdit()
        self.license_plate.setPlaceholderText("Nhập biển số xe...")

        self.vehicle_type = QComboBox()
        self.vehicle_type.addItems(["Xe máy", "Ô tô"])

        self.duration = QSpinBox()
        self.duration.setMinimum(1)
        self.duration.setMaximum(24)
        self.duration.setSuffix(" tháng")

        form_layout.addRow("Tên khách hàng:", self.customer_name)
        form_layout.addRow("Biển số xe:", self.license_plate)
        form_layout.addRow("Loại phương tiện:", self.vehicle_type)
        form_layout.addRow("Thời gian đăng ký/gia hạn:", self.duration)

        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()

        register_btn = QPushButton("Đăng ký vé mới")
        extend_btn = QPushButton("Gia hạn vé")
        cancel_btn = QPushButton("Hủy vé")

        btn_layout.addWidget(register_btn)
        btn_layout.addWidget(extend_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID Thẻ", "Khách hàng", "Biển số", "Loại xe", "Ngày hết hạn", "Trạng thái"])

        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        back = QPushButton("← Quay lại")
        back.clicked.connect(lambda: self.app.setCurrentIndex(1))
        layout.addWidget(back)

        self.setLayout(layout)

        register_btn.clicked.connect(self.register_pass)
        extend_btn.clicked.connect(self.extend_pass)
        cancel_btn.clicked.connect(self.cancel_pass)

        self.load_data()

    def load_data(self):
        rows = theguithang_service.get_all()
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))

    def register_pass(self):
        success, msg = theguithang_service.add(
            self.customer_name.text(),
            self.license_plate.text(),
            self.vehicle_type.currentText(),
            self.duration.value()
        )
        if success:
            self.load_data()
            self.clear_inputs()
            QMessageBox.information(self, "Thành công", msg)
        else:
            QMessageBox.warning(self, "Lỗi", msg)

    def extend_pass(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn thẻ cần gia hạn!")
            return

        card_id = self.table.item(row, 0).text()
        success, msg = theguithang_service.extend(card_id, self.duration.value())
        if success:
            self.load_data()
            QMessageBox.information(self, "Thành công", msg)
        else:
            QMessageBox.warning(self, "Lỗi", msg)

    def cancel_pass(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn thẻ cần hủy!")
            return

        card_id = self.table.item(row, 0).text()
        success, msg = theguithang_service.cancel(card_id)
        if success:
            self.load_data()
            QMessageBox.information(self, "Thành công", msg)
        else:
            QMessageBox.warning(self, "Lỗi", msg)

    def clear_inputs(self):
        self.customer_name.clear()
        self.license_plate.clear()
        self.duration.setValue(1)


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
        in_label = QLabel(" Đường dẫn ảnh LỐI VÀO:")
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
        out_label = QLabel(" Đường dẫn ảnh LỐI RA:")
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
        self.manual_plate.setPlaceholderText("Nhập biển số xe tại đây...")
        self.manual_plate.setStyleSheet("font-size: 16px; padding: 8px;")
        manual_layout.addRow("Nhập biển số thủ công (Nếu lỗi ảnh):", self.manual_plate)
        layout.addLayout(manual_layout)

        # --- NÚT CHỨC NĂNG VÀO / RA ---
        btn_layout = QHBoxLayout()

        self.btn_in = QPushButton("CHO XE VÀO")
        self.btn_in.setStyleSheet("background-color: #27ae60; font-size: 16px; padding: 15px;")

        self.btn_out = QPushButton("CHO XE RA")
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

    def browse_image(self, line_edit):
        fname, _ = QFileDialog.getOpenFileName(self, "Chọn ảnh biển số", "", "Images (*.png *.jpg *.jpeg)")
        if fname:
            line_edit.setText(fname)
            self.log_area.append(f"Đã chọn ảnh: {fname}")

    def process_entry(self):
        img_path = self.in_image_path.text().strip()
        plate = self.manual_plate.text().strip()

        if img_path:
            self.log_area.append(f"Đang nhận diện biển số từ ảnh vào: {img_path}...")
            QApplication.processEvents()
            detected_plate = img_processing.extract_plate(img_path)
            if detected_plate:
                plate = detected_plate
                self.manual_plate.setText(plate)
                self.log_area.append(f"✓ Nhận diện biển số thành công: {plate}")
            else:
                self.log_area.append("✗ Không nhận diện được biển số từ ảnh vào. Sử dụng biển số nhập tay nếu có.")

        if not plate:
            QMessageBox.warning(self, "Cảnh báo", "Không đọc được biển số từ ảnh. Vui lòng nhập biển số thủ công!")
            return

        success, msg = ravao_service.process_entry(plate, img_path)

        if success:
            self.log_area.append(f" [VÀO BÃI] - {msg}")
            QMessageBox.information(self, "Thông báo", f"Xe biển số {plate} đã vào bãi.")
            self.clear_inputs()
        else:
            self.log_area.append(f" [LỖI VÀO] - {msg}")

    def process_exit(self):
        img_path = self.out_image_path.text().strip()
        plate = self.manual_plate.text().strip()

        if img_path:
            self.log_area.append(f"Đang nhận diện biển số từ ảnh ra: {img_path}...")
            QApplication.processEvents()
            detected_plate = img_processing.extract_plate(img_path)
            if detected_plate:
                plate = detected_plate
                self.manual_plate.setText(plate)
                self.log_area.append(f"✓ Nhận diện biển số thành công: {plate}")
            else:
                self.log_area.append("✗ Không nhận diện được biển số từ ảnh ra. Sử dụng biển số nhập tay nếu có.")

        if not plate:
            QMessageBox.warning(self, "Cảnh báo", "Không đọc được biển số từ ảnh. Vui lòng nhập biển số thủ công!")
            return

        success, msg = ravao_service.process_exit(plate, img_path)

        if success:
            self.log_area.append(f" [RỜI BÃI] - {msg}")
            QMessageBox.information(self, "Thông báo", f"Xe biển số {plate} đã rời bãi.")
            self.clear_inputs()
        else:
            self.log_area.append(f" [LỖI RA] - {msg}")

    def clear_inputs(self):
        self.in_image_path.clear()
        self.out_image_path.clear()
        self.manual_plate.clear()


# ==== LỊCH SỬ XE RA VÀO ====
class HistoryScreen(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app

        layout = QVBoxLayout()

        # --- TIÊU ĐỀ ---
        title = QLabel("LỊCH SỬ XE RA / VÀO")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        # --- KHU VỰC TÌM KIẾM & BỘ LỌC ---
        filter_group = QFrame()
        filter_group.setStyleSheet("QFrame { background-color: #1c2b36; border-radius: 10px; padding: 10px; }")
        filter_layout = QGridLayout()

        self.search_plate = QLineEdit()
        self.search_plate.setPlaceholderText("Nhập biển số xe...")
        filter_layout.addWidget(QLabel("Biển số xe:"), 0, 0)
        filter_layout.addWidget(self.search_plate, 0, 1)

        self.search_name = QLineEdit()
        self.search_name.setPlaceholderText("Nhập tên chủ xe (vé tháng)...")
        filter_layout.addWidget(QLabel("Tên chủ xe:"), 0, 2)
        filter_layout.addWidget(self.search_name, 0, 3)

        self.time_from = QDateTimeEdit(QDateTime.currentDateTime().addDays(-1))
        self.time_from.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.time_from.setCalendarPopup(True)
        filter_layout.addWidget(QLabel("Từ thời gian:"), 1, 0)
        filter_layout.addWidget(self.time_from, 1, 1)

        self.time_to = QDateTimeEdit(QDateTime.currentDateTime())
        self.time_to.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.time_to.setCalendarPopup(True)
        filter_layout.addWidget(QLabel("Đến thời gian:"), 1, 2)
        filter_layout.addWidget(self.time_to, 1, 3)

        btn_layout = QHBoxLayout()
        search_btn = QPushButton(" Tìm kiếm")
        search_btn.setStyleSheet("background-color: #2980b9;")
        search_btn.clicked.connect(self.search_history)

        refresh_btn = QPushButton(" Làm mới")
        refresh_btn.clicked.connect(self.clear_filters)

        btn_layout.addWidget(search_btn)
        btn_layout.addWidget(refresh_btn)
        filter_layout.addLayout(btn_layout, 2, 0, 1, 4)

        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        # --- BẢNG HIỂN THỊ LỊCH SỬ ---
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID Giao dịch", "Biển số", "Loại vé", "Tên chủ xe", "Giờ VÀO", "Giờ RA", "Thành tiền/Trạng thái"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        # --- NÚT QUAY LẠI ---
        back = QPushButton("← Quay lại")
        back.clicked.connect(lambda: self.app.setCurrentIndex(1))
        layout.addWidget(back)

        self.setLayout(layout)
        self.load_data()

    def load_data(self):
        rows = lichsu_service.get_all()
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))

    def search_history(self):
        plate = self.search_plate.text().strip()
        name = self.search_name.text().strip()
        t_from = self.time_from.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        t_to = self.time_to.dateTime().toString("yyyy-MM-dd HH:mm:ss")

        rows = lichsu_service.search(plate, name, t_from, t_to)

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))

    def clear_filters(self):
        self.search_plate.clear()
        self.search_name.clear()
        self.time_to.setDateTime(QDateTime.currentDateTime())
        self.time_from.setDateTime(QDateTime.currentDateTime().addDays(-1))
        self.load_data()


# ===== CÀI ĐẶT GIÁ VÉ =====
class PriceSettingScreen(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app

        layout = QVBoxLayout()

        # --- TIÊU ĐỀ ---
        title = QLabel("CẤU HÌNH ĐƠN GIÁ DỊCH VỤ")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)

        content_layout = QHBoxLayout()

        # ---GIÁ VÉ NGÀY ---
        day_group = QGroupBox("Giá Vé Ngày (VNĐ/Giờ)")
        day_group.setStyleSheet(
            "QGroupBox { font-weight: bold; border: 1px solid #2c3e50; margin-top: 10px; padding: 15px; }")
        day_layout = QFormLayout()

        self.day_motor = QSpinBox()
        self.day_motor.setRange(0, 1000000)
        self.day_motor.setSingleStep(1000)
        self.day_motor.setSuffix(" VNĐ")

        self.day_car = QSpinBox()
        self.day_car.setRange(0, 1000000)
        self.day_car.setSingleStep(5000)
        self.day_car.setSuffix(" VNĐ")

        day_layout.addRow("Xe máy:", self.day_motor)
        day_layout.addRow("Ô tô:", self.day_car)
        day_group.setLayout(day_layout)

        # ---GIÁ VÉ THÁNG ---
        month_group = QGroupBox("Giá Vé Tháng (VNĐ/Tháng)")
        month_group.setStyleSheet(
            "QGroupBox { font-weight: bold; border: 1px solid #2c3e50; margin-top: 10px; padding: 15px; }")
        month_layout = QFormLayout()

        self.month_motor = QSpinBox()
        self.month_motor.setRange(0, 10000000)
        self.month_motor.setSingleStep(10000)
        self.month_motor.setSuffix(" VNĐ")

        self.month_car = QSpinBox()
        self.month_car.setRange(0, 10000000)
        self.month_car.setSingleStep(50000)
        self.month_car.setSuffix(" VNĐ")

        month_layout.addRow("Xe máy:", self.month_motor)
        month_layout.addRow("Ô tô:", self.month_car)
        month_group.setLayout(month_layout)

        content_layout.addWidget(day_group)
        content_layout.addWidget(month_group)
        layout.addLayout(content_layout)

        # --- NÚT LƯU CÀI ĐẶT ---
        save_btn = QPushButton(" LƯU THAY ĐỔI")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12; 
                font-size: 16px; 
                margin-top: 20px;
                padding: 15px;
            }
            QPushButton:hover { background-color: #e67e22; }
        """)
        save_btn.clicked.connect(self.save_prices)
        layout.addWidget(save_btn)

        layout.addStretch()

        # --- NÚT QUAY LẠI ---
        back = QPushButton("← Quay lại")
        back.clicked.connect(lambda: self.app.setCurrentIndex(1))
        layout.addWidget(back)

        self.setLayout(layout)
        self.load_current_prices()

    def load_current_prices(self):
        prices = gia_service.get_current_prices()
        self.day_motor.setValue(prices.get("day_motor", 0))
        self.day_car.setValue(prices.get("day_car", 0))
        self.month_motor.setValue(prices.get("month_motor", 0))
        self.month_car.setValue(prices.get("month_car", 0))

    def save_prices(self):
        prices = {
            "day_motor": self.day_motor.value(),
            "day_car": self.day_car.value(),
            "month_motor": self.month_motor.value(),
            "month_car": self.month_car.value()
        }

        success, message = gia_service.update_prices(prices)
        if success:
            QMessageBox.information(self, "Thông báo", message)
        else:
            QMessageBox.critical(self, "Lỗi", message)


# ===== MAIN MENU =====
class MainWindow(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # ===== SIDEBAR =====
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #111b24;
            }
            QPushButton {
                text-align: left;
                padding: 12px;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2c3e50;
            }
        """)

        side_layout = QVBoxLayout()

        title = QLabel("🚗 PARKING")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        side_layout.addWidget(title)

        # MENU
        self.buttons = {}
        menu_items = [
            ("🚪 Vào / Ra", 8),
            ("👨‍💼 Nhân viên", 2),
            ("🔐 Tài khoản", 3),
            ("🪪 Vé tháng", 4),
            ("📜 Lịch sử", 5),
            ("💰 Giá vé", 6),
            ("📊 Thống kê", 7),
        ]

        for text, index in menu_items:
            btn = QPushButton(text)
            btn.clicked.connect(lambda _, i=index: self.switch(i))
            side_layout.addWidget(btn)
            self.buttons[index] = btn

        side_layout.addStretch()

        # LOGOUT
        logout_btn = QPushButton("🚪 Đăng xuất")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
            }
        """)
        logout_btn.clicked.connect(self.logout)

        side_layout.addWidget(logout_btn)
        sidebar.setLayout(side_layout)

        # ===== CONTENT =====
        content = QFrame()
        content.setStyleSheet("background-color: #0f2027;")

        content_layout = QVBoxLayout()

        self.content_title = QLabel("DASHBOARD")
        self.content_title.setStyleSheet("font-size: 24px; font-weight: bold;")
        content_layout.addWidget(self.content_title)

        content_layout.addStretch()
        content.setLayout(content_layout)

        # ===== ADD =====
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content)

        self.setLayout(main_layout)

    def switch(self, index):
        for i, btn in self.buttons.items():
            if i == index:
                btn.setStyleSheet("background-color: #3498db;")
            else:
                btn.setStyleSheet("")
        self.app.setCurrentIndex(index)

    def logout(self):
        reply = QMessageBox.question(
            self,
            "Xác nhận",
            "Bạn có chắc muốn đăng xuất?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.app.logout()


# ===== APP =====
class App(QStackedWidget):
    def __init__(self):
        super().__init__()

        self.login_screen = LoginWindow(self.show_main)
        self.main_screen = MainWindow(self)
        self.staff_screen = StaffScreen(self)
        self.account_screen = AccountScreen(self)
        self.month_screen = MonthlyPassScreen(self)
        self.history_screen = HistoryScreen(self)
        self.price_screen = PriceSettingScreen(self)
        self.report_screen = FeatureScreen("THỐNG KÊ", self)
        self.inout_screen = InOutScreen(self)


        self.addWidget(self.login_screen)  # Index 0
        self.addWidget(self.main_screen)  # Index 1
        self.addWidget(self.staff_screen)  # Index 2
        self.addWidget(self.account_screen)  # Index 3
        self.addWidget(self.month_screen)  # Index 4
        self.addWidget(self.history_screen)  # Index 5
        self.addWidget(self.price_screen)  # Index 6
        self.addWidget(self.report_screen)  # Index 7
        self.addWidget(self.inout_screen)  # Index 8

        self.setCurrentIndex(0)

    def show_main(self, role):
        print(f"Đăng nhập thành công với quyền: {role}")
        self.setCurrentIndex(1)

    def logout(self):
        self.login_screen.clear_fields()
        self.setCurrentIndex(0)
# ===== RUN =====
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)

    window = App()
    window.setWindowTitle("Phần mềm Quản lý Bãi đỗ xe")
    window.resize(1000, 600)
    window.show()

    sys.exit(app.exec())