from PySide6.QtCore import Slot
from models.product_model import Product
#from views.product_view import ProductView

class ProductController:
    """
    ProductController 负责:
    1. 从数据库读取Product数据
    2. 响应视图的搜索请求和点击事件
    3. 把数据穿给productView 让它刷新界面

    """

    def __init__(self,SessionFactory,view):
        """
        :param SessionFactory: 来自 models.database.init_db() 的 sessionmaker
        :param view: ProductView 实例
        """
        self.SessionFactory = SessionFactory
        self.view = view

        # 1) 把 View 发出的信号，绑定到 Controller 的方法上
        # search_requested: 当用户点击“搜索”按钮时，发来关键字
        self.view.search_requested.connect(self.on_search)

        # product_clicked: 当用户点击某个商品图片时，发来该商品的 ID
        self.view.product_clicked.connect(self.on_product_clicked)
        
          # 2) 启动时先载入所有商品
        self.load_products()
    
    def load_products(self):
        """
        从数据库读取所有商品并让 View 显示：
        - 使用 SessionFactory() 创建一个 Session
        - 调用 Product.get_all(session) 拉取数据
        - 关闭 Session 避免连接泄露
        - 调用 view.display_products() 把模型实例传给视图
        """
        
        session = self.SessionFactory()
        try:
            products = Product.get_all(session)
        finally:
            session.close()
        
        # 把查询结果传给View
        self.view.display_products(products)


    @Slot(str)
    def on_search(self,keyword):
        """
        响应用户输入的搜索关键字：
        - 当用户在界面上输入文字并点击“搜索”时触发
        - 使用 Product.filter_by_name(session, keyword) 做模糊查询
        - 结果仍然传给 view.display_products() 刷新网格
        """
        
        session = self.SessionFactory()
        try:
            products = Product.filter_by_name(session,keyword)
        finally:
            session.close()
        
        self.view.display_products(products)
    
    @Slot(int)
    def on_product_clicked(self,product_id):
        """
        响应用户点击某个商品：
        - 这里我们简单打印，后续可以弹对话框做“加入购物车”或“修改价格”
        - product_id 是 ProductView 里 btn.clicked.emit(pid) 发过来的
        """
        print(f"[ProductController] 用户点击了商品 ID={product_id}")
        # TODO: 弹窗询问：加入购物车？编辑价格？……