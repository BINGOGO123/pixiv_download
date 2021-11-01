# 数据库迁移

from config import base_config
import sys
import importlib

config = base_config[__name__]["migrate"]

def get_database(params):
  package_name = "database.{}".format(params["type"])
  db = importlib.import_module(package_name)
  return db.Db(**params[params["type"]])

if __name__ == "__main__":
  if len(sys.argv) > 1:
    config["output"] = sys.argv[1]
  
  print("config = {}".format(config))
  f = open(config["output"], "w", encoding="utf8")
  f.write("config = {}\n\n".format(config))

  try:
    source = get_database(config["source"])
    target = get_database(config["target"])

    # 如果target数据库中没有file表则创建
    if target.execute("""
      create table if not exists file(
        url varchar(1000) not null,
        storage_path varchar(500) primary key,
        md5 char(32) not null,
        download_time datetime default CURRENT_TIMESTAMP
      );
      """) == False:
      print("file表创建失败")
      exit(-1)

    select = "select url,storage_path,md5,download_time from file";
    insert = "insert into file (url,storage_path,md5,download_time) values ({}, {}, {}, {})"

    data = source.execute(select)
    if data == False:
      print("select失败\n")
    else:
      for record in data:
        if target.escape_execute(insert, *record) != False:
          f.write("[Correct]\n")
        else:
          f.write("[Error]\n")
        f.write("storage_path={}\nurl={}\nmd5={}\ndownload_time={}\n\n".format(*record))
  finally:
    f.close()
