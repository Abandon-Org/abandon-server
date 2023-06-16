from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


from config import AbandonConfig

engine = create_engine(AbandonConfig.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(engine)
# 创建对象的基类:
Base = declarative_base()
