# test_product_view.py

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget
from views.product_view import ProductView
from models.product_model import Product

def main():
    app = QApplication(sys.argv)

    # 用一个最简单的 QMainWindow 来承载 ProductView
    win = QMainWindow()
    win.setWindowTitle("ProductView 测试")

    tabs = QTabWidget()
    win.setCentralWidget(tabs)

    # 只创建并测试商品管理这一个标签页
    product_view = ProductView()
    tabs.addTab(product_view, "商品管理")

    # 构造几条测试数据（不写入数据库）
    samples = []
    for i in range(8):
        p = Product(name=f"商品{i+1}",
                    price=2.0 + i,
                    stock=10 + i,
                    image="resources/images/test.png")
        setattr(p, "id", i + 1)  # 手动给它一个 id
        samples.append(p)

    # 渲染到视图
    product_view.display_products(samples)

    win.resize(800, 600)
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
