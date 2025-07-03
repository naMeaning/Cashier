from PySide6.QtWidgets import(
    QWidget,QVBoxLayout,QHBoxLayout,QLabel,
    QSpinBox,QPushButton,QTableWidget,QTableWidgetItem,QListWidget,QMessageBox,QGroupBox,
    QHeaderView
)

from PySide6.QtCore import Signal

class InventoryView(QWidget):
    
    # 当用户更改阈值时发出新的 阈值
    threshold_changed = Signal(int)

    increase_requested   = Signal(int, int)  # (product_id, qty)
    decrease_requested   = Signal(int, int)

    def __init__(self):
         # 整体留白和间距
        super().__init__()
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(16)

        # ——— 阈值设置区 ———
        gb_thresh = QGroupBox("库存预警阈值")
        thresh_layout = QHBoxLayout(gb_thresh)
        thresh_layout.addWidget(QLabel("阈值："))
        self.spin_threshold = QSpinBox()
        self.spin_threshold.setRange(1, 1000)
        self.spin_threshold.setValue(5)
        thresh_layout.addWidget(self.spin_threshold)
        btn_update = QPushButton("更新")
        btn_update.clicked.connect(
            lambda: self.threshold_changed.emit(self.spin_threshold.value())
        )
        thresh_layout.addWidget(btn_update)
        thresh_layout.addStretch()
        main_layout.addWidget(gb_thresh)

        # ——— 库存列表区 ———
        gb_table = QGroupBox("库存列表")
        table_layout = QVBoxLayout(gb_table)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["商品ID", "名称", "库存"])
        # 样式优化
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(QHeaderView.Stretch)
        table_layout.addWidget(self.table)
        main_layout.addWidget(gb_table, stretch=3)

        # ——— 库存调整区 ———
        gb_adjust = QGroupBox("库存调整")
        adj_layout = QHBoxLayout(gb_adjust)
        adj_layout.addWidget(QLabel("数量："))
        self.adjust_spin = QSpinBox()
        self.adjust_spin.setRange(1, 1000)
        adj_layout.addWidget(self.adjust_spin)
        btn_inc = QPushButton("增加")
        btn_inc.clicked.connect(self._on_increase_clicked)
        adj_layout.addWidget(btn_inc)
        btn_dec = QPushButton("减少")
        btn_dec.clicked.connect(self._on_decrease_clicked)
        adj_layout.addWidget(btn_dec)
        adj_layout.addStretch()
        main_layout.addWidget(gb_adjust)

        # ——— 预警日志区 ———
        gb_log = QGroupBox("预警日志")
        log_layout = QVBoxLayout(gb_log)
        self.log_list = QListWidget()
        self.log_list.setAlternatingRowColors(True)
        log_layout.addWidget(self.log_list)
        main_layout.addWidget(gb_log, stretch=1)
        
        
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
        self.decrease_requested.emit(pid,qty)
    
    