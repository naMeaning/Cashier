from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QComboBox, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem
)
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
from PySide6.QtGui     import QPixmap
from PySide6.QtCore    import Qt
from PySide6.QtWidgets import QHeaderView

class PaymentView(QWidget):
    """
    支付处理模块的视图：  
     - 左侧展示购物车列表  
     - 右侧选择支付方式、输入金额/扫码、确认付款并显示找零
    """
    # 当用户点击“确认付款”时，发出 (pay_type:str, amount:float)   
    # checkout_requested = Signal(str,float)
    checkout_requested = Signal(str, float, object)
    # 当需要清空购物车或移除某项时也可发信号（可选扩展）
    # clear_cart = Signal()

    def __init__(self):
        super().__init__()

        # 整体横向布局：左-购物车；右-结算
        main_layout = QHBoxLayout(self)
        left = QVBoxLayout()
        left.addWidget(QLabel('购物车'))

        # 创建一个 5 列的表格：图片、名称、单价、数量、小计
        self.cart_table = QTableWidget(0, 5)
        self.cart_table.setHorizontalHeaderLabels(
            ["图片", "名称", "单价", "数量", "小计"]
        )
        # 让列宽自适应内容
        self.cart_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.Stretch
        )

        left.addWidget(self.cart_table)
        main_layout.addLayout(left, 2)

       
        
        # 右侧 结算区

        right = QVBoxLayout()

        # 总额显示
        self.total_label = QLabel('总额:¥0.00')
        right.addWidget(self.total_label)

        # 支付方式下拉
        right.addWidget(QLabel('支付方式'))
        self.method_box = QComboBox()
        self.method_box.addItems(['现金','移动支付','积分','储值卡'])
        right.addWidget(self.method_box)
        
        # —— 会员选择下拉 —— 
        right.addWidget(QLabel("选择会员"))
        self.member_box = QComboBox()
        self.member_box.addItem("非会员", None)   # data=None
        right.addWidget(self.member_box)

        # 金额/扫码输入
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText('输入现金金额或扫码结果')
        right.addWidget(self.input_line)

        # 确认付款按钮
        btn_pay = QPushButton('确认付款')
        # 点击时内部调用 ——onpay_clicked 再发checkout_requested信号
        btn_pay.clicked.connect(self._on_pay_clicked)
        right.addWidget(btn_pay)

         # 找零显示
        self.change_label = QLabel("找零：￥0.00")
        right.addWidget(self.change_label)

        main_layout.addLayout(right, 1)  # 权重 1
        
        
    def update_cart(self, cart_items):
        """
        cart_items: List of tuples (pid, image_path, name, price, qty, subtotal)
        """
        self.cart_table.setRowCount(len(cart_items))
        for row, (pid, img, name, price, qty, subtotal) in enumerate(cart_items):
            # 1) 图片单元格：用 QLabel + QPixmap
            lbl = QLabel()
            pix = QPixmap(img)
            if not pix.isNull():
                pix = pix.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                lbl.setPixmap(pix)
            self.cart_table.setCellWidget(row, 0, lbl)

            # 2) 名称
            self.cart_table.setItem(row, 1, QTableWidgetItem(name))

            # 3) 单价
            self.cart_table.setItem(row, 2, QTableWidgetItem(f"￥{price:.2f}"))

            # 4) 数量
            self.cart_table.setItem(row, 3, QTableWidgetItem(str(qty)))

            # 5) 小计
            self.cart_table.setItem(row, 4, QTableWidgetItem(f"￥{subtotal:.2f}"))


    def update_total(self,total:float):
        """刷新总额标签"""
        self.total_label.setText(f"总额：￥{total:.2f}")
        
    def show_change(self,change:float):
        """展示找零金额"""
        self.change_label.setText(f"找零：￥{change:.2f}")
    
    def _on_pay_clicked(self):
        """内部槽：读取当前支付方式 & 用户输入，发出 checkout_requested 信号"""
        pay_type = self.method_box.currentText()
        text = self.input_line.text().strip()
        try:
             amt = float(text)
        except ValueError:
            amt = 0.0
        

        member_id = self.member_box.currentData()
        self.checkout_requested.emit(pay_type, amt, member_id)
    
    def init_members(self, members):
        """
        填充会员下拉列表
        :param members: List of ORM Member 对象
        """
        self.member_box.clear()
        self.member_box.addItem("非会员", None)
        for m in members:
            # 下拉项显示“姓名(ID)”；data 存 member.id
            self.member_box.addItem(f"{m.name}（ID:{m.id}）", m.id)

    
        
        
