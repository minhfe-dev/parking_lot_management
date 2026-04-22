class NhanVien:
    def __init__(self, id_nv=None, ho_ten="", sdt="", chuc_vu=""):
        self.id_nv = id_nv        # Khóa chính, có thể là None nếu đang tạo mới (chưa lưu DB)
        self.ho_ten = ho_ten
        self.sdt = sdt
        self.chuc_vu = chuc_vu

    # Hàm phụ trợ để dễ dàng đưa dữ liệu lên QTableWidget
    def to_tuple(self):
        return (self.id_nv, self.ho_ten, self.sdt, self.chuc_vu)