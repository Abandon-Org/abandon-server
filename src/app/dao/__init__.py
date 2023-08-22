from datetime import datetime

from loguru import logger

from config import AdminConfig
from src.app.middleware.my_jwt import AbandonJWT
from src.app.models import Base, engine, async_session
from src.app.models.user import User
from sqlalchemy import or_, select, func  # 导入or_、select和func类/函数，用于构建SQL查询语句


async def init_user():
    """
    初始化注册用户
    """
    username = AdminConfig.USERNAME
    name = AdminConfig.NAME
    password = AdminConfig.PASSWORD
    email = AdminConfig.EMAIL
    username = AdminConfig.USERNAME
    phone = AdminConfig.PHONE
    role = 2
    try:
        # 采用aiomysql异步操作数据库
        async with async_session() as session:
            async with session.begin():
                # 检查用户名和邮箱是否已存在
                users = await session.execute(
                    select(User).where(or_(User.username == username, User.email == email)))
                counts = await session.execute(select(func.count(User.id)))
                if users.scalars().first():
                    raise Exception("用户名或邮箱已存在")
                # 注册时给密码加盐
                pwd = AbandonJWT.add_salt(password)
                user = User(username, name, pwd, email, phone, role)
                user.last_login_at = datetime.now()
                session.add(user)
                await session.flush()
                session.expunge(user)
                return user  # 返回注册成功的用户对象
    except Exception as e:
        logger.error(f"用户注册失败: {str(e)}")
        raise Exception(f"注册失败: {e}")


Base.metadata.create_all(engine)
init_user()


