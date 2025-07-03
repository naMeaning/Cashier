from PySide6.QtWidgets import (
    QWidget,QVBoxLayout,QHBoxLayout,QLineEdit,QComboBox,QPushButton,
    QScrollArea,QGridLayout
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QInputDialog

class ProductView(QWidget):
    
    # 用户点击商品图片是发出ID
    # product_clicked = Signal(int)
    # 用户在搜索框点击搜索是发出关键字
    search_requested = Signal(str)
    # 用户点击商品图片时发出 (pid, qty)  或者 pid（兼容老逻辑）
    product_clicked   = Signal(object)
    
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout(self)

        # 顶部：搜索区

        top_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入商品名称...")
        self.category_box = QComboBox()
        self.category_box.addItems(['所有分类','饮料','食品','日用品'])  # 示例？
        btn_search = QPushButton("搜索")
        btn_search.clicked.connect(lambda:self.search_requested.emit(self.search_input.text()))
        top_layout.addWidget(self.search_input)
        top_layout.addWidget(self.category_box)
        top_layout.addWidget(btn_search)
        main_layout.addLayout(top_layout)

        # 中部： 滚动网络

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        self.grid = QGridLayout(container)
        scroll.setWidget(container)
        main_layout.addWidget(scroll,1) #权重1 可拉伸

    def _ask_quantity(self, product_id):
        """
        弹出数量输入框，输入后发出 (product_id, qty)
        """
        qty, ok = QInputDialog.getInt(
            self,              # 父窗口
            "购买数量",         # 对话框标题
            "输入数量：",       # 标签文本
            1,                 # 默认值
            1,                 # 最小可输入
            100                # 最大可输入
        )
        if ok:
            self.product_clicked.emit((product_id, qty))
    
    def display_products(self,products):
        """
        products: 模型对象List
        渲染网格按钮，每行四列
        """

        # 清空就内容
        while self.grid.count():
            w = self.grid.takeAt(0).widget()
            if w:w.deleteLater()

        cols = 4 # 列数
        for idx,p in enumerate(products):
            btn = QPushButton()

            # 显示图片
            btn.setIcon(QIcon(p.image))
            btn.setIconSize(QSize(80,80))
            btn.setFixedSize(100,100)

            # 鼠标悬停提示
            btn.setToolTip(f'{p.name}\n¥{p.price:.2f}\n库存：{p.stock}')

            # 点击发送信号
            btn.clicked.connect(lambda _, pid=p.id: self._ask_quantity(pid))

            r,c = divmod(idx,cols)
            self.grid.addWidget(btn,r,c)

        




