import hashlib
import jwt
from datetime import timedelta, datetime

from config import AbandonConfig


class AbandonJWT(object):

    @staticmethod
    def get_token(data):
        """
        定义一个静态方法 get_token，用于生成 JWT 令牌
        :param data:
        :return: 过期时间和生成的 JWT 令牌
        """
        # 计算过期时间
        expire = datetime.now() + timedelta(hours=AbandonConfig.EXPIRED_HOUR)
        # 将过期时间加入到输入数据中，并生成新的数据
        new_data = dict({"exp": datetime.utcnow() + timedelta(hours=AbandonConfig.EXPIRED_HOUR)}, **data)
        return int(expire.timestamp()), jwt.encode(new_data, key=AbandonConfig.JWT_KEY, algorithm='HS256')

    @staticmethod
    def parse_token(token):
        """
        定义一个静态方法 parse_token，用于解析 JWT 令牌
        :param token:
        :return: 使用密钥解码 JWT 令牌，并返回解码后的数据
        """
        try:
            return jwt.decode(token, key=AbandonConfig.JWT_KEY, algorithms=["HS256"])
        except Exception:
            raise Exception("登录状态校验失败, 请重新登录")

    @staticmethod
    def add_salt(password):
        """
        定义一个静态方法 add_salt，用于给密码添加盐并进行 MD5 加密
        :param password:
        :return: 加密结果的十六进制
        """
        # 创建一个 MD5 对象
        m = hashlib.md5()
        # 将密码和盐拼接，并将字符串转换为字节串
        bt = f"{password}{AbandonConfig.JWT_SALT}".encode("utf-8")
        m.update(bt)
        return m.hexdigest()


if __name__ == '__main__':
    expire, token = AbandonJWT.get_token({'这是一个usr': 1})
    print(expire, token)
    print(AbandonJWT.parse_token(token))
