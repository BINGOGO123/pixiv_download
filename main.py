# 主函数

from spider.Spider import Spider
import sys
from config.config import base_config

config = base_config[__name__]["main"]

if __name__ == "__main__":
  if len(sys.argv) < 2:
    if config.get("download_list") != None:
      print("config = {}".format(config))
      spider = Spider()
      for url in config["download_list"]:
        spider.download(url)
    else:
      print("请输入url")
  else:
    spider = Spider()
    spider.download(sys.argv[1])