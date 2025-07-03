# inspect_db.py
from models.database import init_db
from models.product_model import Product

Session = init_db()
sess = Session()
for p in sess.query(Product).all():
    print(p.id, p.name, p.image)
sess.close()
