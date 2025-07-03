from sqlalchemy import Integer,Float,String,Column,DateTime,ForeignKey
from .database import Base
import datetime
import json

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer,primary_key = True,autoincrement = True)
    timestamp = Column(DateTime,default = datetime.datetime.utcnow)
    items_json = Column(String,nullable=False)
    total = Column(Float,nullable=False)
    pay_type = Column(String(50),nullable = False)
    member_id = Column(Integer,ForeignKey('members.id'),nullable=True)

    @classmethod
    def record(cls, session, cart: dict, total: float, pay_type: str, member_id: int = None):
        """
        记录一笔交易
        - cart: {product_id: quantity, …}
        - total: 实付金额
        - pay_type: 支付方式
        - member_id: 可选，会员支付时传入
        """
        tx = cls(
            items_json=json.dumps(cart, ensure_ascii=False),
            total=total,
            pay_type=pay_type,
            member_id=member_id
        )
        session.add(tx)
        session.commit()
        return tx
    
    @classmethod
    def query_by_period(cls, session, start, end):
        """查询指定时间段内的流水"""
        return session.query(cls)\
                      .filter(cls.timestamp >= start, cls.timestamp <= end)\
                      .all()
                      