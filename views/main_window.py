from PySide6.QtWidgets import (
    QMainWindow,QTableWidget,QWidget,QVBoxLayout,QLabel,QTabWidget
    )

# # 下面这几行会在后续写对应文件时用到
from .product_view import ProductView
from .payment_view import PaymentView
from .inventory_view import InventoryView
from .member_view import MemberView
from .report_view import ReportView

class MainWindow(QMainWindow):
    """
    主窗口：包含一个 Tab 控件，预留 5 个标签页（模块）。
    这里先用占位页（QWidget + QLabel）来跑通框架，后面再替换成真正的 View。

    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("便利店收银系统")

          # 1) 创建一个 QTabWidget
        tabs = QTabWidget()
        self.setCentralWidget(tabs)
        
        # ———— 商品管理，用真实的 ProductView ————
        self.product_view = ProductView()
        self.payment_view = PaymentView()
        self.inventory_view = InventoryView()

        tabs.addTab(self.product_view, "商品管理")
        tabs.addTab(self.payment_view,'支付处理')
        tabs.addTab(self.inventory_view,'库存监控')

        self.member_view = MemberView()
        tabs.addTab(self.member_view, "会员管理")

        self.report_view = ReportView()
        tabs.addTab(self.report_view, "数据分析")
        

     
        
