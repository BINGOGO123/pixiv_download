# 默认的配置
base_config = {
  "spider": {
    # 路径可以为相对路径或者绝对路径可以用\或者/但最后一定要有一个\或者/
    "save_dir_name": "downloaded/",
    "your_uid": "",
    "cookie": "",
    "timeout": 20,
    "request_max_count": 5,
    # 在判断数据库信息是否存在时，是否和硬盘中实际文件的md5进行比较
    "md5_match": True,
    # 在数据库查询时是否将无效的条目清除掉
    "clear": True,
    # all表示所有帖子下的图片均存放在单独的文件夹下，multiple表示当一个帖子下有多张图片时才放在单独文件夹下，none表示所有帖子的图片存放在同一个文件夹下面
    "image_by_folder": "multiple",
    # 数据库连接信息，可选mysql或sqlite
    # "database": {
    #   "type": "mysql",
    #   "params": {
    #     "host": "localhost",
    #     "port": 3306,
    #     "user": "",
    #     "password": "",
    #     "db": ""
    #   }
    # },
    "database": {
      "type": "sqlite",
      "params": {
        "db": "pixiv_download"
      }
    },
    "logs": {
      # 路径可以为相对路径或者绝对路径可以用\或者/但最后一定要有一个\或者/
      "logs_dir": "logs/",
      "logger_level": "logging.DEBUG",
      "file_level": "logging.DEBUG",
      "stream_level": "logging.INFO"
    }
  },
  "database": {
    # 当数据库不存在时是否创建，仅对pymysql有效
    "create": True,
    "logs": {
      # 路径可以为相对路径或者绝对路径可以用\或者/但最后一定要有一个\或者/
      "logs_dir": "logs/",
      "logger_level": "logging.DEBUG",
      "file_level": "logging.DEBUG",
      "stream_level": "logging.INFO"
    },
    # pymysql连接数据库的选项可以在这里进行更改
    "db_connect_params":{

    }
  },
  # 这一部分是主函数的配置信息，子键为脚本名称
  "__main__": {
    # 给main.py的配置
    "main": {
      "download_list": [],
      # 是否输出新增加的文件列表
      "print_new_file": True,
      # 将新文件另存到另一个文件夹
      "save_as": "downloaded_latest/"
    },
    # 给check.py的配置
    "check": {
      # 在检查的时候是否校正错误数据（删除无效条目，纠正错误条目）
      "revise": False,
      # 默认的输出文件
      "output": "check.txt"
    },
    # 给migrate.py的配置
    "migrate": {
      # 源数据库
      # "source": {
      #   "type": "mysql",
      #   "params": {
      #     "host": "localhost",
      #     "port": 3306,
      #     "user": "",
      #     "password": "",
      #     "db": ""
      #   }
      # },
      # 目标数据库
      # "target": {
      #   "type": "sqlite",
      #   "params": {
      #     "db": "pixiv_download"
      #   }
      # },
      # 默认的输出文件
      "output": "migrate.txt"
    }
  }
}