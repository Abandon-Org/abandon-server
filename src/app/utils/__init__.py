import random
import string


def generate_random_string(length=32):
    # 可以选择的字符集合
    characters = string.ascii_letters + string.digits  # 包括字母和数字
    # 使用随机选择函数生成随机字符串
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string