from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base

Base = declarative_base()

def init_db(db_url:str = 'sqlite:///cashier.db'):
    
    # db_url SQLite的文件路径
    engine = create_engine(db_url,echo = True,future = True)
    
    Base.metadata.create_all(engine)

    return sessionmaker(bind=engine,autoflush= False,future = True)

    
