import os
from datetime import datetime
from loguru import logger

from config import AbandonConfig


# 初始化日志记录器
def init_logger(log_file_path):
    # 如果日志文件夹不存在，则创建它
    if not os.path.exists(log_file_path):
        os.makedirs(log_file_path)

    # 获取当前时间并根据时间创建日志文件名
    now = datetime.now()
    log_file_name = f"{log_file_path}{now.strftime('%Y-%m-%d_%H')}.log"

    # 添加日志记录器，设置日志文件的轮换和保留策略
    logger.add(log_file_name, rotation=f"{AbandonConfig.LOG_ROTATE} day", retention=f"{AbandonConfig.LOG_SAVE} days",
               enqueue=True)

    # 记录日志，标记日志记录器已初始化
    logger.info("Logger initialized.")


# 调用日志记录器初始化函数并传入日志文件夹路径
init_logger(AbandonConfig.PATH + '/' + AbandonConfig.LOG_DIR + '/')

if __name__ == "__main__":
    pass
