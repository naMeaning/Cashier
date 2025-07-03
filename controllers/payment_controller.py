from PySide6.QtCore import Slot
from models.product_model import Product
from models.transaction_model import Transaction
from models.member_model import Member
from PySide6.QtWidgets import QMessageBox

class PaymentController:
    """
    PaymentController 负责：
      - 维护购物车数据结构 self.cart: {pid: qty}
      - 响应添加商品、移除商品、结算请求
      - 调用 Model 完成库存更新、交易记录、会员扣款/积分更新
      - 最后调用 View.update_cart/update_total/show_change
    """
    
    def __init__(self, SessionFactory, view, product_controller, member_controller):
        """
        :param SessionFactory: init_db() 返回的 sessionmaker
        :param view: PaymentView 实例
        :param product_controller: ProductController 实例，用于读取和刷新商品管理
        """
        self.SessionFactory = SessionFactory
        self.view = view
        self.product_controller = product_controller
        self.member_ctrl    = member_controller
        
        
        # ——— 拉取所有会员，初始化视图下拉 ———
        session = self.SessionFactory()
        try:
            members = session.query(Member).all()
        finally:
            session.close()
        self.view.init_members(members)

        #购物车 ：pid->数量

        self.cart = {}

        # 1) 监听PaymentView的付款信号
        self.view.checkout_requested.connect(self.on_checkout)

        # 2) 监听ProductView的点击商品的信号，实现 加入购物车
        self.product_controller.view.product_clicked.connect(self.add_to_cart)
        
        # 每次启动先清空并刷新
        self._refresh_view()
    
    def _refresh_view(self):
        """内部方法：根据 self.cart 重算小计和总额，更新 View"""
        session = self.SessionFactory()
        try:
            items = []
            total = 0.0
            for pid,qty in self.cart.items():
                prod = session.get(Product,pid)
                if not prod:
                    continue
                subtotal = prod.price * qty
                items.append((pid,prod.image,prod.name,prod.price,qty,subtotal))
        finally:
            session.close()

        self.view.update_cart(items)
        total = sum(i[5] for i in items)
        self.view.update_total(total)

    @Slot(object)
     # 不限定参数类型，接 pid 或 (pid,qty)
    def add_to_cart(self, pid_or_tuple):
        """
        当收到 product_clicked 信号时：
         - 如果 pid_or_tuple 是单个 int，就当 qty=1
         - 如果是 (pid,qty) 元组，就按照用户输入的 qty
        """
        if isinstance(pid_or_tuple, tuple):
            pid, qty = pid_or_tuple
        else:
            pid, qty = pid_or_tuple, 1
            
            # —— 防错：检查库存 —— 
        session = self.SessionFactory()
        try:
            prod = session.get(Product, pid)
            if prod is None:
                QMessageBox.warning(
                    self.view, "错误", f"商品 ID={pid} 不存在"
                )
                return
            # 已加入购物车的数量
            existing = self.cart.get(pid, 0)
            # 如果总需求量超出库存
            if existing + qty > prod.stock:
                QMessageBox.warning(
                    self.view,
                    "库存不足",
                    f"“{prod.name}” 库存仅剩 {prod.stock} 件，\n"
                    + f"已在购物车 {existing} 件，无法再添加 {qty} 件。"
                )
                return
        finally:
            session.close()
        self.cart[pid] = self.cart.get(pid, 0) + qty
        self._refresh_view()

    @Slot(str, float, object)
    def on_checkout(self, pay_type: str, amount: float, member_id):
        session = self.SessionFactory()
        try:
            # 1) 校验库存并计算总额
            total = 0.0
            for pid, qty in self.cart.items():
                prod = session.get(Product, pid)
                if prod is None:
                    QMessageBox.warning(self.view, "错误", f"商品 ID={pid} 不存在")
                    return
                if qty > prod.stock:
                    QMessageBox.warning(
                        self.view,
                        "库存不足",
                        f"“{prod.name}” 库存仅剩 {prod.stock} 件，购物车有 {qty} 件，无法结算。"
                    )
                    return
                total += prod.price * qty

            # 2) 预计算可得积分
            pts_earned = int(total / 0.1) if member_id is not None else 0

            # 3) 统一取出 member（可能为 None）
            member = None
            if member_id is not None:
                member = session.get(Member, member_id)
                if member is None:
                    QMessageBox.warning(self.view, "错误", "所选会员不存在")
                    return

            change = 0.0

            # 4) 按支付方式处理
            if pay_type == "现金":
                if amount < total:
                    QMessageBox.warning(
                        self.view, "支付失败",
                        f"现金不足！\n应付：￥{total:.2f}，您输入：￥{amount:.2f}"
                    )
                    return
                change = amount - total

            elif pay_type == "移动支付":
                pass  # 模拟成功

            elif pay_type == "积分":
                if member is None:
                    QMessageBox.warning(self.view, "错误", "请选择会员后使用积分支付")
                    return
                pts_needed = int(total / 0.1)
                if member.points < pts_needed:
                    QMessageBox.warning(
                        self.view, "支付失败",
                        f"积分不足！需要：{pts_needed}，您有：{member.points}"
                    )
                    return
                member.consume_points(pts_needed)

            else:  # 储值卡
                if member is None:
                    QMessageBox.warning(self.view, "错误", "请选择会员后使用储值卡支付")
                    return
                if member.balance < total:
                    QMessageBox.warning(
                        self.view, "支付失败",
                        f"余额不足！应付：￥{total:.2f}，余额：￥{member.balance:.2f}"
                    )
                    return
                member.balance -= total

            # 5) 发放积分（仅对有会员且不是积分支付的方式）
            if member is not None and pay_type in ("现金", "移动支付", "储值卡"):
                member.earn_points(pts_earned)

            # 6) 扣库存 & 记录交易
            for pid, qty in self.cart.items():
                prod = session.get(Product, pid)
                prod.change_stock(-qty)
            Transaction.record(session, self.cart, total, pay_type)

            # 7) 提交事务
            session.commit()

        finally:
            session.close()

        # 8) 刷新界面
        self.cart.clear()
        self._refresh_view()
        self.view.show_change(change)
        self.product_controller.load_products()
        self.member_ctrl.load_members()
