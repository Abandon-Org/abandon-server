from datetime import datetime

from sqlalchemy import or_, select, func

from src.app.dao.common.mapper import Mapper
from src.app.middleware.my_jwt import AbandonJWT
from src.app.models.user import User
from src.app.utils.log_config import logger
from src.app.models import async_session


class UserDao(Mapper):

    @staticmethod
    async def register_user(username: str, name: str, password: str, email: str):
        """
        :param username: 用户名
        :param name: 姓名
        :param password: 密码
        :param email: 邮箱
        :return:
        """
        try:
            async with async_session() as session:
                async with session.begin():
                    users = await session.execute(
                        select(User).where(or_(User.username == username, User.email == email)))
                    counts = await session.execute(select(func.count(User.id)))
                    if users.scalars().first():
                        raise Exception("用户名或邮箱已存在")
                    # 注册的时候给密码加盐
                    pwd = AbandonJWT.add_salt(password)
                    user = User(username, name, pwd, email)
                    user.last_login_at = datetime.now()
                    session.add(user)
                    await session.flush()
                    session.expunge(user)
                    return user
        except Exception as e:
            logger.error(f"用户注册失败: {str(e)}")
            raise Exception(f"注册失败: {e}")

    @staticmethod
    async def login(username, password):
        """
        :param username:
        :param password:
        :return:
        """
        try:
            pwd = AbandonJWT.add_salt(password)
            async with async_session() as session:
                async with session.begin():
                    # 查询用户名/密码匹配且没有被删除的用户
                    query = await session.execute(
                        select(User).where(or_(User.username == username, User.password == pwd)))
                    user = query.scalars().first()
                    if user is None:
                        raise Exception("用户名或密码错误")
                    if not user.is_valid:
                        # 说明用户被禁用
                        raise Exception("您的账号已被封禁, 请联系管理员")
                    user.last_login_at = datetime.now()
                    await session.flush()
                    session.expunge(user)
                    return user
        except Exception as e:
            logger.error(f"用户{username}登录失败: {str(e)}")
            raise e

    @staticmethod
    async def list_users():
        try:
            async with async_session() as session:
                query = await session.execute(select(User))
                return query.scalars().all()
        except Exception as e:
            logger.error(f"获取用户列表失败: {str(e)}")
            raise Exception("获取用户列表失败")

    @staticmethod
    async def query_user(id: int):
        async with async_session() as session:
            query = await session.execute(select(User).where(User.id == id))
            return query.scalars().first()

    @staticmethod
    async def list_user_touch(*user):
        try:
            if not user:
                return []
            async with async_session() as session:
                query = await session.execute(select(User).where(User.id.in_(user), User.deleted_at == 0))
                return [{"email": q.email, "phone": q.phone} for q in query.scalars().all()]
        except Exception as e:
            logger.error(f"获取用户联系方式失败: {str(e)}")
            raise Exception(f"获取用户联系方式失败: {e}")
