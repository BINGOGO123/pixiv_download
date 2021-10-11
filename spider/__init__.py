import logging
import os
import datetime
from config.config import base_config

config = base_config[__name__]
logger = logging.getLogger(__name__)

# 初始化日志对象
def initialLogger(logger, name, logs_dir, logger_level, file_level, stream_level):
  # 如果不存在logs文件夹则创建
  if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)
  handler1 = logging.FileHandler(logs_dir + name + "." + str(datetime.date.today()) + ".log","a",encoding="utf8")
  handler2 = logging.StreamHandler()
  formatter1 = logging.Formatter(fmt="%(asctime)s [%(levelname)s] [%(lineno)d] [%(funcName)s] >> %(message)s",datefmt="%Y-%m-%d %H:%M:%S")
  formatter2 = logging.Formatter(fmt = "[%(levelname)s] >> %(message)s")
  handler1.setFormatter(formatter1)
  handler2.setFormatter(formatter2)
  handler1.setLevel(eval(file_level))
  handler2.setLevel(eval(stream_level))
  logger.setLevel(eval(logger_level))
  logger.addHandler(handler1)
  logger.addHandler(handler2)

initialLogger(logger, __name__, **config.get("logs"))
logger.debug("config = {}".format(config))