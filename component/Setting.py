# 设置界面

import os
from PyQt6 import QtCore
from PyQt6.QtGui import QFont, QIcon, QKeySequence
from PyQt6.QtWidgets import QCheckBox, QFrame, QHBoxLayout, QLabel, QMessageBox, QPushButton, QScrollArea, QVBoxLayout, QWidget
import copy
import json

from tool.tool import cover, getDict, setDict
from config import base_config, default_config
from .LineEdit import LineEdit
from .CheckBox import CheckBox
from .ComboBox import ComboBox
from .PathSelect import PathSelect
from .ResetButton import ResetButton

class Setting(QFrame):
  # 内部类二次封装
  class SCheckBox(CheckBox):
    def __init__(self, outer, name, params, inform = lambda : 1, *args):
      self.outer = outer
      super().__init__(
        name, 
        getDict(self.outer.base_config, params), 
        lambda val : (self.outer.changeDict(self.outer.base_config, params, val), inform()),
        self.outer.level4, 
        *args
      )
      self.params = params
    def resetDefaultValue(self):
      self.setValue(getDict(default_config, self.params))
    def cancelValue(self):
      self.setValue(getDict(base_config, self.params))

  class SComboBox(ComboBox):
    def __init__(self, outer, name, params, valList, inform = lambda : 1, *args):
      self.outer = outer
      self.params = params
      super().__init__(
        name,
        getDict(self.outer.base_config, params),
        valList,
        lambda val: (self.outer.changeDict(self.outer.base_config, params, val), inform()),
        self.outer.level4,
        *args
      )
    def resetDefaultValue(self):
      self.setValue(getDict(default_config, self.params))
    def cancelValue(self):
      self.setValue(getDict(base_config, self.params))
    
  class SLineEdit(LineEdit):
    def __init__(self, outer, name, params, number = False, letter = False, password = False, inform = lambda : 1, *args):
      self.outer = outer
      self.params = params
      super().__init__(
        name,
        getDict(self.outer.base_config, params),
        lambda val : (self.outer.changeDict(self.outer.base_config, params, val), inform()),
        self.outer.level4,
        number,
        letter,
        password,
        *args
      )
    def resetDefaultValue(self):
      self.setValue(getDict(default_config, self.params))
    def cancelValue(self):
      self.setValue(getDict(base_config, self.params))

  class SPathSelect(PathSelect):
    def __init__(self, outer, name, params, inform = lambda : 1, *args):
      self.outer = outer
      self.params = params
      super().__init__(
        name,
        getDict(self.outer.base_config, params),
        lambda val : (self.outer.changeDict(self.outer.base_config, params, val), inform()),
        self.outer.level4,
        *args
      )
    def resetDefaultValue(self):
      self.setValue(getDict(default_config, self.params))
    def cancelValue(self):
      self.setValue(getDict(base_config, self.params))
    
  class SDatabaseSelect(QWidget):
    def __init__(self, outer, params, *args):
      self.outer = outer
      self.params = params
      super().__init__(*args)

      self.widgets = []

      # sqlite选项卡
      section = {}
      section["title"] = QCheckBox()
      section["title"].setText("sqlite")
      section["title"].setFont(self.outer.level2)
      section["content"] = [
        self.outer.SLineEdit(self.outer, "database", params + ["sqlite", "db"])
      ]
      self.widgets.append(section)

      # mysql选项卡
      section = {}
      section["title"] = QCheckBox()
      section["title"].setText("mysql")
      section["title"].setFont(self.outer.level2)
      section["content"] = [
        self.outer.SLineEdit(self.outer, "host", params + ["mysql", "host"], True, True),
        self.outer.SLineEdit(self.outer, "port", params + ["mysql", "port"], True),
        self.outer.SLineEdit(self.outer, "user", params + ["mysql", "user"], True, True),
        self.outer.SLineEdit(self.outer, "password", params + ["mysql", "password"], True, True, True),
        self.outer.SLineEdit(self.outer, "database", params + ["mysql", "db"], True, True)
      ]
      self.widgets.append(section)

      hbox = QHBoxLayout()
      for section in self.widgets:
        db = QFrame()
        layout_db = QVBoxLayout()
        layout_db.addWidget(section["title"])
        db_sub = QWidget()
        layout_db_sub = QVBoxLayout()
        for item in section["content"]:
          layout_db_sub.addWidget(item)
        layout_db_sub.addStretch(1)
        layout_db_sub.setContentsMargins(0, 0, 0, 0)
        db_sub.setLayout(layout_db_sub)
        layout_db.addWidget(db_sub)
        db.setLayout(layout_db)
        db.setFrameShape(QFrame.Shape.StyledPanel)
        hbox.addWidget(db)
        section["sub"] = db_sub
      hbox.addStretch(1)
      hbox.setSpacing(10)
      hbox.setContentsMargins(0, 0, 0, 0)
      self.setLayout(hbox)

      # 这里注意闭包的特性，同时由于connect会传参，因此需要用val占住第一个参数
      for pos in range(len(self.widgets)):
        self.widgets[pos]["title"].clicked.connect(lambda val, _pos = pos : self.toggleSection(_pos))

      # 将组件状态切换到与self.outer.base_config相同
      self.toggleSectionByText(getDict(self.outer.base_config, params + ["type"]))
    
    # 将选项卡切换到pos位置并更改self.outer.base_config对应项的值
    def toggleSection(self, pos):
      self.outer.changeDict(self.outer.base_config, self.params + ["type"], self.widgets[pos]["title"].text())
      for i in range(len(self.widgets)):
        if i == pos:
          self.widgets[i]["title"].setCheckState(QtCore.Qt.CheckState.Checked)
          self.widgets[i]["sub"].setDisabled(False)
        else:
          self.widgets[i]["title"].setCheckState(QtCore.Qt.CheckState.Unchecked)
          self.widgets[i]["sub"].setDisabled(True)

    # 将选项卡切换到内容为text的位置并更改self.outer.base_config对应项的值
    def toggleSectionByText(self, text):
      self.outer.changeDict(self.outer.base_config, self.params + ["type"], text)
      for section in self.widgets:
        if section["title"].text() == text:
          section["title"].setCheckState(QtCore.Qt.CheckState.Checked)
          section["sub"].setDisabled(False)
        else:
          section["title"].setCheckState(QtCore.Qt.CheckState.Unchecked)
          section["sub"].setDisabled(True)
        
    # 这里直接调用toggleSectionByText来重置，这样即使默认的type不再section选项内也可以重置
    def resetDefaultValue(self):
      self.toggleSectionByText(getDict(default_config, self.params + ["type"]))
      for section in self.widgets:
        for item in section["content"]:
          item.resetDefaultValue()
    # 这里重置选项的方式和上面一样
    def cancelValue(self):
      self.toggleSectionByText(getDict(base_config, self.params + ["type"]))
      for section in self.widgets:
        for item in section["content"]:
          item.cancelValue()

  def changeDict(self, d, params, val):
    setDict(d, params, val)
    self.buttonStateChange()

  def buttonStateChange(self):
    if self.base_config == base_config:
      self.changed = False
      self.saveButton.setDisabled(True)
      self.cancelButton.setDisabled(True)
    else:
      self.changed = True
      self.saveButton.setDisabled(False)
      self.cancelButton.setDisabled(False)

  def __init__(self, *args):
    super().__init__(*args)

    # 对象内部存储设置信息的副本
    self.base_config = copy.deepcopy(base_config)
    # 表示各项设置是否改变过
    self.changed = False

    self.initUI()

  def initUI(self):
    # 字体信息
    self.level1 = QFont("宋体", 14, QFont.Weight.Bold)
    self.level2 = QFont("宋体", 12, QFont.Weight.Bold)
    self.level3 = QFont("宋体", 10, QFont.Weight.Bold)
    self.level4 = QFont("宋体", 10)

    # 功能按钮
    self.saveButton = QPushButton(" 保存")
    self.cancelButton = QPushButton(" 撤销")
    self.resetButton = QPushButton(" 重置")
    # 所有内容信息
    self.content = [
      {
        "title": QLabel("下载设置"),
        "options": 
        [
          Setting.SPathSelect(self, "文件存放位置", ["spider", "save_dir_name"], lambda : scroll_widget.adjustSize()),
          Setting.SLineEdit(self, "请求超时(ms)", ["spider", "timeout"], True),
          Setting.SLineEdit(self, "最大请求次数", ["spider", "request_max_count"], True),
          Setting.SCheckBox(self, "MD5匹配", ["spider", "md5_match"]),
          Setting.SCheckBox(self, "校正数据库", ["spider", "clear"]),
          Setting.SCheckBox(self, "每次下载完成后显示新增文件", ["__main__", "main", "print_new_file"]),
          Setting.SCheckBox(self, "存放新增文件快捷方式", ["__main__", "main", "save_new_file"]),
          Setting.SPathSelect(self, "快捷方式存放位置", ["__main__", "main", "save_as"], lambda : scroll_widget.adjustSize()),
          Setting.SComboBox(self, "图片存放方式", ["spider", "image_by_folder"], self.base_config["spider"]["image_by_folder_options"])
        ]
      }, 
      {
        "title": QLabel("校正设置"),
        "options": 
        [
          Setting.SCheckBox(self, "校正数据库", ["__main__", "check", "revise"])
        ]
      }, 
      {
        "title": QLabel("数据库设置"),
        "options": 
        [
          Setting.SDatabaseSelect(self, ["spider", "database"])
        ]
      }
    ]

    # 设置滚动条中的布局
    layout_scroll = QVBoxLayout()
    for part in self.content:
      # 添加title
      layout_part = QHBoxLayout()
      part["title"].setFont(self.level1)
      layout_part.addWidget(part["title"])
      # 添加重置按钮
      button = ResetButton()
      layout_part.addSpacing(5)
      layout_part.addWidget(button)
      layout_part.addStretch(1)
      layout_scroll.addLayout(layout_part)
      # 添加设置项
      for option in part["options"]:
        layout_scroll.addWidget(option)
      layout_scroll.addSpacing(10)
      # 设置撤销按钮功能，这里闭包的特性一定要注意一下，同时要用val占住第一个位置
      button.clicked.connect(
        # 由于要执行循环，所以用列表推导式来单行实现，实际上并不需要该方法的返回值
        lambda val, _options = part["options"]:
          [one.cancelValue() for one in _options]
      )

    # 设置功能按钮布局
    layout_function = QHBoxLayout()
    self.saveButton.setStyleSheet(
      """
      QPushButton {
        border: none;
        padding: 5px 10px 5px 10px;
        border-top-left-radius: 12px;
        border-bottom-left-radius: 12px;
        background-color: white;
        border-width: 1px;
        border-style: solid;
        border-color: gray;
        border-right: none;
      }
      QPushButton:hover {
        background-color: rgb(200, 200, 200)
      }
      QPushButton:pressed {
        background-color: rgb(150, 150, 150)
      }
      """
    )
    self.cancelButton.setStyleSheet(
      """
      QPushButton {
        border: none;
        padding: 5px 10px 5px 10px;
        background-color: white;
        border-width: 1px;
        border-style: solid;
        border-color: gray;
      }
      QPushButton:hover {
        background-color: rgb(200, 200, 200)
      }
      QPushButton:pressed {
        background-color: rgb(150, 150, 150)
      }
      """
    )
    self.resetButton.setStyleSheet(
      """
      QPushButton {
        border: none;
        padding: 5px 10px 5px 10px;
        background-color: white;
        border-top-right-radius: 12px;
        border-bottom-right-radius: 12px;
        border-width: 1px;
        border-style: solid;
        border-color: gray;
        border-left: none;
      }
      QPushButton:hover {
        background-color: rgb(200, 200, 200)
      }
      QPushButton:pressed {
        background-color: rgb(150, 150, 150)
      }
      """
    )
    self.saveButton.setFixedWidth(100)
    self.cancelButton.setFixedWidth(100)
    self.resetButton.setFixedWidth(100)
    self.saveButton.setFont(self.level3)
    self.cancelButton.setFont(self.level3)
    self.resetButton.setFont(self.level3)
    saveIcon = QIcon("icons/save.svg")
    self.saveButton.setIcon(saveIcon)
    cancelIcon = QIcon("icons/cancel.svg")
    self.cancelButton.setIcon(cancelIcon)
    resetIcon = QIcon("icons/reset.svg")
    self.resetButton.setIcon(resetIcon)
    layout_function.addStretch(1)
    layout_function.addWidget(self.saveButton)
    layout_function.addWidget(self.cancelButton)
    layout_function.addWidget(self.resetButton)
    layout_function.setSpacing(0)

    # 功能设置
    self.saveButton.clicked.connect(lambda val : self.save(False))
    self.cancelButton.clicked.connect(lambda val : self.cancel(True))
    self.resetButton.clicked.connect(lambda val : self.reset(True))

    # 最终布局设置
    layout_final = QVBoxLayout()
    scroll = QScrollArea()
    scroll_widget = QFrame()
    scroll_widget.setLayout(layout_scroll)
    # 设置滚动区域的最小尺寸，因为在父亲上面设置了最小尺寸，所以这里就不用设置了
    # scroll.setMinimumSize(300, 400)
    # scrollarea 作为一个组件，可以设置窗口
    scroll.setWidget(scroll_widget)
    layout_final.addWidget(scroll)
    layout_final.addLayout(layout_function)
    layout_final.setContentsMargins(0, 0, 0, 0)
    self.setLayout(layout_final)
    # 设置边框，因为子组件scroll已经有边框了，所以这里就不用加了
    # self.setFrameShape(QFrame.Shape.StyledPanel)

    # 所有工作完成之后更改一次按钮状态
    self.buttonStateChange()

  # 保存功能
  def save(self, alert = False):
    execute = False
    if alert:
      box = QMessageBox(self)
      box.setText("是否保存修改的设置信息？")
      box.setWindowTitle("Pixiv下载工具")
      yesButton = box.addButton("是(Y)", QMessageBox.ButtonRole.AcceptRole)
      noButton = box.addButton("否(N)", QMessageBox.ButtonRole.RejectRole)
      box.setDefaultButton(yesButton)
      yesButton.setShortcut("Y")
      noButton.setShortcut("N")
      box.setStyleSheet(
        """
        QLabel {
          color: rgb(0, 51, 153);
          font-size: 16px;
        }
        """
      )
      box.exec()
      if box.clickedButton() == yesButton:
        execute = True
    else:
      execute = True
    if execute:
      try:
        f = open(os.path.abspath("config.json"), "w", encoding = "utf8")
        f.write(json.dumps(self.base_config, sort_keys = True, indent = 2))
        f.close()
      except Exception as e:
        box = QMessageBox(self)
        box.setText(f"保存失败: {str(e)}")
        box.setWindowTitle("Pixiv下载工具")
        okButton = box.addButton("好的", QMessageBox.ButtonRole.AcceptRole)
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
        base_config.clear()
        cover(base_config, self.base_config)
        self.buttonStateChange()
        box = QMessageBox(self)
        box.setText(f"配置文件保存成功")
        box.setWindowTitle("Pixiv下载工具")
        okButton = box.addButton("好的", QMessageBox.ButtonRole.AcceptRole)
        box.setDefaultButton(okButton)
        box.setStyleSheet(
          """
          QLabel {
            color: rgb(0, 51, 153);
            font-size: 16px;
          }
          """
        )
        box.exec()
        return True
    else:
      return False

  # 撤销功能
  def cancel(self, alert = True):
    execute = False
    if alert:
      box = QMessageBox(self)
      box.setText("是否撤销当前所有修改？")
      box.setWindowTitle("Pixiv下载工具")
      yesButton = box.addButton("是(Y)", QMessageBox.ButtonRole.AcceptRole)
      noButton = box.addButton("否(N)", QMessageBox.ButtonRole.RejectRole)
      box.setDefaultButton(yesButton)
      yesButton.setShortcut("Y")
      noButton.setShortcut("N")
      box.setStyleSheet(
        """
        QLabel {
          color: rgb(0, 51, 153);
          font-size: 16px;
        }
        """
      )
      box.exec()
      if box.clickedButton() == yesButton:
        execute = True
    else:
      execute = True
    if execute:
      for part in self.content:
        for option in part["options"]:
          option.cancelValue()
      # 讲道理上面已经撤销了所有设置，无需下面的操作了
      # self.base_config = copy.deepcopy(base_config)
      # self.buttonStateChange()
      return True
    else:
      return False

  # 重置功能
  def reset(self, alert = True):
    execute = False
    if alert:
      box = QMessageBox(self)
      box.setText("是否重置所有配置信息？")
      box.setWindowTitle("Pixiv下载工具")
      yesButton = box.addButton("是(Y)", QMessageBox.ButtonRole.AcceptRole)
      noButton = box.addButton("否(N)", QMessageBox.ButtonRole.RejectRole)
      box.setDefaultButton(yesButton)
      yesButton.setShortcut("Y")
      noButton.setShortcut("N")
      box.setStyleSheet(
        """
        QLabel {
          color: rgb(0, 51, 153);
          font-size: 16px;
        }
        """
      )
      box.exec()
      if box.clickedButton() == yesButton:
        execute = True
    else:
      execute = True
    if execute:
      for part in self.content:
        for option in part["options"]:
          option.resetDefaultValue()
      return True
    else:
      return False

  # 获取组件当前是否可以切走
  def canSwitchOut(self):
    return not self.changed
  
  # 尝试切走，成功返回True，失败返回False
  def switchOut(self):
    if self.changed:
      box = QMessageBox(self)
      box.setText("当前修改尚未保存，是否保存？")
      box.setWindowTitle("Pixiv下载工具")
      saveButton = box.addButton("保存(S)", QMessageBox.ButtonRole.AcceptRole)
      cancelButton = box.addButton("不保存(N)", QMessageBox.ButtonRole.DestructiveRole)
      quitButton = box.addButton("取消", QMessageBox.ButtonRole.RejectRole)
      box.setDefaultButton(saveButton)

      saveButton.setShortcut("S")
      cancelButton.setShortcut("N")
      box.setStyleSheet(
        """
        QLabel {
          color: rgb(0, 51, 153);
          font-size: 16px;
        }
        """
      )
      box.exec()
      if box.clickedButton() == saveButton:
        return self.save(False)
      elif box.clickedButton() == cancelButton:
        return self.cancel(False)
      else:
        return False
    else:
      return True
