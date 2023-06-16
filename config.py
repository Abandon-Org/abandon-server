# 基础配置类
import os
from urllib import parse


class AbandonConfig(object):
    # 项目根目录
    PATH: str = os.path.dirname(os.path.abspath(__file__))

    # 日志配置信息
    LOG_DIR: str = 'logs'  # 日志存放的目录名称
    LOG_ROTATE: str = '1'  # 日志多久分割一次，单位day
    LOG_SAVE: str = '7'  # 日志留存多久，单位day

    # 服务信息
    SERVER_HOST: str = "127.0.0.1"
    SERVER_PORT: int = 9923

    # MySQL配置信息
    MYSQL_HOST: str = '127.0.0.1'
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = 'root'
    MYSQL_PASSWD: str = 'Yyi22yy@'
    MYSQL_DB: str = 'abandon'

    # sqlalchemy，此处采用parse是因为如果你的密码包含特殊字符，如@:等，会有识别冲突，因此使用parse
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://{}:{}@{}:{}/{}'.format(
        MYSQL_USER, parse.quote_plus(MYSQL_PASSWD), MYSQL_HOST, MYSQL_PORT, MYSQL_DB)


if __name__ == '__main__':
    print(AbandonConfig.LOG_ROTATE)
