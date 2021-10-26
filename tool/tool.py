import logging
import os
import datetime
import hashlib
import pythoncom
import copy
from win32com.shell import shell

def cover(o1, o2):
  """
  o1和o2是dict，用o2覆盖o1中的值

  对于o2和o1键相同且值均为dict类型的情况，递归调用cover处理
  """
  for key in o2:
    if type(o2.get(key)) == dict and type(o1.get(key)) == dict:
      cover(o1[key], o2[key])
    # 这里一定要copy，否则如果o2[key]也是对象，o1[key]会直接指向o2[key]
    else:
      o1[key] = copy.deepcopy(o2[key])

# 用在spider.Spider和check中
def get_md5(data:bytes):
  """
  计算md5摘要
  """
  md5 = hashlib.md5()
  md5.update(data)
  return md5.hexdigest()

# 暂时没有用这里的这个方法，因为每个模块的日志格式可能不一样，所以应该各自可以高度自定义自己的日志格式，不应该用统一的模板
def initialLogger(logger, name, logs_dir, logger_level, file_level, stream_level):
  """
  格式化日志对象
  """
  # 如果不存在logs文件夹则创建
  if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)
  handler1 = logging.FileHandler(os.path.join(logs_dir, name + "." + str(datetime.date.today()) + ".log"),"a",encoding="utf8")
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

# 这个方法目前尚未使用，因为用到的地方比较少，而且简化的代码量有限
def get_config(base_config, *args):
  """
  从base_config中获取层级为args:list的项，即base_config的子config

  如果从base_config无法到达args:list子项则返回None
  """
  if len(args) == 0:
    return base_config
  if type(base_config) != dict:
    return None
  else:
    return get_config(base_config.get(args[0]), *args[1:])

def create_shortcut(source, lnkname):
  """
  建立source到lnkname的快捷方式，若lnkname不是.lnk格式会在最后加上.lnk

  该方法可能会抛出异常
  """
  shortcut = pythoncom.CoCreateInstance(shell.CLSID_ShellLink, None, pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)
  shortcut.SetPath(source)
  if os.path.splitext(lnkname)[-1] != '.lnk':
    lnkname += ".lnk"
  shortcut.QueryInterface(pythoncom.IID_IPersistFile).Save(lnkname, 0)

def del_file(path):
  """
  删除path目录及path目录下的所有内容
  """
  ls = os.listdir(path)
  for i in ls:
    c_path = os.path.join(path, i)
    if os.path.isdir(c_path):
      del_file(c_path)
    else:
      os.remove(c_path)
  os.rmdir(path)

def setDict(d, params, val):
  """
  d是一个字典或者列表，params是一个列表，通过params修改d中对应项的值为val
  """
  index = "".join([f"[params[{i}]]" for i in range(len(params))])
  exec(f"d{index} = val")

def getDict(d, params):
  """
  d是一个字典或者列表，params是一个列表，通过params获取d中对应项的值
  """
  result = d
  for item in params:
    result = result[item]
  return result
