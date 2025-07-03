from apscheduler.schedulers.background import BackgroundScheduler
from PySide6.QtCore import Slot
from models.product_model import Product
from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import Signal, Qt
class InventoryController:
    """
    InventoryController 负责：
      - 初始化库存阈值和定时任务
      - 从数据库读取库存数据、刷新表格
      - 定期检查低库存并发预警
      - 响应用户手动更新阈值
    """


    def __init__(self, SessionFactory, view, product_controller):
        
        self.SessionFactory = SessionFactory
        self.view = view
        self.product_controller = product_controller
        # 默认阈值，从视图上读取一次
        self.threshold = view.spin_threshold.value()

        # 绑定阈值更新信号
        self.view.threshold_changed.connect(self.on_threshold_changed)
        # —— 绑定新增/减少库存信号 —— 
        self.view.increase_requested.connect(self.on_increase)
        self.view.decrease_requested.connect(self.on_decrease)

        # 创建后台，每2min检查一次库存
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self.check_stock,'interval',minutes = 2)
        self.scheduler.start()
        # 启动时先加载一次库存表
        self.load_inventory()
        
    def load_inventory(self):
        """
        从数据库读取所有商品库存，然后调用 view.update_inventory。
        """
        session = self.SessionFactory()
        try:
            products = session.query(Product).all()
            rows = [(p.id, p.name,p.stock) for p in products]
        finally:
            session.close()
        self.view.update_inventory(rows)
    
    @Slot(int)
    def on_threshold_changed(self,new_threshold):
        """
        用户手动更新阈值时：保存阈值并立即触发一次检查
        """
        self.threshold = new_threshold
        self.check_stock()
    
    @Slot(int, int)
    def on_increase(self, pid, qty):
        """
        响应“增加库存”：
         - 从 DB 加载对应 Product
         - 调用 prod.change_stock(qty)
         - commit 并刷新界面
        """
        session = self.SessionFactory()
        try:
            prod = session.get(Product, pid)
            if not prod:
                QMessageBox.warning(self.view, "错误", f"商品 ID={pid} 不存在")
                return

            # 2) 执行库存修改
            prod.change_stock(qty)
            # 3) 在 commit 之前，prod.stock 已经更新到内存，取它
            new_stock = prod.stock

            # 4) 提交改动，把 new_stock 写入数据库
            session.commit()
        finally:
            # 5) 关闭会话，prod 会话绑定断开
            session.close()

        # 6) 刷新库存列表
        self.load_inventory()
        self.product_controller.load_products()
        # 7) 弹窗显示结果，使用保存在本地的 new_stock
        QMessageBox.information(
            self.view,
            "操作成功",
            f"“{prod.name}” 增加库存 {qty} 件\n当前库存：{new_stock} 件"
        )

    @Slot(int, int)
    def on_decrease(self, pid, qty):
        """
        响应“减少库存”：
         - 校验不超出库存
         - 调用 prod.change_stock(-qty)
         - commit 并刷新界面
        """
        session = self.SessionFactory()
        try:
            prod = session.get(Product, pid)
            # … 校验 …
            # 先把要显示的属性缓存下来
            name = prod.name
            new_stock = prod.stock - qty

            # 修改库存并提交
            prod.change_stock(-qty)
            session.commit()
        finally:
            session.close()

        # 刷新 UI
        self.load_inventory()
        # 用本地缓存变量，不再访问已过期的 prod
        QMessageBox.information(
            self.view, "成功",
            f"“{name}” 减少库存 {qty} 件\n当前库存：{new_stock} 件"
        )
    
    def check_stock(self):
        """
        定时任务或阈值更新后调用：
        1. 读取所有产品
        2. 筛选出 stock < threshold 的商品
        3. 调用 view.alert_low_stock() 发出预警
        4. 总是刷新表格，保证库存列表最新
        """
        session = self.SessionFactory()
        try:
            products = session.query(Product).all()
            low = [(p.id,p.name,p.stock) for p in products if p.stock < self.threshold]
            rows = [(p.id,p.name,p.stock) for p in products]
        finally:
            session.close()
        
        #1) 刷新库存表
        self.view.update_inventory(rows)
        if low:
            self.view.alert_low_stock(low)
