# seed_products.py

import os
from models.database      import init_db, Base
from models.product_model import Product

def seed():
    # 1) 初始化数据库（如果第一次运行会自动建表）
    Session = init_db()
    session = Session()

    # 2) 清空 products 表（无需 engine）
    session.query(Product).delete()
    session.commit()

    # 3) 准备要插入的商品，图片路径相对于项目根
    products = [
        Product(name="可乐",     price=3.5,  stock=100,
                image=os.path.join("resources","images","cola.png")),
        Product(name="牛奶",     price=5.0,   stock=80,
                image=os.path.join("resources","images","milk.png")),
        Product(name="奶昔",     price=6.0,   stock=40,
                image=os.path.join("resources","images","milkshake.png")),
        Product(name="面包",     price=4.5,   stock=50,
                image=os.path.join("resources","images","bread.png")),
        Product(name="奶酪",     price=8.0,   stock=30,
                image=os.path.join("resources","images","cheese.png")),
        Product(name="矿泉水",   price=2.0,  stock=200,
                image=os.path.join("resources","images","bottle.png")),
        Product(name="婴儿奶瓶", price=15.0,  stock=20,
                image=os.path.join("resources","images","baby_bottle.png")),
        Product(name="蓝莓", price=20.0,  stock=30,
                image=os.path.join("resources","images","blueberry.png")),
    ]

    # 4) 批量插入
    session.add_all(products)
    session.commit()

    # 5) 打印确认（此时 session 还没 close，ORM 实例仍然有效）
    print("✅ 已清空并插入测试商品：", [p.name for p in products])

    # 6) 关闭会话
    session.close()


if __name__ == "__main__":
    seed()
