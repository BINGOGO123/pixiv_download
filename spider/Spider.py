from json.decoder import JSONDecodeError
import requests
import json
import os
import re
from datetime import datetime
import importlib
from bs4 import BeautifulSoup
from tool.tool import get_md5
from config import base_config
from . import logger
from . import module_name
from .err import InitException, NetworkException, AccountException
import copy
# 这个必须先引入，否则打包时无法通过importlib引入这两个包，目前尚不清楚原因，其他包都可以
from database import mysql, sqlite

# 用以爬虫的配置
# config = base_config["spider"]

class Spider:
  __routes = {
    "bookmarks/artworks": "download_bookmarks_artworks",
    "bookmarks/novels": "download_bookmarks_novels",
    "illustrations": "download_illustrations",
    "novels": "download_novels"
  }
  # 用来将路径中的非法字符替换掉
  __regular = re.compile(r"""[\\/:*?<>"|]""")

  @classmethod
  def getRoutes(cls):
    """
    返回所有可下载的路由类型，组成一个列表
    """
    return list(cls.__routes.keys());

  @classmethod
  def isNovel(cls, route: str):
    """
    判断route是小说还是图片，若为小说返回True，否则返回False
    """
    if route in cls.__routes.keys():
      if route.find("novels") < 0:
        return False
      return True
    else:
      raise Exception("不存在[{}]类型".format(route))

  def __init__(self, inform = None):
    """
    初始化spider对象

    若数据库初始化失败，抛出database.err.ConnectionException
    
    出现其他问题导致无法继续，抛出spider.err.InitException
    """
    logger.info("Spider()")
    # 存储一份副本
    self.config = copy.deepcopy(base_config[module_name])
    logger.debug("config = {}".format(self.config))
    # 每一个对象拥有单独的header
    __headers = {
      "cookie": self.config["cookie"],
      "accept": "application/json",
      "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
      # 必须加上下面这一项才能正常下载图片，否则会403forbbiden
      "referer": "https://www.pixiv.net/",
      "sec-ch-ua": '" Not;A Brand";v="99", "Microsoft Edge";v="91", "Chromium";v="91"',
      "sec-ch-ua-mobile": "?0",
      "sec-fetch-dest": "empty",
      "sec-fetch-mode": "cors",
      "sec-fetch-site": "same-origin",
      "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.64",
      # "x-user-id": self.config["your_uid"],
    }
    # 通知选项
    self.inform = inform
    # 创建会话
    self.s = requests.session()
    self.s.headers.update(__headers)
    self.start_time = datetime.now()
    # 根据config选择使用的数据库
    package_name = "database.{}".format(self.config["database"]["type"])
    try:
      db = importlib.import_module(package_name)
    except ModuleNotFoundError:
      logger.exception("模块 {} 不存在".format(package_name))
      raise
    # 这里可能有连接失败的异常，但是我们不需要处理，直接raise即可
    self.database = db.Db(**self.config["database"][self.config["database"]["type"]])
    if self.database.execute("""
      create table if not exists file(
        url varchar(1000) not null,
        storage_path varchar(500) primary key,
        md5 char(32) not null,
        download_time datetime default CURRENT_TIMESTAMP
      );
      """) == False:
      raise InitException("file表创建失败")
    if not os.path.exists(self.config["save_dir_name"]):
      os.makedirs(self.config["save_dir_name"])

  def __del__(self):
    """
    析构对象
    """
    self.s.close()

  def get_response(self, url: str, **kwargs):
    """
    通过http.get获取内容
    """
    logger.debug("get_response(url={}, kwargs={})".format(url, kwargs))
    if kwargs.get("timeout") == None:
      try:
        kwargs["timeout"] = int(self.config["timeout"])
      except ValueError:
        logger.error("{}-timeout参数不合法，使用timeout=5".format(module_name))
        kwargs["timeout"] = 5
    try:
      max_count = int(self.config["request_max_count"])
    except ValueError:
      logger.error("{}-request_max_count参数不合法，使用request_max_count=3".format(module_name))
      max_count = 3
    count = 0
    while True:
      try:
        res = self.s.get(url, **kwargs)
        break
      # 这里不会捕获KeyboardInterrupt
      except Exception:
        count += 1
        logger.exception("第{}次失败".format(count))
        if count == max_count:
          logger.error("达到失败次数上限{} url={}".format(count,url))
          return False
    try:
      res.raise_for_status()
    except Exception:
      logger.exception("请求状态异常")
      return False
    return res

  @staticmethod
  def url_analyze(url: str):
    """
    对url中的关键参数进行分析
    """
    regular = re.compile(r"""https://www\.pixiv\.net/users/(\d+)/([/\w]+)""")
    m = regular.match(url)
    if m:
      return m.group(1), m.group(2)

  @staticmethod
  def url_package(uid: str, route: str):
    """
    将uid和route组装为url
    """
    return "https://www.pixiv.net/users/{}/{}".format(uid, route)
    
  def download(self, url: str):
    """
    根据url进行下载
    """
    logger.info("download(url={})".format(url))
    # 首先分析url是否合法，提取url中的关键参数
    try:
      uid, route = self.url_analyze(url)
    except TypeError:
      logger.error("url不合法")
      return
    if route not in self.__routes:
      logger.error("route错误 route={}".format(route))
      return
    # 然后根据uid和route进行下载
    self.download_by_info(uid, route)

  def download_by_info(self, uid: str, route: str):
    """
    根据uid和route进行下载
    """
    logger.info("download(uid={}, route={})".format(uid, route))
    # 本次下载存储的文件路径
    filepath = os.path.join(self.config["save_dir_name"], uid, route)
    if not os.path.exists(filepath):
      os.makedirs(filepath)
      logger.info("存储路径不存在，创建 path={}".format(filepath))
      self.inform({
        "type": "makedir"
      })
    getattr(self, self.__routes.get(route))(uid, filepath)

  def download_illustrations(self, uid: str, filepath: str):
    """
    下载uid用户创作的插画和漫画
    """
    logger.info("download_illustrations(uid={}, filepath={})".format(uid, filepath))
    # 首先获取这个用户创作的插画和漫画的所有pid列表
    all_url = "https://www.pixiv.net/ajax/user/{}/profile/all?lang=zh".format(uid)
    res = self.get_response(all_url)
    if res == False:
      return
    try:
      result = json.loads(res.text)
    except json.decoder.JSONDecodeError:
      logger.exception("res.text格式化json错误 res.text={}".format(res.text))
      return
    params = ["ids%5B%5D={}".format(x) for x in result["body"]["illusts"]]
    url = "https://www.pixiv.net/ajax/user/{}/profile/illusts?{}&work_category=illust&is_first_page=1&lang=zh"
    # 每组limit个，从offset开始依次获取插画网址的title和pid
    offset, limit, total, successful = 0, 48, len(params), 0
    while offset < total:
      data_url = url.format(uid, "&".join(params[offset : offset + limit]))
      logger.debug("[{}, {})".format(offset, offset + limit))
      offset += limit
      res = self.get_response(data_url)
      if res == False:
        continue
      try:
        result = json.loads(res.text)
      except json.decoder.JSONDecodeError:
        logger.exception("res.text格式化json错误 res.text={}".format(res.text))
        continue
      data = result["body"]["works"]
      for key in data:
        pid = data[key]["id"]
        title = data[key]["title"]
        # 如果这个poster成功了，那么就是总成功数+1
        if self.download_image(pid, title, filepath) != False:
          successful += 1
    logger.info("poster总数={} 下载成功={} 下载失败={}".format(total, successful, total - successful))

  def download_bookmarks_artworks(self, uid: str, filepath: str):
    """
    下载uid用户收藏的插画和漫画
    """
    logger.info("download_bookmarks_artworks(uid={}, filepath={})".format(uid, filepath))
    url = "https://www.pixiv.net/ajax/user/{}/illusts/bookmarks?tag=&offset={}&limit={}&rest=show&lang=zh"
    # 每组limit个，从offset开始依次获取每个poster的pid和title
    offset, limit, successful, order = 0, 48, 0, 1
    while True:
      data_url = url.format(uid, offset, limit)
      logger.debug("[{}, {})".format(offset, offset + limit))
      res = self.get_response(data_url)
      if res == False:
        break
      try:
        result = json.loads(res.text)
      except json.decoder.JSONDecodeError:
        logger.exception("res.text格式化json错误 res.text={}".format(res.text))
        break
      data = result["body"]["works"]
      for poster in data:
        pid = poster["id"]
        title = poster["title"]
        # 如果该poster成功，那么successful+1
        if self.download_image(pid, title, filepath) != False:
          successful += 1
      offset += len(data)
      # 如果本次获取的数据量小于limit，说明后面已经没有了
      if len(data) < limit:
        break
    logger.info("poster总数={} 下载成功={} 下载失败={}".format(offset, successful, offset - successful))
  
  def download_image(self, pid: str, title: str, filepath: str):
    """
    下载一个poster页面的所有图片，下载成功返回True，否则返回False
    
    只要获取图片列表成功即为True
    """
    logger.info("download_image(pid={}, title={}, filepath={})".format(pid, title, filepath))
    # 通知父亲新增图画页面
    if self.inform != None:
      self.inform({
        "type": "gallery",
        "update": False,
        "title": title,
        "url": "https://www.pixiv.net/artworks/{}".format(pid)
      })
    # 获取这个poster页面内的所有图片url
    url = "https://www.pixiv.net/ajax/illust/{}/pages?lang=zh".format(pid)
    res = self.get_response(url)
    if res == False:
      return False
    try:
      result = json.loads(res.text)
    except json.decoder.JSONDecodeError:
      logger.exception("res.text格式化json错误 res.text={}".format(res.text))
      return False
    image_urls = [x["urls"]["original"] for x in result["body"]]

    # 生成文件基础路径
    name = title + "_" + pid
    name = self.__regular.sub("#", name)
    if self.config.get("image_by_folder") == "all" or self.config.get("image_by_folder") == "multiple" and len(image_urls) > 1:
      base_path = os.path.join(filepath, name + "/")
      if not os.path.exists(base_path):
        os.makedirs(base_path)
    else:
      base_path = os.path.join(filepath, name + "_")

    # 依次下载每张图片并存储
    total, successful = len(image_urls), 0
    for i in range(total):
      # 首先生成文件存储路径
      image_url = image_urls[i]
      image_format = image_url.split(".")[-1]
      storage_path = "{}{}.{}".format(base_path, i, image_format)
      # 最终存储时相对路径转换为绝对路径
      storage_path = os.path.abspath(storage_path)
      logger.info("{}. storage_path={} image_url={}".format(i + 1, storage_path, image_url))
      # 通知父亲新增图片
      if self.inform != None:
        self.inform({
          "type": "image",
          "update": False,
          "url": image_url,
          "method": "正在下载",
          "color": "blue"
        })

      # 查询该路径是否下载了该image_url图片
      ret = self.database.escape_execute("select md5 from file where storage_path = {} and url = {}", storage_path, image_url)
      if ret != False and len(ret) > 0 and os.path.exists(storage_path):
        if self.config.get("md5_match") == True:
          if self.compare_md5(storage_path, ret[0][0]) != False:
            logger.info("已存在且md5匹配，跳过")
            successful += 1
            # 通知父亲更新刚才添加的图片
            if self.inform != None:
              self.inform({
                "type": "image",
                "update": True,
                "url": image_url,
                "path": storage_path,
                "method": "已存在"
              })
            continue
        else:
          logger.info("已存在，跳过")
          successful += 1
          # 通知父亲更新刚才添加的图片
          if self.inform != None:
            self.inform({
              "type": "image",
              "update": True,
              "url": image_url,
              "path": storage_path,
              "method": "已存在"
            })
          continue
      # 查询是否可从其他地方搬运，carry为True表示可从其他地方搬运
      carry = False
      self.database.escape_execute("delete from file where storage_path = {}", storage_path)
      ret = self.database.escape_execute("select storage_path,md5 from file where url = {} and storage_path != {}", image_url, storage_path)
      if ret != False:
        for one in ret:
          if self.config.get("md5_match") == True:
            content = self.compare_md5(one[0], one[1])
          else:
            content = self.compare_md5(one[0], "")
          if content != False:
            logger.info("搬运，图片存于{}".format(one[0]))
            carry = True
            break
          else:
            # 此时说明文件不存在或者文件的md5与数据库的md5不吻合
            if self.config.get("clear") == True:
              self.database.escape_execute("delete from file where storage_path = {}", one[0])
        else:
          res = self.get_response(image_url)
          if res == False:
            # 通知父亲更新刚才添加的图片
            if self.inform != None:
              self.inform({
                "type": "image",
                "update": True,
                "url": image_url,
                "method": "下载失败",
                "color": "red"
              })
            continue
          content = res.content
      else:
        res = self.get_response(image_url)
        if res == False:
          # 通知父亲更新刚才添加的图片
          if self.inform != None:
            self.inform({
              "type": "image",
              "update": True,
              "url": image_url,
              "method": "下载失败",
              "color": "red"
            })
          continue
        content = res.content
      # 写入
      try:
        f = open(storage_path, "wb")
        f.write(content)
        f.close()
      except PermissionError:
        logger.exception("文件写入失败")
        # 通知父亲更新刚才添加的图片
        if self.inform != None:
          self.inform({
            "type": "image",
            "update": True,
            "url": image_url,
            "method": "写入失败",
            "color": "red"
          })
        continue
      # 通知父亲更新刚才添加的图片
      if self.inform != None:
        self.inform({
          "type": "image",
          "update": True,
          "url": image_url,
          "path": storage_path,
          "method": "搬运完成" if carry else "下载完成",
          "new": True
        })
      # 由于sqlite3的时区使用的不是本地时区，而mysql和python获取的时间均为本地时区，所以如果使用默认的download_time,会导致时间不一致，这里统一按照python代码获取的时间来存储和查询
      if False != self.database.escape_execute("insert into file (url, storage_path, md5, download_time) values ({}, {}, {}, {})", image_url, storage_path, get_md5(content), datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S")):
        successful += 1
    logger.info("图片总数={} 下载成功={} 下载失败={}".format(total, successful, total - successful))
    return True

  def compare_md5(self, file_name:str, db_md5:str):
    """
    如果文件内容的md5和db_md5相同或者md5为""则返回文件内容
    如果文件不存在或者md5不同则返回False，并且记录日志
    """
    try:
      f = open(file_name, "rb")
      content = f.read()
      f.close()
    except FileNotFoundError:
      logger.debug("文件不存在 file_name={}".format(file_name))
      return False
    if db_md5 == "":
      return content
    file_md5 = get_md5(content)
    ret = file_md5 == db_md5
    if ret == False:
      logger.debug("md5不匹配 file_md5={} db_md5={}".format(file_md5, db_md5))
    return content if ret == True else ret

  def download_bookmarks_novels(self, uid: str, filepath: str):
    """
    下载uid用户收藏的小说

    如果收藏的某篇小说是系列中的一篇，那么会将这个系列整个下载，存放在一个文件夹里面
    """
    logger.info("download_bookmarks_novels(uid={}, filepath={})".format(uid, filepath))
    url = "https://www.pixiv.net/ajax/user/{}/novels/bookmarks?tag=&offset={}&limit={}&rest=show&lang=zh"
    offset, limit, successful = 0, 24, 0
    # 用在存储已经下载过的系列小说ID
    downloaded_series = set()
    while True:
      # 首先下载一批小说列表
      data_url = url.format(uid, offset, limit)
      logger.debug("[{}, {})".format(offset, offset + limit))
      res = self.get_response(data_url)
      if res == False:
        break
      try:
        result = json.loads(res.text)
      except json.decoder.JSONDecodeError:
        logger.exception("res.text格式化json错误 res.text={}".format(res.text))
        break
      data = result["body"]["works"]
      for poster in data:
        # 如果是系列小说会下载该系列中的所有小说
        try:
          seriesId = poster["seriesId"]
          seriesTitle = poster["seriesTitle"]
          logger.info("seriesId={} seriesTitle={}".format(seriesId, seriesTitle))
          successful += 1
          if seriesId in downloaded_series:
            logger.info("该系列在本轮已经下载过，跳过")
            continue
          # 通知父亲新增系列
          if self.inform != None:
            self.inform({
              "type": "series",
              "update": False,
              "title": seriesTitle,
              "url": "https://www.pixiv.net/novel/series/{}".format(seriesId)
            })
          series_data = self.get_series(seriesId)
          series_path = os.path.join(filepath, self.__regular.sub("#", seriesTitle) + "_" + str(seriesId))
          if not os.path.exists(series_path):
            os.makedirs(series_path)
          for pid,title in series_data:
            self.download_novel(pid, title, series_path)
          downloaded_series.add(seriesId)
        except KeyError:
          pid = poster["id"]
          title = poster["title"]
          # 通知父亲新增系列（相当于该系列只有一篇小说）
          if self.inform != None:
            self.inform({
              "type": "series",
              "update": False,
              "title": title,
              "url": "https://www.pixiv.net/novel/show.php?id={}".format(pid)
            })
          if self.download_novel(pid, title, filepath) != False:
            successful += 1
      offset += len(data)
      if len(data) < limit:
        break
    logger.info("poster总数={} 下载成功={} 下载失败={}".format(offset, successful, offset - successful))
  
  def download_novels(self, uid: str, filepath: str):
    """
    下载uid用户创作的小说

    如果收藏的某篇小说是系列中的一篇，那么会将这个系列整个下载，存放在一个文件夹里面
    """
    logger.info("download_novels(uid={}, filepath={})".format(uid, filepath))
    # 首先获取这个用户创作的所有小说pid列表
    all_url = "https://www.pixiv.net/ajax/user/{}/profile/all?lang=zh".format(uid)
    res = self.get_response(all_url)
    if res == False:
      return
    try:
      result = json.loads(res.text)
    except json.decoder.JSONDecodeError:
      logger.exception("res.text格式化json错误 res.text={}".format(res.text))
      return
    params = ["ids%5B%5D={}".format(x) for x in result["body"]["novels"]]
    url = "https://www.pixiv.net/ajax/user/{}/profile/novels?{}&lang=zh"
    # 每组limit个，从offset开始依次获取每篇小说的信息
    offset, limit, total, successful = 0, 24, len(params), 0
    # 用来存储已经下载过的系列小说ID
    downloaded_series = set()
    while offset < total:
      data_url = url.format(uid, "&".join(params[offset : offset + limit]))
      logger.debug("[{}, {})".format(offset, offset + limit))
      offset += limit
      res = self.get_response(data_url)
      if res == False:
        continue
      try:
        result = json.loads(res.text)
      except json.decoder.JSONDecodeError:
        logger.exception("res.text格式化json错误 res.text={}".format(res.text))
        continue
      data = result["body"]["works"]
      for key in data:
        # 如果是系列小说会下载该系列中的所有小说
        try:
          seriesId = data[key]["seriesId"]
          seriesTitle = data[key]["seriesTitle"]
          logger.info("seriesId={} seriesTitle={}".format(seriesId, seriesTitle))
          successful += 1
          if seriesId in downloaded_series:
            logger.info("该系列在本轮已经下载过，跳过")
            continue
          # 通知父亲新增系列
          if self.inform != None:
            self.inform({
              "type": "series",
              "update": False,
              "title": seriesTitle,
              "url": "https://www.pixiv.net/novel/series/{}".format(seriesId)
            })
          series_data = self.get_series(seriesId)
          series_path = os.path.join(filepath, self.__regular.sub("#", seriesTitle) + "_" + str(seriesId))
          if not os.path.exists(series_path):
            os.makedirs(series_path)
          for pid,title in series_data:
            self.download_novel(pid, title, series_path)
          downloaded_series.add(seriesId)
        except KeyError:
          pid = data[key]["id"]
          title = data[key]["title"]
          # 通知父亲新增系列（相当于该系列只有一篇小说）
          if self.inform != None:
            self.inform({
              "type": "series",
              "update": False,
              "title": title,
              "url": "https://www.pixiv.net/novel/show.php?id={}".format(pid)
            })
          if self.download_novel(pid, title, filepath) != False:
            successful += 1
    logger.info("poster总数={} 下载成功={} 下载失败={}".format(total, successful, total - successful))

  def get_series(self, sid: str):
    """
    获取一个系列小说的所有pid和title以列表的形式返回
    """
    logger.info("get_series(sid={})".format(sid))
    url = "https://www.pixiv.net/ajax/novel/series_content/{}?limit={}&last_order={}&order_by=asc&lang=zh"
    ret = []
    offset, limit = 0, 10
    while True:
      data_url = url.format(sid, limit, offset)
      res = self.get_response(data_url)
      if res == False:
        break
      try:
        result = json.loads(res.text)
      except json.decoder.JSONDecodeError:
        logger.exception("res.text格式化json错误 res.text={}".format(res.text))
        break
      data = [[x["id"], x["title"]] for x in result["body"]["seriesContents"]]
      ret += data
      offset += len(data)
      if len(data) < limit:
        break
    return ret

  def download_novel(self, pid, title, filepath):
    """
    下载一篇novel类型的poster内容

    成功返回True，失败返回False
    """
    logger.info("download_novel(pid={}, title={}, filepath={})".format(pid, title, filepath))
    url = "https://www.pixiv.net/novel/show.php?id={}".format(pid)
    # 通知父亲新增小说
    if self.inform != None:
      self.inform({
        "type": "novel",
        "update": False,
        "url": url,
        "method": "正在下载",
        "color": "blue"
      })

    # 生成文件存储路径
    name = title + "_" + pid
    name = self.__regular.sub("#", name)
    storage_path = os.path.join(filepath, name + ".txt")
    # 最终存储时相对路径转换为绝对路径
    storage_path = os.path.abspath(storage_path)
    # 查询该路径是否下载了该url的小说
    ret = self.database.escape_execute("select md5 from file where storage_path = {} and url = {}", storage_path, url)
    if ret != False and len(ret) > 0 and os.path.exists(storage_path):
      if self.config.get("md5_match") == True:
        if self.compare_md5(storage_path, ret[0][0]) != False:
          logger.info("已存在且md5匹配，跳过")
          # 通知父亲更新小说
          if self.inform != None:
            self.inform({
              "type": "novel",
              "update": True,
              "url": url,
              "path": storage_path,
              "method": "已存在"
            })
          return True
      else:
        logger.info("已存在，跳过")
        # 通知父亲更新小说
        if self.inform != None:
          self.inform({
            "type": "novel",
            "update": True,
            "url": url,
            "path": storage_path,
            "method": "已存在"
          })
        return True
    # 查询是否可从其他位置搬运，carry=True表示可以
    carry = False
    self.database.escape_execute("delete from file where storage_path = {}", storage_path)
    ret = self.database.escape_execute("select storage_path,md5 from file where url = {} and storage_path != {}", url, storage_path)
    if ret != False:
      for one in ret:
        if self.config.get("md5_match") == True:
          content = self.compare_md5(one[0], one[1])
        else:
          content = self.compare_md5(one[0], "")
        if content != False:
          logger.info("搬运，文件存于{}".format(one[0]))
          carry = True
          break
        else:
          # 此时说明文件不存在或者文件的md5与数据库的md5不吻合
          if self.config.get("clear") == True:
            self.database.escape_execute("delete from file where storage_path = {}", one[0])
      else:
        res = self.get_response(url)
        content = self.novel_parse(res.text, pid) if res != False else False
        if content == False:
          # 通知父亲更新小说
          if self.inform != None:
            self.inform({
              "type": "novel",
              "update": True,
              "url": url,
              "method": "下载失败",
              "color": "red"
            })
          return False
    else:
      res = self.get_response(url)
      content = self.novel_parse(res.text, pid) if res != False else False
      if content == False:
        # 通知父亲更新小说
        if self.inform != None:
          self.inform({
            "type": "novel",
            "update": True,
            "url": url,
            "method": "下载失败",
            "color": "red"
          })
        return False
    # 写文件存库
    try:
      f = open(storage_path, "wb")
      f.write(content)
      f.close()
    except PermissionError:
      logger.exception("文件写入失败")
      # 通知父亲更新小说
      if self.inform != None:
        self.inform({
          "type": "novel",
          "update": True,
          "url": url,
          "method": "写入失败",
          "color": "red"
        })
      return False
    # 通知父亲更新小说
    if self.inform != None:
      self.inform({
        "type": "novel",
        "update": True,
        "url": url,
        "path": storage_path,
        "method": "搬运完成" if carry else "下载完成",
        "new": True
      })
    # 由于sqlite3的时区使用的不是本地时区，而mysql和python获取的时间均为本地时区，所以如果使用默认的download_time,会导致时间不一致，这里统一按照python代码获取的时间来存储和查询
    if self.database.escape_execute("insert into file (url, storage_path, md5, download_time) values ({}, {}, {}, {})", url, storage_path, get_md5(content), datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S")) == False:
      return False
    return True

  def novel_parse(self, text: str, pid: str):
    """
    对页面进行解析，返回小说的内容
    """
    html = BeautifulSoup(text, "lxml")
    try:
      meta = html.select_one("#meta-preload-data") 
      data = json.loads(meta["content"])
      content = data["novel"][pid]["content"]
    except (JSONDecodeError, TypeError, KeyError, IndexError) :
      logger.exception("解析错误")
      return False
    return content.encode("utf8")

  def get_new_files(self):
    """
    返回最新增加的图片地址和网址
    """
    sql = "select storage_path,url from file where download_time >= {} order by download_time asc"
    ret = self.database.escape_execute(sql, datetime.strftime(self.start_time,"%Y-%m-%d %H:%M:%S"))
    return [] if ret == False else ret

  def get_start_time(self):
    """
    返回Spider对象的建立时间
    """
    return self.start_time

  def test(self):
    """
    测试当前用户是否可用
    """
    logger.info("test()")
    url = "https://www.pixiv.net/ajax/user/extra?lang=zh"
    try:
      timeout = int(self.config["timeout"])
    except ValueError:
      logger.error("{}-timeout参数不合法，使用timeout=5".format(module_name))
      timeout = 5
    try:
      max_count = int(self.config["request_max_count"])
    except ValueError:
      logger.error("{}-request_max_count参数不合法，使用request_max_count=3".format(module_name))
      max_count = 3
    count = 0
    while True:
      try:
        res = self.s.get(url, timeout = timeout)
        break
      # 这里不会捕获KeyboardInterrupt
      except Exception:
        count += 1
        logger.exception("第{}次失败".format(count))
        if count == max_count:
          logger.error("达到失败次数上限{} url={}".format(count,url))
          raise NetworkException("网络异常")
    try:
      res.raise_for_status()
    except Exception:
      logger.exception("请求状态异常")
      raise AccountException("请求状态异常")
    try:
      res.json()
    except Exception:
      logger.exception("请求内容无法解析")
      raise AccountException("请求内容无法JSON解析")
    logger.info("test success")
    return True
