from sqlalchemy import Column,Integer,String,Float
from .database import Base

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer,primary_key=True,autoincrement=True)
    name = Column(String(100),nullable=False)
    price = Column(Float,nullable=False)
    stock = Column(Integer,default= 0 )
    image = Column(String(200)) # 存图片相对路径

    def adjust_price(self,new_price:float):
        self.price = new_price
    
    def change_stock(self,delta:int):
        self.stock += delta

    @classmethod
    def get_all(cls,session):
        return session.query(cls).order_by(cls.id).all()
    
    @classmethod
    def filter_by_name(cls,session,keyword:str):
        """ 按名字模糊查询"""

        return session.query(cls).filter(cls.name.ilike(f'%{keyword}%')).all()
    
    