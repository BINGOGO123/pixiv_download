# 校正数据库，删除无效条目，改正错误条目
# 默认输出"check.txt"

import importlib
from config import base_config
import os
from tool.tool import get_md5
import sys

config = base_config[__name__]["check"]
# 数据库连接信息
config_database = base_config["spider"]["database"]

if __name__ == "__main__":
  if len(sys.argv) >= 2:
    config["output"] = sys.argv[1]
  print("config = {}\nconfig_database = {}".format(config, config_database))
  package_name = "database.{}".format(config_database["type"])
  db = importlib.import_module(package_name)
  database = db.Db(**config_database[config_database["type"]])
  sql = "select storage_path,url,md5 from file"
  ret = database.execute(sql)
  record = open(config["output"], "w", encoding="utf8")
  record.write("config = {}\nconfig_database = {}\n\n".format(config, config_database))
  for one in ret:
    storage_path, url, md5 = one
    if not os.path.exists(storage_path):
      record.write("[FileNotFoud]\nstorage_path={}\nurl={}\nmd5={}\n\n".format(storage_path, url, md5))
      if config["revise"]:
        database.escape_execute("delete from file where storage_path = {}", storage_path)
    else:
      with open(storage_path, "rb") as f:
        content = f.read()
      new_md5 = get_md5(content)
      if new_md5 == md5:
        record.write("[Correct]\nstorage_path={}\nurl={}\nmd5={}\n\n".format(storage_path, url, md5))
      else: 
        record.write("[Md5NotMatch]\nstorage_path={}\nurl={}\nmd5={}\nnew_md5={}\n\n".format(storage_path, url, md5, new_md5))
        if config["revise"]:
          database.escape_execute("update file set md5 = {} where storage_path = {}", new_md5, storage_path)
  record.close()
