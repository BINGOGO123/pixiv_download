# 主函数

from spider.Spider import Spider
import sys
import os
from config import base_config
from tool.tool import create_shortcut, del_file

config = base_config[__name__]["main"]

if __name__ == "__main__":
  if len(sys.argv) < 2:
    if config.get("download_list") != None:
      print("config = {}".format(config))
      spider = Spider()
      for item in config["download_list"]:
        if type(item) == dict:
          url = item.get("url")
          if url == None:
            print("下载项[{}]没有url项，跳过\n".format(item))
            continue
        elif type(item) == str:
          url = item
        else:
          print("下载项[{}]格式错误，跳过\n".format(item))
          continue
        spider.download(url)
    else:
      print("请输入url")
      exit()
  else:
    spider = Spider()
    spider.download(sys.argv[1])

  # 对本次下载新增的文件进行处理
  if config.get("print_new_file") == True or config.get("save_new_file") == True:
    ret = spider.get_new_files()
    if ret != False and ret != None: 
      # 将新增加的文件的快捷方式放于target目录中
      if config.get("save_new_file") == True and config.get("save_as") != None and config.get("save_as") != False:
        target = os.path.abspath(config.get("save_as"))
        save_path = os.path.join(target, str(spider.get_start_time().date()))
        # 如果说该文件夹已经存在，那么就在最末级文件夹后面加上-数字作为后缀
        if os.path.exists(save_path):
          order = 1
          while os.path.exists("{}-{}".format(save_path, order)):
            order += 1
          save_path = "{}-{}".format(save_path, order)
        os.makedirs(save_path)
        print("\n本次下载新增文件可见文件夹：{}".format(save_path))
        for i in range(len(ret)):
          # 如果快捷文件的名称已经存在那么就通过后缀的方式更改名称
          shortcut = os.path.join(save_path, os.path.split(ret[i][0])[-1])
          if os.path.exists(shortcut + ".lnk"):
            order = 1
            while os.path.exists("{}_{}.lnk".format(shortcut, order)):
              order += 1
            shortcut = "{}_{}.lnk".format(shortcut, order)
          else:
            shortcut += ".lnk"
          create_shortcut(ret[i][0], shortcut)

      # 输出新增加的文件，这里获取到了storage_path和url但是没必要输出url，只需要输出storage_path即可，多了反而显得凌乱
      if config.get("print_new_file") == True:
        if not (config.get("save_as") != None and config.get("save_as") != False):
          print("\n本次下载新增文件：")
        for i in range(len(ret)):
          print("{}. {}".format(i + 1, ret[i][0]))
