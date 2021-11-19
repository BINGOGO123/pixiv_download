# 默认的配置
default_config = {
  "spider": {
    # 路径可以为相对路径或者绝对路径可以用\或者/
    "save_dir_name": "downloaded/",
    # 现在发现这一项不需要，只要有COOKIE就可以了
    # "your_uid": "",
    "cookie": "",
    # 该项字符串必须为数字组成，单位秒
    "timeout": "5",
    # 该项字符串必须为数字组成
    "request_max_count": "5",
    # 在判断数据库信息是否存在时，是否和硬盘中实际文件的md5进行比较
    "md5_match": True,
    # 在数据库查询时是否将无效的条目清除掉
    "clear": True,
    # all表示所有帖子下的图片均存放在单独的文件夹下，multiple表示当一个帖子下有多张图片时才放在单独文件夹下，none表示所有帖子的图片存放在同一个文件夹下面
    "image_by_folder": "multiple",
    # 上面一个配置的所有可选选项
    "image_by_folder_options": ["none", "multiple", "all"],
    # 数据库连接信息，可选mysql或sqlite
    "database": {
      "type": "sqlite",
      "mysql": {
        "host": "localhost",
        # 该项字符串必须为数字组成
        "port": "3306",
        "user": "",
        "password": "",
        "db": ""
      },
      "sqlite": {
        "db": "pixiv_download"
      }
    },
    "logs": {
      # 路径可以为相对路径或者绝对路径可以用\或者/
      "logs_dir": "logs/",
      "logger_level": "logging.DEBUG",
      "file_level": "logging.DEBUG",
      "stream_level": "logging.INFO",
      "level_options": ["logging.DEBUG", "logging.INFO", "logging.WARNING", "logging.ERROR", "logging.CRITICAL"]
    }
  },
  "database": {
    # 当数据库不存在时是否创建，仅对mysql有效，sqlite必然会自动创建
    # 另外当表不存在时都会自动创建
    "create": True,
    "logs": {
      # 路径可以为相对路径或者绝对路径可以用\或者/
      "logs_dir": "logs/",
      "logger_level": "logging.DEBUG",
      "file_level": "logging.DEBUG",
      "stream_level": "logging.INFO",
      "level_options": ["logging.DEBUG", "logging.INFO", "logging.WARNING", "logging.ERROR", "logging.CRITICAL"]
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
      # 是否将新文件快捷方式另外存储
      "save_new_file": True,
      # 新文件快捷方式另外存储的位置
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
      "source": {
        "type": "mysql",
        "mysql": {
          "host": "localhost",
          "port": "3306",
          "user": "",
          "password": "",
          "db": ""
        },
        "sqlite": {
          "db": "pixiv_download"
        }
      },
      # 目标数据库
      "target": {
        "type": "sqlite",
        "mysql": {
          "host": "localhost",
          "port": "3306",
          "user": "",
          "password": "",
          "db": ""
        },
        "sqlite": {
          "db": "pixiv_download"
        }
      },
      # 默认的输出文件
      "output": "migrate.txt"
    }
  }
}