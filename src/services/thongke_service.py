import matplotlib.pyplot as plt
import numpy as np

months = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
income = np.array([400, 842, 999, 762, 333, 542, 879, 923, 104, 235, 109, 200])

plt.bar(months, income)
plt.xlabel("Tháng")
plt.ylabel("Lượt gửi")
plt.title("Thống kê lượt gửi theo tháng")

plt.show()