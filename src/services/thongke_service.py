import matplotlib.pyplot as plt

def draw_chart():
    data = get_revenue_by_day()

    days = [x[0] for x in data]
    revenue = [x[1] for x in data]

    plt.bar(days, revenue)
    plt.title("Doanh thu theo ngày")
    plt.xlabel("Ngày")
    plt.ylabel("Tiền")

    plt.xticks(rotation=45)
    plt.show()