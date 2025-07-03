from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,QInputDialog
)
from PySide6.QtCore import Signal

class MemberView(QWidget):
    """
    会员管理界面：
     - 列表展示会员 ID / 姓名 / 余额 / 积分 / 等级
     - 右侧面板执行：充值、积分兑换
    """
    
    # 信号：充值(会员ID, 金额)，积分兑换(会员ID, 积分)
    recharge_requested = Signal(int ,float)
    redeem_requested = Signal(int,int)
    add_requested      = Signal(str)
    

    def __init__(self):
        super().__init__()
        main_layout = QHBoxLayout(self)

        # 左边： 会员列表表格
        left = QVBoxLayout()
        btn_add = QPushButton('新增会员')
        btn_add.clicked.connect(self._on_add_member_clicked)
        left.addWidget(btn_add)

        
        self.table = QTableWidget(0,5)
        self.table.setHorizontalHeaderLabels(['ID','姓名','余额','积分','等级'])
        
        # self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        # main_layout.addWidget(self.table, 3)
        
        left.addWidget(self.table,3)
        main_layout.addLayout(left,3)
        # 右边 ： 操作面板
        ops = QVBoxLayout()
        ops.addWidget(QLabel('操作面板'))

        # 充值区域
        ops.addWidget(QLabel('充值金额: '))
        self.amt_input = QLineEdit()
        self.amt_input.setPlaceholderText('输入充值金额')
        ops.addWidget(self.amt_input)

        btn_recharge = QPushButton('充值')
        btn_recharge.clicked.connect(self._on_recharge_clicked)
        ops.addWidget(btn_recharge)

        # 积分兑换区域
        ops.addWidget(QLabel('积分兑换'))
        self.pt_input = QLineEdit()
        self.pt_input.setPlaceholderText('输入兑换积分')
        ops.addWidget(self.pt_input)
        btn_redeem = QPushButton("兑换")
        btn_redeem.clicked.connect(self._on_redeem_clicked)
        ops.addWidget(btn_redeem)

        ops.addStretch()
        main_layout.addLayout(ops,1)

    def update_members(self,members):
        """
        用最新的会员数据刷新表格
        :param members: List of Member ORM 对象
        """
        
        self.table.setRowCount(len(members))
        for i,m in enumerate(members):
            self.table.setItem(i,0,QTableWidgetItem(str(m.id)))
            self.table.setItem(i,1,QTableWidgetItem(m.name))
            self.table.setItem(i,2,QTableWidgetItem(f'¥{m.balance:.2f}'))
            self.table.setItem(i,3,QTableWidgetItem(str(m.points)))
            self.table.setItem(i,4,QTableWidgetItem(m.level))

    def get_selected_member_id(self):
        """ 
        获取当前选中行的会员的ID，没选择弹窗并返回None
        
        """

        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self,'错误','请先在表格中选中一个会员')
            return None
        return int(self.table.item(row,0).text())

    def _on_recharge_clicked(self):
        """ 
        当用户点击充值按钮时
        1. 获取选中会员ID
        2. 读取金额输入框并转换
        3. 发出 recharge_requested信号

        """

        member_id = self.get_selected_member_id()
        if member_id is None:
            return 
        text = self.amt_input.text().strip()
        try:
            amt = float(text)
        except ValueError:
            QMessageBox.warning(self,'错误','请输入合法的充值金额')
            return 
        self.recharge_requested.emit(member_id,amt)
    
    def _on_redeem_clicked(self):
        """
        槽：用户点击“兑换”按钮时
         - 获取选中会员 ID
         - 读取积分输入框并转换
         - 发出 redeem_requested 信号
        """
        member_id = self.get_selected_member_id()
        if member_id is None:
            return
        text = self.pt_input.text().strip()
        try:
            pts = int(text)
        except ValueError:
            QMessageBox.warning(self, "错误", "请输入合法的积分数量")
            return
        self.redeem_requested.emit(member_id, pts)

    
    def _on_add_member_clicked(self):
        """
        弹出对话框输入新会员姓名，非空时发 add_requested 信号
        """
        name, ok = QInputDialog.getText(self, "新增会员", "请输入会员姓名：")
        if not ok:
            return
        name = name.strip()
        if not name:
            QMessageBox.warning(self, "错误", "会员姓名不能为空")
            return
        # 发给 Controller 去写数据库
        self.add_requested.emit(name)
        
