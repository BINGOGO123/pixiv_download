import sqlite3
from config import base_config
from . import module_name
from . import logger
from .AbstractDb import AbstractDb
import copy

class Db(AbstractDb):
  def __init__(self, db):
    """
    一次连接，没用连接池
    """
    logger.debug("Db(db={})".format(db))
    self.config = copy.deepcopy(base_config[module_name])
    logger.debug("config = {}".format(self.config))
    if db.split(".")[-1] != "db":
      db += ".db"
    self.db = sqlite3.connect(db)

  def __del__(self):
    """
    析构对象
    """
    self.db.close()
  
  def execute(self, sql):
    """
    执行sql语句，正确返回结果，一个列表[]，可能为空

    出现异常返回False
    """
    logger.debug("execute(sql={})".format(sql))
    try:
      cur = self.db.cursor()
      cur.execute(sql)
      ret = cur.fetchall()
    except Exception:
      logger.exception("execute 执行异常 sql={}")
      self.db.rollback()
      return False
    else:
      self.db.commit()
      logger.debug("execute ret={}".format(str(ret)))
      return ret
    finally:
      cur.close()

  def escape_execute(self, sql, *data):
    """
    data中可能存在'和"等数据，通过参数化执行sql语句

    正确返回结果，一个列表[]，可能为空，出现异常返回False
    """
    logger.debug("escape_execute(sql={}, data={}".format(sql, data))
    try:
      cur = self.db.cursor()
      sql = sql.format(*(['?'] * len(data)))
      cur.execute(sql, data)
      ret = cur.fetchall()
    except Exception:
      logger.exception("escape_execute 执行异常 sql={} data={}".format(sql, data))
      self.db.rollback()
      return False
    else:
      self.db.commit()
      logger.debug("escape_execute ret={}".format(str(ret)))
      return ret
    finally:
      cur.close()