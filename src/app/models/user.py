from datetime import datetime
# dColumn 用于定义表字段，String 和 INT 分别表示字符串和整数类型，DATETIME 表示日期时间类型
from sqlalchemy import Column, String, INT, DATETIME, Boolean

from src.app.models import Base


class User(Base):
    # 定义表名为 "abandon_user"，表名和类名不必相同，但通常保持一致比较好
    __tablename__ = "abandon_user"

    id = Column(INT, primary_key=True, comment="用户唯一id")
    # 定义字段 id，类型为整数，是主键，注释为 "用户唯一id"
    username = Column(String(16), unique=True, index=True, comment="用户名")
    # 定义字段 username，类型为字符串，长度为 16，唯一且建立索引，注释为 "用户名"
    name = Column(String(16), index=True, comment="姓名")
    # 定义字段 name，类型为字符串，长度为 16，建立索引，注释为 "姓名"
    password = Column(String(32), unique=False, comment="用户密码")
    # 定义字段 password，类型为字符串，长度为 32，不唯一，注释为 "用户密码"
    email = Column(String(64), unique=True, nullable=False, comment="用户邮箱")
    # 定义字段 email，类型为字符串，长度为 64，唯一且不能为空，注释为 "用户邮箱"
    role = Column(INT, default=0, comment="0: 普通用户 1: 组长 2: 超级管理员")
    # 定义字段 role，类型为整数，缺省值为 0，注释为 "0: 普通用户 1: 组长 2: 超级管理员"
    created_at = Column(DATETIME, nullable=False, comment="创建时间")
    # 定义字段 created_at，类型为日期时间，不能为空，注释为 "创建时间"
    updated_at = Column(DATETIME, nullable=False, comment="更改时间")
    # 定义字段 updated_at，类型为日期时间，不能为空，注释为 "更改时间"
    deleted_at = Column(DATETIME, comment="删除时间")
    # 定义字段 deleted_at，类型为日期时间，可为空，注释为 "删除时间"
    last_login_at = Column(DATETIME, comment="上次登录时间")
    # 定义字段 last_login_at，类型为日期时间，可为空，注释为 "上次登录时间"
    avatar = Column(String(128), nullable=True, default=None)
    # 管理员可以禁用某个用户，当他离职后
    is_valid = Column(Boolean, nullable=False, default=True, comment="是否合法")

    def __init__(self, username, name, password, email, is_valid=True):
        self.username = username
        self.password = password
        self.email = email
        self.name = name
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.role = 0
        self.is_valid = is_valid