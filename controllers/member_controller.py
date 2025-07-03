from PySide6.QtCore import Slot
from PySide6.QtWidgets import QMessageBox
from models.member_model import Member

class MemberController:
    """
    MemberController 负责：
      - 从数据库读取会员列表并刷新视图
      - 响应充值和积分兑换请求，调用模型，commit 并刷新视图
    """
    def __init__(self,SessionFactory,view):
        
        self.SessionFactory = SessionFactory
        self.view = view

        # 绑定信号
        self.view.recharge_requested.connect(self.on_recharge)
        self.view.redeem_requested.connect(self.on_redeem)
        self.view.add_requested.connect(self.on_add_member)
        # 初始化加载会员列表
        self.load_members()
    
    @Slot(str)
    def on_add_member(self, name: str):
        """
        收到新增会员请求后：
        1. 在数据库创建 Member(name=name, balance=0, points=0, level="普通会员")
        2. 提交事务
        3. 刷新列表
        4. 弹窗提示新会员ID
        """
        session = self.SessionFactory()
        try:
            # 模型构造，默认余额/积分为 0，等级“普通会员”
            m = Member(name=name, balance=0.0, points=0, level="普通会员")
            session.add(m)
            session.commit()
            new_id = m.id
        finally:
            session.close()

        # 刷新表格显示新会员
        self.load_members()

        # 提示
        QMessageBox.information(
            self.view,
            "新增成功",
            f"已添加新会员：{name}\n会员ID={new_id}"
        )
 
    def load_members(self):
        """
        查询所有会员，调用 view.update_members()
        """
        session = self.SessionFactory()
        try:
            members = session.query(Member).all()
        finally:
            session.close()
        self.view.update_members(members)

    @Slot(int,float)
    def on_recharge(self,member_id:int,amount:float):
        """
        处理充值：
         1. 查询对应 Member 实例
         2. 调用 m.recharge(amount)
         3. commit 并刷新列表
         4. 弹窗告知新的余额
        """
        session = self.SessionFactory()
        try:
            m = session.get(Member,member_id)
            if not m:
                QMessageBox.warning(self.view,'错误','会员不存在')
                return
            m.recharge(amount)
            session.commit()
            new_balance = m.balance
        finally:
            session.close()
        self.load_members()
        QMessageBox.information(
            self.view,'充值成功',
            f'会员【{m.name} 】余额已更新为¥{new_balance:.2f}'
        )

    @Slot(int,int)
    def on_redeem(self,member_id:int,points:int):
        """
        处理积分兑换：
         1. 查询 Member
         2. 检查 m.points >= points，否则警告
         3. 调用 m.consume_points(points)
         4. commit 并刷新
         5. 弹窗告知新的积分 & 余额
        """
        session = self.SessionFactory()
        try:
            m = session.get(Member, member_id)
            if not m:
                QMessageBox.warning(self.view, "错误", "会员不存在")
                return
            if points > m.points:
                QMessageBox.warning(
                    self.view, "错误",
                    f"积分不足！最高可兑换 {m.points} 积分"
                )
                return
            # 假设兑换积分会折抵一定金额，可在模型里定义
            m.consume_points(points)
            session.commit()
            new_points = m.points
            new_balance = m.balance
        finally:
            session.close()

        self.load_members()
        QMessageBox.information(
            self.view, "兑换成功",
            f"会员[{m.name}] 余留积分：{new_points}，余额：￥{new_balance:.2f}"
        )


        

