from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from config import AbandonConfig

engine = create_engine(AbandonConfig.SQLALCHEMY_DATABASE_URI)

Session = sessionmaker(engine)

async_engine = create_async_engine(AbandonConfig.ASYNC_SQLALCHEMY_URI, pool_recycle=1500)
async_session = sessionmaker(async_engine, class_=AsyncSession)
# 创建对象的基类:
Base = declarative_base()
