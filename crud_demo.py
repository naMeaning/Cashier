# crud_demo.py
from models.database import init_db
from models.product_model import Product
from models.member_model import Member
from models.transaction_model import Transaction
import datetime

# 初始化并获取会话
Session = init_db()
session = Session()

print("=== Product CRUD ===")

# 2. 查询
all_prods = Product.get_all(session)
print("所有商品：", [(x.id, x.name, x.price, x.stock) for x in all_prods])

session.close()
