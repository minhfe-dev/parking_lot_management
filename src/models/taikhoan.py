class TaiKhoan:
    def __init__(self, id_tk=None, username="", password="", role="staff", id_nv=None):
        self.id_tk = id_tk
        self.username = username
        self.password = password
        self.role = role
        self.id_nv = id_nv

    def to_tuple(self):
        return (self.id_tk, self.username, "*****", self.role, self.id_nv)