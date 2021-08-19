import json
from json.decoder import JSONDecodeError
from .config import base_config
from tool.tool import cover

try:
  f = open("config.json", "r", encoding = "utf8")
  user_config = json.loads(f.read())
  f.close()
except FileNotFoundError:
  user_config = {}
except JSONDecodeError:
  print("config.json配置文件格式错误")
  exit(-1)

cover(base_config, user_config)