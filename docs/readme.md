
Mô tả dự án

Hệ thống quản lý bãi đỗ xe (Parking Lot Management) là một ứng dụng phần mềm được thiết kế để hỗ trợ quản lý các hoạt động tại bãi đỗ xe một cách hiệu quả. Dự án này sử dụng Python để xây dựng, với cấu trúc tổ chức rõ ràng bao gồm các module cho đăng nhập, quản lý dữ liệu và các dịch vụ nghiệp vụ.


Chức năng chính


1.	Đăng nhập hệ thống
-	Cho phép nhân viên và quản trị viên đăng nhập vào hệ thống với thông tin tài khoản bảo mật.
-	Xác thực quyền truy cập dựa trên vai trò người dùng.


2.	Quản lý nhân viên
-	Thêm, sửa, xóa thông tin nhân viên.
-	Phân quyền và quản lý vai trò trong hệ thống.


3.	Quản lý tài khoản
-	Tạo và quản lý tài khoản người dùng.
-	Đặt lại mật khẩu và bảo mật tài khoản.


4.	Quản lý xe ra vào
-	Ghi nhận xe vào và ra khỏi bãi đỗ.
-	Tính toán thời gian đỗ xe và phí tương ứng.
 
5.	Quản lý thẻ gửi xe
-	Thẻ ngày: Quản lý thẻ gửi xe theo ngày.
-	Thẻ tháng: Quản lý thẻ gửi xe theo tháng với ưu đãi dài hạn.


6.	Quản lý giá cả
-	Thiết lập và cập nhật bảng giá dịch vụ đỗ xe.
-	Áp dụng các chính sách giá linh hoạt.


7.	Lịch sử hoạt động
-	Lưu trữ và truy vấn lịch sử ra vào của xe.
-	Theo dõi các hoạt động của nhân viên.


8.	Thống kê và báo cáo
-	Tạo báo cáo về doanh thu, số lượng xe, và hiệu suất.
-	Phân tích dữ liệu để tối ưu hóa hoạt động bãi đỗ.


Kiến trúc hệ thống


-	Frontend: Giao diện người dùng (có thể tích hợp với GUI framework như Tkinter hoặc web-based).
-	Backend: Xử lý logic nghiệp vụ với Python.
-	Database: Lưu trữ dữ liệu (MySQL).
-	Models: Định nghĩa cấu trúc dữ liệu cho Nhân viên, Tài khoản, Xe.
-	Services: Các module xử lý nghiệp vụ cụ thể
-	Utils: viết các hàm xử lí ảnh để đọc được biển số xe

 
Công nghệ sử dụng
-	Ngôn ngữ: Python
-	Database: MySQL
-	Opencv
-	Easyocr
-	QTdesigner
-	Tkinter
