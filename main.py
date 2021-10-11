# 主函数

from spider.Spider import Spider
import sys
import os
from config.config import base_config
from tool.tool import create_shortcut, del_file

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
      exit()
  else:
    spider = Spider()
    spider.download(sys.argv[1])

  # 对本次下载新增的文件进行处理
  if config.get("print_new_file") == True or config.get("save_as") != None and config.get("save_as") != False:
    ret = spider.get_new_files()
    if ret != False and ret != None: 
      # 将新增加的文件的快捷方式放于target目录中
      if config.get("save_as") != None and config.get("save_as") != False:
        target = os.path.abspath(config.get("save_as"))
        # 先把上次存储的快捷方式全部删除，再重新创建该文件夹
        if os.path.exists(target):
          del_file(target)
        os.makedirs(target)
        print("\n本次下载新增文件可见文件夹：{}".format(target))
        for i in range(len(ret)):
          create_shortcut(ret[i][0], os.path.join(target, os.path.split(ret[i][0])[-1] + ".lnk"))

      # 输出新增加的文件，这里获取到了storage_path和url但是没必要输出url，只需要输出storage_path即可，多了反而显得凌乱
      if config.get("print_new_file") == True:
        if not (config.get("save_as") != None and config.get("save_as") != False):
          print("\n本次下载新增文件：")
        for i in range(len(ret)):
          print("{}. {}".format(i + 1, ret[i][0]))
