# 账户界面

from enum import Enum
import os
from PyQt6 import QtCore
from PyQt6.QtCore import QEvent, QRegularExpression, QSize, Qt
from PyQt6.QtGui import QIcon, QRegularExpressionValidator
from PyQt6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout, QWidget
from config import base_config
from spider.Spider import Spider
from spider.err import AccountException, NetworkException
from .Font import Font
from tool.tool import saveJson
import threading
import ctypes

class StateChangeEvent(QEvent):
  """
  账户状态变化，通知主线程进行操作
  """
  idType = QEvent.registerEventType()
  def __init__(self, state):
    super(StateChangeEvent, self).__init__(StateChangeEvent.idType)
    self.state = state

class Account(QFrame):

  class State(Enum):
    NONE = "请输入账户信息"
    OK = "账户可用"
    QUERY = "账户查询中"
    ERROR = "账户不可用"
    NETWORK_ANOMALY = "网络异常"
    UNKNOWN = "账户状态未知"
    SYSTEM_ERROR = "系统异常"

  def timerEvent(self, a0):
    text = self.tip.text()
    count = text.count(".") + 1
    count = count % 4
    text = text.replace(".", "")
    text += (count * ".")
    self.tip.setText(text)


  @property
  def changed(self):
    return self._changed
  @changed.setter
  def changed(self, new_val):
    self._changed = new_val
    if new_val:
      self.saveButton.setDisabled(False)
      self.quitButton.setDisabled(False)
    else:
      self.saveButton.setDisabled(True)
      self.quitButton.setDisabled(True)

  def customEvent(self, e):
    if e.type() == StateChangeEvent.idType:
      self.state = e.state

  @property
  def state(self):
    return self._state
  @state.setter
  def state(self, new_val):
    # 关闭定时器
    self._state = state = new_val
    # 停止计时器
    if self.timeID != None:
      self.killTimer(self.timeID)
      self.timeID = None
    # 设置文字值
    if type(state) == self.State:
      self.tip.setText(state.value)
    else:
      self.tip.setText(state)
    # 设置文字颜色
    if state == self.State.ERROR or state == self.State.NETWORK_ANOMALY:
      self.tip.setStyleSheet(
        """
        color: #d03404;
        """
      )
    elif state == self.State.OK:
      self.tip.setStyleSheet(
        """
        color: green;
        """
      )
    elif state == self.State.NONE or state == self.State.UNKNOWN:
      self.tip.setStyleSheet(
        """
        color: black;
        """
      )
    elif state == self.State.QUERY:
      self.tip.setStyleSheet(
        """
        color: #1296db;
        """
      )
    else:
      self.tip.setStyleSheet(
        """
        color: #d03404;
        """
      )
    if state == Account.State.NONE or state == Account.State.UNKNOWN:
      userIcon = QIcon("icons/user.svg")
    elif state == Account.State.ERROR or state == Account.State.NETWORK_ANOMALY:
      userIcon = QIcon("icons/cry.svg")
    elif state == Account.State.OK:
      userIcon = QIcon("icons/smile.svg")
    elif state == Account.State.QUERY:
      userIcon = QIcon("icons/query.svg")
    else:
      userIcon = QIcon("icons/error.svg")
    self.head.setIcon(userIcon)
    self.head.setIconSize(QSize(180, 180))
    # 设置重新测试按钮是否隐藏
    if state == self.State.NONE or state == self.State.QUERY:
      self.recheck.setHidden(True)
    else:
      self.recheck.setHidden(False)
    # 设置输入可编辑性
    # if state == self.State.QUERY:
    #   self.cookieEdit.setDisabled(True)
    # else:
    #   self.cookieEdit.setDisabled(False)
    # 判断是否开始计时器
    if state == self.State.QUERY:
      self.timeID = self.startTimer(500)
    # 通知父亲状态发生变化
    self.inform(state)
    

  def checkValue(self):
    if self.cookieEdit.text() == base_config["spider"]["cookie"]:
      self.changed = False
    else:
      self.changed = True

  def save(self):
    previous_cookie = base_config["spider"]["cookie"]
    base_config["spider"]["cookie"] = self.cookieEdit.text()
    try:
      saveJson(base_config, os.path.abspath("config.json"))
    except Exception as e:
      # 将base_config还原
      base_config["spider"]["cookie"] =previous_cookie
      box = QMessageBox(self)
      box.setText(f"保存失败: {str(e)}")
      box.setWindowTitle("Pixiv下载工具")
      box.setFont(Font.LEVEL3)
      okButton = box.addButton("好的", QMessageBox.ButtonRole.AcceptRole)
      okButton.setFont(Font.LEVEL4)
      box.setDefaultButton(okButton)
      box.setStyleSheet(
        """
        QLabel {
          color: red;
          font-size: 16px;
        }
        """
      )
      box.exec()
      return False
    else:
      return True
    finally:
      # 更新changed状态
      self.checkValue()
      # 验证账户状态
      self.verifyAccount()

  def quit(self):
    # 因为setText最终会调用checkValue，因此最后无需再次调用
    self.cookieEdit.setText(base_config["spider"]["cookie"])
    return True


  def __init__(self, inform, *args):
    super().__init__(*args)

    # 通知父亲账户状态发生变化
    self.inform = inform

    self.initUI()

    # 记录正在运行的测试线程
    self.test = None
    # 记录定时器ID
    self.timeID = None
    # 表示内容是否改变过
    self.changed = False
    # 记录账户状态
    self.state = self.State.UNKNOWN
    # 验证账户状态
    self.verifyAccount()


  def initUI(self):
    # 头像
    self.head = QPushButton()
    self.head.setStyleSheet(
      """
      border: none;
      """
    )
   
    # 账户状态
    self.tip = QLabel()
    self.tip.setFont(Font.LEVEL2)
    self.recheck = QPushButton()
    self.recheck.setIcon(QIcon("icons/recheck.svg"))
    self.recheck.setIconSize(QtCore.QSize(16, 16))
    self.recheck.setStyleSheet(
      """
      QPushButton {
        border: none;
        padding: 4px; 
        border-radius: 11px;
        background-color: white;
      }
      QPushButton:hover {
        background-color: rgb(200, 200, 200);
      }
      QPushButton:pressed {
        background-color:rgb(150, 150, 150);
      }
      """
    )
    self.recheck.setFixedSize(22, 22)
    # self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
    self.recheck.setToolTip("重新验证账户信息")
    self.recheck.clicked.connect(self.verifyAccount)

    # 内容输入
    cookie = QLabel("COOKIE")
    cookie.setFont(Font.ENGLISH_LEVEL4)
    self.cookieEdit = QLineEdit(base_config["spider"]["cookie"])
    # 不以空格开头
    self.cookieEdit.setValidator(QRegularExpressionValidator(QRegularExpression('^\\S.*$')))
    self.cookieEdit.setFixedWidth(200)
    cookie.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.cookieEdit.setFont(Font.ENGLISH_LEVEL4)
    self.cookieEdit.setStyleSheet(
      """
      QLineEdit {
        background-color: rgb(240, 240, 240);
        padding: 3px 7px 3px 7px;
        border: none;
        border-width: 1px;
        border-style: solid;
        border-color: rgb(240, 240, 240);
        margin-right:5px;
      }
      QLineEdit:focus {
        background-color: white;
        border-width: 1px;
        border-style: solid;
        border-color: gray;
        border-color: rgb(200, 200, 200);
      }
      """
    )
    self.cookieEdit.textChanged.connect(self.checkValue)

    # 按钮
    self.saveButton = QPushButton(" 保存")
    self.quitButton = QPushButton(" 放弃")
    self.saveButton.setFont(Font.LEVEL4)
    self.quitButton.setFont(Font.LEVEL4)
    saveIcon = QIcon("icons/save.svg")
    self.saveButton.setIcon(saveIcon)
    quitIcon = QIcon("icons/cancel.svg")
    self.quitButton.setIcon(quitIcon)
    self.saveButton.setFixedWidth(100)
    self.quitButton.setFixedWidth(100)
    self.saveButton.setStyleSheet(
      """
      QPushButton {
        border: none;
        border-radius: 8px;
        background-color: rgb(220, 230, 240);
        padding: 7px 10px 7px 10px;
      }
      QPushButton:hover {
        background-color: rgb(200, 220, 240);
      }
      QPushButton:pressed {
        background-color: rgb(180, 210, 240);
      }
      """
    )
    self.quitButton.setStyleSheet(
      """
      QPushButton {
        border: none;
        border-radius: 8px;
        background-color: rgb(240, 220, 220);
        padding: 7px 10px 7px 10px;
      }
      QPushButton:hover {
        background-color: rgb(240, 200, 200);
      }
      QPushButton:pressed {
        background-color: rgb(240, 180, 180);
      }
      """
    )
    self.saveButton.clicked.connect(self.save)
    self.quitButton.clicked.connect(self.quit)

    # 布局设置
    headHbox = QHBoxLayout()
    headHbox.addStretch(1)
    headHbox.addWidget(self.head)
    headHbox.addStretch(1)
    tipHbox = QHBoxLayout()
    tipHbox.addStretch(1)
    tipHbox.addWidget(self.tip)
    tipHbox.addWidget(self.recheck)
    tipHbox.addStretch(1)
    tipHbox.setContentsMargins(0, 0, 0, 0)
    tipWidget = QWidget()
    tipWidget.setLayout(tipHbox)
    tipWidget.setFixedHeight(28)
    tipWidget.setContentsMargins(0, 0, 0, 0)
    gridHbox = QHBoxLayout()
    grid = QGridLayout()
    grid.addWidget(cookie, 0, 0)
    grid.addWidget(self.cookieEdit, 0, 1)
    gridHbox.addStretch(1)
    gridHbox.addLayout(grid)
    gridHbox.addStretch(1)
    buttonHbox = QHBoxLayout()
    buttonHbox.addStretch(1)
    buttonHbox.addWidget(self.saveButton)
    buttonHbox.addSpacing(10)
    buttonHbox.addWidget(self.quitButton)
    buttonHbox.addStretch(1)

    layout = QVBoxLayout()
    layout.addStretch(1)
    layout.addLayout(headHbox)
    layout.addSpacing(-10)
    layout.addWidget(tipWidget)
    layout.addSpacing(10)
    layout.addLayout(gridHbox)
    layout.addSpacing(15)
    layout.addLayout(buttonHbox)
    layout.addStretch(1)

    hbox = QHBoxLayout()
    hbox.addStretch(1)
    hbox.addLayout(layout)
    hbox.addStretch(1)
    self.setLayout(hbox)
    self.setContentsMargins(0, 0, 0, 0)

  # 验证账户是否可用
  def verifyAccount(self):
    cookie = base_config["spider"]["cookie"]
    # 终止正在进行的测试线程
    if self.test != None:
      self.test.raise_exception()
    # 开启新的测试线程
    self.test = SpiderTest(self, cookie)
    # 当程序退出时线程终止
    self.test.setDaemon(True)
    self.test.start()

  # 获取组件当前是否可以切走
  def canSwitchOut(self):
    return not self.changed
    
  # 尝试切走，成功返回True，失败返回False
  def switchOut(self):
    if self.changed:
      box = QMessageBox(self)
      box.setText("COOKIE修改后尚未保存，是否保存？")
      box.setWindowTitle("Pixiv下载工具")
      box.setFont(Font.LEVEL3)
      saveButton = box.addButton("保存(S)", QMessageBox.ButtonRole.AcceptRole)
      cancelButton = box.addButton("放弃(N)", QMessageBox.ButtonRole.DestructiveRole)
      quitButton = box.addButton("取消", QMessageBox.ButtonRole.RejectRole)
      saveButton.setFont(Font.LEVEL4)
      cancelButton.setFont(Font.LEVEL4)
      quitButton.setFont(Font.LEVEL4)
      box.setDefaultButton(saveButton)
      saveButton.setShortcut("S")
      cancelButton.setShortcut("N")
      box.setStyleSheet(
        """
        QLabel {
          color: rgb(0, 51, 153);
        }
        """
      )
      box.exec()
      if box.clickedButton() == saveButton:
        return self.save()
      elif box.clickedButton() == cancelButton:
        return self.quit()
      else:
        return False
    else:
      return True


