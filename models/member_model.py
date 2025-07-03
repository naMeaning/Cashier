from sqlalchemy import Column , Integer , String , Float
from .database import Base

class Member(Base):
    __tablename__ = 'members'

    id = Column(Integer,primary_key=True,autoincrement=True)
    name = Column(String(100),nullable=False)
    balance = Column(Float,default=0.0)
    points = Column(Integer,default= 0 )
    level = Column(Integer,default = 1)


    def recharge(self,amount:float):
        """储值卡充值"""
        if amount < 0:
            raise ValueError("充值金额必须为正")
        
        self.balance += amount
    
    def consume_points(self,pts:int):
        
        """积分消费"""
        if pts > self.points:
            raise ValueError("积分不足")
        
        self.points -= pts

    @property
    def discount_rate(self)->float:
        """根据等级返回折扣率"""
        rates = {1:0.0,2:0.05,3:0.10}
        return rates.get(self.level,0.0)
    
    @classmethod
    def get_all(cls,session):
        return session.query(cls).order_by(cls.id).all()

    def earn_points(self, pts: int):
        """消费后赚取积分"""
        self.points += pts

