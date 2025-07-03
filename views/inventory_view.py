from PySide6.QtWidgets import(
    QWidget,QVBoxLayout,QHBoxLayout,QLabel,
    QSpinBox,QPushButton,QTableWidget,QTableWidgetItem,QListWidget,QMessageBox,
)

from PySide6.QtCore import Signal

class InventoryView(QWidget):
    
    # 当用户更改阈值时发出新的 阈值
    threshold_changed = Signal(int)

    increase_requested   = Signal(int, int)  # (product_id, qty)
    decrease_requested   = Signal(int, int)

    def __init__(self):
        super().__init__()

        # 整体垂直布局
        main_layout = QVBoxLayout(self)

        # 阈值设置区

        hl = QHBoxLayout()
        hl.addWidget(QLabel('库存预警阈值：'))

        # SPinBox 用于选择阈值

        self.spin_threshold = QSpinBox()
        self.spin_threshold.setRange(1,1000)
        self.spin_threshold.setValue(5) # 默认阈值
        hl.addWidget(self.spin_threshold)

        # 更新按钮
        btn_upgrate = QPushButton('更新阈值')

        # 点击发送信号，把当前阈值传出去

        btn_upgrate.clicked.connect(
            lambda: self.threshold_changed.emit(self.spin_threshold.value())
        )

        hl.addWidget(btn_upgrate)
        main_layout.addLayout(hl)

        
        # 库存列表
        # 用QTableWidget显示每个商品的ID、名称、库存
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["商品ID", "名称", "库存"])
        main_layout.addWidget(self.table, 3)  # 拉伸比例 3
        
         # —— 库存调整区 —— 
        adj_layout = QHBoxLayout()
        adj_layout.addWidget(QLabel("调整数量："))
        self.adjust_spin = QSpinBox()
        self.adjust_spin.setRange(1, 1000)
        adj_layout.addWidget(self.adjust_spin)

        btn_inc = QPushButton("增加库存")
        btn_inc.clicked.connect(self._on_increase_clicked)
        adj_layout.addWidget(btn_inc)

        btn_dec = QPushButton("减少库存")
        btn_dec.clicked.connect(self._on_decrease_clicked)
        adj_layout.addWidget(btn_dec)

        main_layout.addLayout(adj_layout)
        
        # —— 预警日志 —— 
        main_layout.addWidget(QLabel("预警日志"))
        self.log_list = QListWidget()
        main_layout.addWidget(self.log_list, 1)
        
        
    def update_inventory(self, rows):
        """
        用最新的库存数据刷新表格
        :param rows: List of tuples (pid:int, name:str, stock:int)
        """
        self.table.setRowCount(len(rows))
        for i, (pid, name, stock) in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(pid)))
            self.table.setItem(i, 1, QTableWidgetItem(name))
            self.table.setItem(i, 2, QTableWidgetItem(str(stock)))

    def alert_low_stock(self, low_items):
        """
        将每个低库存商品添加到预警日志
        :param low_items: List of tuples (pid:int, name:str, stock:int)
        """
        for pid, name, stock in low_items:
            text = f"[警告] 商品 {pid}-{name} 库存仅剩 {stock} 件！"
            self.log_list.addItem(text)
            
    def get_selected_pid(self):
        """ 
        返回当前选中行的商品ID，若无返回None
        """
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row,0)
        return int(item.text())
    
    def _on_increase_clicked(self):
        pid = self.get_selected_pid()
        if pid is None:
            QMessageBox.warning(self,'错误','请先选择一条商品记录')
            return 
        
        qty = self.adjust_spin.value()
        self.increase_requested.emit(pid,qty)

    def _on_decrease_clicked(self):
        pid = self.get_selected_pid()
        if pid is None:
            QMessageBox.warning(self,'错误','请先选择一条商品记录')
            return 
        qty = self.adjust_spin.value()
        self.decrease_requested()
    
    