import time
from datetime import datetime  # 导入datetime类，用于处理日期和时间

from sqlalchemy import or_, select, func  # 导入or_、select和func类/函数，用于构建SQL查询语句

from src.app.dao.common.mapper import Mapper  # 导入Mapper类，用作该类的父类
from src.app.middleware.my_jwt import AbandonJWT  # 导入AbandonJWT类，用于处理JWT认证
from src.app.models.user import User  # 导入User类，用于操作用户数据表
from src.app.utils.log_config import logger  # 导入logger，用于日志记录
from src.app.models import async_session  # 导入async_session，用于操作异步数据库会话


class UserDao(Mapper):  # 定义名为UserDao的类，继承自Mapper类

    @staticmethod
    async def register_user(username: str, name: str, password: str, email: str):
        """
        注册用户
        :param username: 用户名
        :param name: 姓名
        :param password: 密码
        :param email: 邮箱
        :return: 用户对象
        """
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
                    user = User(username, name, pwd, email)
                    user.last_login_at = datetime.now()
                    session.add(user)
                    await session.flush()
                    session.expunge(user)
                    return user  # 返回注册成功的用户对象
        except Exception as e:
            logger.error(f"用户注册失败: {str(e)}")
            raise Exception(f"注册失败: {e}")

    @staticmethod
    async def login(username, password):
        """
        用户登录
        :param username: 用户名
        :param password: 密码
        :return: 用户对象
        """
        try:
            # 将输入的密码加密并赋值给变量pwd
            pwd = AbandonJWT.add_salt(password)
            # aiomysql异步操作数据库
            async with async_session() as session:
                async with session.begin():
                    # 查询用户名/密码匹配且没有被删除的用户
                    # where中的语句意思：数据库中的username与输入的username相等，且数据库中的password与pwd相等
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
                    return user  # 返回登录成功的用户对象
        except Exception as e:
            logger.error(f"用户{username}登录失败: {str(e)}")
            raise e

    @staticmethod
    async def list_users():
        """
        获取用户列表
        :return: 用户列表
        """
        try:
            # aiomysql异步操作数据库
            async with async_session() as session:
                query = await session.execute(select(User))
                return query.scalars().all()  # 返回所有用户对象的列表
        except Exception as e:
            logger.error(f"获取用户列表失败: {str(e)}")
            raise Exception("获取用户列表失败")

    @staticmethod
    async def query_user(id: int):
        """
        查询用户
        :param id: 用户ID
        :return: 用户对象
        """
        async with async_session() as session:
            query = await session.execute(select(User).where(User.id == id))
            return query.scalars().first()  # 返回查询到的用户对象

    @staticmethod
    async def list_user_touch(*user):
        """
        获取用户联系方式列表
        :param user: 用户ID列表
        :return: 用户联系方式列表
        """
        try:
            if not user:
                return []
            async with async_session() as session:
                query = await session.execute(select(User).where(User.id.in_(user)))
                # 返回包含用户邮箱和电话信息的字典列表
                return [{"email": q.email, "phone": q.phone} for q in query.scalars().all()]
        except Exception as e:
            logger.error(f"获取用户联系方式失败: {str(e)}")
            raise Exception(f"获取用户联系方式失败: {e}")

    @staticmethod
    async def delete_user(id: int):
        """
        变更用户的接口，主要用于用户管理页面
        :param id: 被删除用户id
        :return:
        """
        try:
            async with async_session() as session:
                async with session.begin():
                    query = await session.execute(select(User).where(User.id == id))
                    user = query.scalars().first()
                    if not user:
                        raise Exception("该用户不存在, 请检查")
                    user.deleted_at = int(time.time() * 1000)
        except Exception as e:
            logger.error(f"修改用户信息失败: {str(e)}")
            raise Exception(e)