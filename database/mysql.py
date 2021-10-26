import pymysql
from dbutils.pooled_db import PooledDB
from pymysql.converters import escape_string
from . import config
from . import logger
from tool.tool import cover
from .err import ConnectException
from .AbstractDb import AbstractDb

class Db(AbstractDb):
  def __init__(self, host, port, user, password, db):
    """
    初始化数据库对象，根据传入的参数以及config配置

    若连接失败，抛出database.err.ConnectionException
    """
    logger.debug("Db(host={}, port={}, user={}, password={}, db={})".format(host, port, user, password, db))
    port = int(port)
    db_connect_params = {
      "creator": pymysql,  # 使用链接数据库的模块
      "maxconnections": 6,  # 连接池允许的最大连接数，0和None表示不限制连接数
      "mincached": 2,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
      "maxcached": 5,  # 链接池中最多闲置的链接，0和None不限制
      "maxshared": 1,  # 链接池中最多共享的链接数量，0和None表示全部共享
      "blocking": True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
      "maxusage": None,  # 一个链接最多被重复使用的次数，None表示无限制
      "setsession": [],  # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
      "ping": 0,
      # ping MySQL服务端，检查是否服务可用。
      # 如：0 = None = never,
      # 1 = default = whenever it is requested,
      # 2 = when a cursor is created,
      # 4 = when a query is executed,
      # 7 = always
      "charset": 'utf8mb4' # 4字节编码utf8
    }
    # 根据config配置中的连接配置覆盖
    db_connect_params_config = config.get("db_connect_params") if config.get("db_connect_params") != None else {}
    cover(db_connect_params, db_connect_params_config)
    try:
      self.pool = PooledDB(
        host = host,
        port = port,
        user = user,
        password = password,
        database = db,
        **db_connect_params)
    except pymysql.err.OperationalError as e:
      # 表示数据库能连接，但是库名不存在
      if e.args[0] == 1049 and config.get("create") == True:
        # 在下面处理
        pass
      else:
        logger.exception("连接数据库失败")
        raise ConnectException("连接数据库失败")
    except Exception:
      logger.exception("连接数据库失败")
      raise ConnectException("连接数据库失败")
    else:
      # 没有异常发生
      return

    # 数据库名不存在，且根据配置文件新建数据库
    logger.info("数据库 {} 不存在，创建".format(db))
    try:
      self.pool = PooledDB(
        host = host,
        port = port,
        user = user,
        password = password,
        **db_connect_params)
    except Exception:
      logger.exception("连接数据库失败")
      raise ConnectException("连接数据库失败")
    if self.execute("create database if not exists {}".format(db)) == False:
      logger.error("创建数据库失败")
      raise ConnectException("连接数据库失败")

    # 再次连接
    try:
      self.pool = PooledDB(
        host = host,
        port = port,
        user = user,
        password = password,
        database = db,
        **db_connect_params)
    except Exception:
      logger.exception("连接数据库失败")
      raise ConnectException("连接数据库失败")

  def __del__(self):
    """
    析构对象
    """
    self.pool.close()
    
  def create_conn(self):
    conn = self.pool.connection()
    cursor = conn.cursor()
    return conn, cursor
  
  def close_conn(self, conn, cursor):
    conn.close()
    cursor.close()
  
  def execute(self, sql):
    """
    执行sql语句，正确返回结果，一个元组()，可能为空

    出现异常返回False
    """
    logger.debug("execute(sql={})".format(sql))
    conn, cursor = self.create_conn()
    try:
      cursor.execute(sql)
      conn.commit()
    except:
      logger.exception("execute 执行异常 sql={}".format(sql))
      conn.rollback()
      self.close_conn(conn, cursor)
      return False
    ret = cursor.fetchall()
    logger.debug("execute ret={}".format(str(ret)))
    return ret

  def escape_execute(self, sql, *data):
    """
    data中可能存在'和"和\数据，因为传给mysql之后会在转义一次，因此需要在前面加上\转义

    正确返回结果，一个元组()，可能为空，出现异常返回False
    """
    logger.debug("escape_execute(sql={}, data={}".format(sql, data))
    # 手动组装成sql语句，所以两边需要加上''
    escape_data = ["'{}'".format(escape_string(x)) for x in data]
    escape_sql = sql.format(*escape_data)
    return self.execute(escape_sql)