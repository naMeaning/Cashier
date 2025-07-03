# main.py

import sys
from PySide6.QtWidgets import QApplication
from views.main_window import MainWindow  # 只依赖已经写好的 main_window.py
from models.database import init_db
from views.main_window import MainWindow
from controllers.product_controller import ProductController
from controllers.payment_controller import PaymentController
from controllers.inventory_controller import InventoryController
from controllers.member_controller import MemberController
from controllers.report_controller import ReportController

def main():
    """
    程序入口：
      1) 创建 QApplication
      2) 实例化 MainWindow（含占位标签页）
      3) 显示窗口并进入事件循环
    """
    
    # 1) Qt 应用
    app = QApplication(sys.argv)

    # 2) 初始化数据库，建表，拿到 SessionFactory
    Session = init_db()  

    # 3) 主窗口（包含已经替换好的 ProductView）
    window = MainWindow()
    window.resize(900, 650)

    # 4) 挂载商品管理的 Controller
    #    这样一来，ProductView 发出的 search/product_clicked 信号
    #    就会被 ProductController 处理，Model <-> View 完成连接
    prod_ctrl = ProductController(Session, window.product_view)
    pay_ctrl  = PaymentController(Session, window.payment_view, prod_ctrl)
    inv_ctrl  = InventoryController(Session, window.inventory_view, prod_ctrl)
    mem_ctrl   = MemberController(Session, window.member_view)
    report_ctrl = ReportController(Session, window.report_view)
    # 5) 启动
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