class SpiderTest(threading.Thread):
  def __init__(self, target, cookie):
    threading.Thread.__init__(self)
    self.target = target
    self.cookie = cookie
    self.a = []
  
  def run(self):
    if self.cookie == "":
      QtCore.QCoreApplication.postEvent(self.target, StateChangeEvent(self.target.State.NONE))
    else:
      QtCore.QCoreApplication.postEvent(self.target, StateChangeEvent(self.target.State.QUERY))
      try:
        spider = Spider()
        spider.test()
        QtCore.QCoreApplication.postEvent(self.target, StateChangeEvent(self.target.State.OK))
      except AccountException:
        QtCore.QCoreApplication.postEvent(self.target, StateChangeEvent(self.target.State.ERROR))
      except NetworkException:
        QtCore.QCoreApplication.postEvent(self.target, StateChangeEvent(self.target.State.NETWORK_ANOMALY))
      except Exception as e:
        QtCore.QCoreApplication.postEvent(self.target, StateChangeEvent("系统异常：{}".format(str(e))))

  def get_id(self):
    if hasattr(self, '_thread_id'):
      return self._thread_id
    for id, thread in threading._active.items():
      if thread is self:
        return id

  def raise_exception(self):
    thread_id = self.get_id() 
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit)) 
    if res > 1: 
      ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0) 
      print('Exception raise failure') 
