# seed_products.py

from models.database import init_db
from models.product_model import Product

def seed():
    Session = init_db()
    session = Session()

    products = [
        Product(name="可乐", price=3.5, stock=100, image="resources/images/test.png"),
        Product(name="矿泉水", price=2.0, stock=200, image="resources/images/cola.png"),
        Product(name="面包",   price=4.5, stock=50,  image="resources/images/cola.png"),
        Product(name="牛奶",   price=5.0, stock=80,  image="resources/images/cola.png"),
    ]

    session.add_all(products)
    session.commit()

    # ← 在这里打印，Session 还没 close，ORM 实例仍有效
    print("✅ 已插入测试商品：", [p.name for p in products])

    session.close()

if __name__ == "__main__":
    seed()
