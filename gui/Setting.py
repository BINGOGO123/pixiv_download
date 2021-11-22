# 设置界面

import os
from PyQt6 import QtCore
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import QCheckBox, QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QMessageBox, QPushButton, QScrollArea, QVBoxLayout, QWidget
import copy
from tool.tool import saveJson
from .component.Font import Font

from tool.tool import cover, getDict, setDict
from config import base_config, default_config
from .component.LineEdit import LineEdit
from .component.CheckBox import CheckBox
from .component.ComboBox import ComboBox
from .component.PathSelect import PathSelect
from .component.ResetButton import ResetButton
from . import logger

class Setting(QFrame):
  # 内部类二次封装
  class SCheckBox(CheckBox):
    def __init__(self, outer, name, params, inform = lambda : 1, *args):
      self.outer = outer
      self.params = params
      super().__init__(
        name, 
        getDict(base_config, self.params), 
        lambda val: (self.outer.settingChanged(), inform()),
        Font.LEVEL4,
        *args
      )
    def resetDefaultValue(self):
      self.setValue(getDict(default_config, self.params))
    def cancelValue(self):
      self.setValue(getDict(base_config, self.params))
    # 是否与base_config有差异，应该与save的逻辑相同，即changed()=False则save()无变化，反之changed()=True则save()有变化
    def changed(self):
      if self.getValue() == getDict(base_config, self.params):
        return False
      return True
    def save(self):
      new_value = self.getValue()
      previous_value = getDict(base_config, self.params)
      if new_value != previous_value:
        logger.debug("{}:({})->({})".format(self.params, previous_value, new_value))
        setDict(base_config, self.params, new_value)

  class SComboBox(ComboBox):
    def __init__(self, outer, name, params, valList, inform = lambda : 1, *args):
      self.outer = outer
      self.params = params
      super().__init__(
        name,
        getDict(base_config, self.params),
        valList,
        lambda val: (self.outer.settingChanged(), inform()),
        Font.LEVEL4,
        *args
      )
    def resetDefaultValue(self):
      self.setValue(getDict(default_config, self.params))
    def cancelValue(self):
      self.setValue(getDict(base_config, self.params))
    # 是否与base_config有差异，应该与save的逻辑相同，即changed()=False则save()无变化，反之changed()=True则save()有变化
    def changed(self):
      if self.getValue() == getDict(base_config, self.params):
        return False
      return True
    def save(self):
      new_value = self.getValue()
      previous_value = getDict(base_config, self.params)
      if new_value != previous_value:
        logger.debug("{}:({})->({})".format(self.params, previous_value, new_value))
        setDict(base_config, self.params, new_value)
    
  class SLineEdit(LineEdit):
    def __init__(self, outer, name, params, number = False, letter = False, password = False, inform = lambda : 1, *args):
      self.outer = outer
      self.params = params
      super().__init__(
        name,
        getDict(base_config, self.params),
        lambda val: (self.outer.settingChanged(), inform()),
        Font.LEVEL4,
        number,
        letter,
        password,
        *args
      )
    def resetDefaultValue(self):
      self.setValue(getDict(default_config, self.params))
    def cancelValue(self):
      self.setValue(getDict(base_config, self.params))
    # 是否与base_config有差异，应该与save的逻辑相同，即changed()=False则save()无变化，反之changed()=True则save()有变化
    def changed(self):
      if self.getValue() == getDict(base_config, self.params):
        return False
      return True
    def save(self):
      new_value = self.getValue()
      previous_value = getDict(base_config, self.params)
      if new_value != previous_value:
        logger.debug("{}:({})->({})".format(self.params, previous_value, new_value))
        setDict(base_config, self.params, new_value)

  class SPathSelect(PathSelect):
    def __init__(self, outer, name, params, inform = lambda : 1, *args):
      self.outer = outer
      self.params = params
      super().__init__(
        name,
        getDict(base_config, self.params),
        lambda val: (self.outer.settingChanged(), inform()),
        Font.LEVEL4,
        *args
      )
    def resetDefaultValue(self):
      self.setValue(getDict(default_config, self.params))
    def cancelValue(self):
      self.setValue(getDict(base_config, self.params))
    # 是否与base_config有差异，应该与save的逻辑相同，即changed()=False则save()无变化，反之changed()=True则save()有变化
    def changed(self):
      if self.getValue() == getDict(base_config, self.params):
        return False
      return True
    def save(self):
      new_value = self.getValue()
      previous_value = getDict(base_config, self.params)
      if new_value != previous_value:
        logger.debug("{}:({})->({})".format(self.params, previous_value, new_value))
        setDict(base_config, self.params, new_value)
    
  class SDatabaseSelect(QFrame):
    def __init__(self, outer, text, params, *args):
      self.outer = outer
      self.params = params
      super().__init__(*args)

      self.widgets = []

      # sqlite选项卡
      section = {}
      section["title"] = QCheckBox()
      section["title"].setText("sqlite")
      section["title"].setFont(Font.LEVEL3)
      section["content"] = [
        Setting.SLineEdit(self.outer, "database", self.params + ["sqlite", "db"])
      ]
      self.widgets.append(section)

      # mysql选项卡
      section = {}
      section["title"] = QCheckBox()
      section["title"].setText("mysql")
      section["title"].setFont(Font.LEVEL3)
      section["content"] = [
        Setting.SLineEdit(self.outer, "host", self.params + ["mysql", "host"], True, True),
        Setting.SLineEdit(self.outer, "port", self.params + ["mysql", "port"], True),
        Setting.SLineEdit(self.outer, "user", self.params + ["mysql", "user"], True, True),
        Setting.SLineEdit(self.outer, "password", self.params + ["mysql", "password"], True, True, True),
        Setting.SLineEdit(self.outer, "database", self.params + ["mysql", "db"], True, True)
      ]
      self.widgets.append(section)

      vbox = QVBoxLayout()
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
        # db.setFrameShape(QFrame.Shape.StyledPanel)
        db.setStyleSheet(
          """
          .QFrame {
            border-width: 1px;
            border-style: solid;
            border-color: rgb(140, 140, 140);
          }
          """
        )
        hbox.addWidget(db)
        section["sub"] = db_sub
      hbox.addStretch(1)
      hbox.setSpacing(10)
      hbox.setContentsMargins(0, 0, 0, 0)
      title = QLabel(text)
      title.setFont(Font.LEVEL4)
      vbox.addWidget(title)
      vbox.addLayout(hbox)
      vbox.setContentsMargins(0, 0, 0, 0)
      self.setLayout(vbox)

      # 这里注意闭包的特性，同时由于connect会传参，因此需要用val占住第一个参数，这里用clicked事件最好，用stateChanged在逻辑上很繁琐
      for pos in range(len(self.widgets)):
        self.widgets[pos]["title"].clicked.connect(lambda val, _pos = pos : self.toggleSection(_pos))

      # 将组件状态切换到与base_config相同，但是由于现在处于init函数中，父亲组件还未初始化完成，所以不应该触发settingChanged，等父亲初始化完成后会自动调用
      self.toggleSectionByText(getDict(base_config, self.params + ["type"]), False)
    
    # 将选项卡切换到pos位置
    def toggleSection(self, pos):
      for i in range(len(self.widgets)):
        if i == pos:
          self.widgets[i]["title"].setCheckState(QtCore.Qt.CheckState.Checked)
          self.widgets[i]["sub"].setDisabled(False)
        else:
          self.widgets[i]["title"].setCheckState(QtCore.Qt.CheckState.Unchecked)
          self.widgets[i]["sub"].setDisabled(True)
      self.outer.settingChanged()

    # 将选项卡切换到内容为text的位置
    def toggleSectionByText(self, text, change = True):
      for section in self.widgets:
        if section["title"].text() == text:
          section["title"].setCheckState(QtCore.Qt.CheckState.Checked)
          section["sub"].setDisabled(False)
        else:
          section["title"].setCheckState(QtCore.Qt.CheckState.Unchecked)
          section["sub"].setDisabled(True)
      if change:
        self.outer.settingChanged()
        
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
    # 是否与base_config有差异，应该与save的逻辑相同，即changed()=False则save()无变化，反之changed()=True则save()有变化
    def changed(self):
      # 如果没有选中的选项，那么在保存的时候就不保存了，维持base_config的原值
      for section in self.widgets:
        # 保存时遇到第一项相同则保存
        if section["title"].checkState() == QtCore.Qt.CheckState.Checked:
          if section["title"].text() != getDict(base_config, self.params + ["type"]):
            return True
          else:
            break
      for section in self.widgets:
        for item in section["content"]:
          if item.changed():
            return True
      return False
    def save(self):
      # 如果没有选中的选项则不保存
      for section in self.widgets:
        if section["title"].checkState() == QtCore.Qt.CheckState.Checked:
          previous_value = getDict(base_config, self.params + ["type"])
          new_value = section["title"].text()
          if new_value != previous_value:
            logger.debug("{}:({})->({})".format(self.params + ["type"], previous_value, new_value))
            setDict(base_config, self.params + ["type"], new_value)
          break
      for section in self.widgets:
        for item in section["content"]:
         item.save()

  class SLogEdit(QFrame):
    def __init__(self, outer, text, params, *args):
      self.outer = outer
      self.params = params
      super().__init__(*args)
      self.contents = [
        Setting.SPathSelect(self.outer, "日志存放位置", self.params + ["logs_dir"], lambda : (self.vFrame.adjustSize(), self.adjustSize(), self.outer.adjustSize())),
        Setting.SComboBox(self.outer, "日志输出等级", self.params + ["logger_level"], getDict(base_config, self.params + ["level_options"])),
        Setting.SComboBox(self.outer, "文件输出等级", self.params + ["file_level"], getDict(base_config, self.params + ["level_options"])),
        Setting.SComboBox(self.outer, "命令行输出等级", self.params + ["stream_level"], getDict(base_config, self.params + ["level_options"]))
      ]
      hbox = QHBoxLayout()
      self.vFrame = vFrame = QFrame()
      vbox = QVBoxLayout()
      title = QLabel(text)
      title.setFont(Font.LEVEL2)
      vbox.addWidget(title)
      for item in self.contents:
        vbox.addWidget(item)
      vFrame.setLayout(vbox)
      # vFrame.setFrameShape(QFrame.Shape.StyledPanel)
      hbox.addWidget(vFrame)
      # hbox.addStretch(1)
      hbox.setContentsMargins(0, 0, 0, 0)
      self.setLayout(hbox)
      # self.setDisabled(True)

    def resetDefaultValue(self):
      for item in self.contents:
        item.resetDefaultValue()
    def cancelValue(self):
      for item in self.contents:
        item.cancelValue()
    # 是否与base_config有差异，应该与save的逻辑相同，即changed()=False则save()无变化，反之changed()=True则save()有变化
    def changed(self):
      for item in self.contents:
        if item.changed():
          return True
      return False
    def save(self):
      for item in self.contents:
        item.save()

  class STitle(QLabel):
    def __init__(self, outer, text, *args):
      self.outer = outer
      super().__init__(text, *args)
      self.setFont(Font.LEVEL1)

  @property
  def changed(self):
    return self._changed
  @changed.setter
  def changed(self, new_val):
    if new_val:
      self.saveButton.setDisabled(False)
      self.cancelButton.setDisabled(False)
    else:
      self.saveButton.setDisabled(True)
      self.cancelButton.setDisabled(True)
    self._changed = new_val

  def settingChanged(self):
    """
    判断设置是否发生了更改，并据此修改changed值
    """
    for section in self.content:
      for option in section["options"]:
        if option.changed():
          self.changed = True
          return
    self.changed = False

  def adjustSize(self):
    for section in self.sections:
      section.adjustSize()
    self.scroll_widget.adjustSize()
      
  def __init__(self, *args):
    super().__init__(*args)

    self.initUI()
    
    # 依据子组件状态更改changed值
    self.settingChanged()

  def initUI(self):
    # 功能按钮
    self.saveButton = QPushButton(" 保存")
    self.cancelButton = QPushButton(" 放弃")
    self.resetButton = QPushButton(" 重置")
    # 所有内容信息
    self.content = [
      {
        "title": Setting.STitle(self, "下载设置"),
        "options": 
        [
          Setting.SPathSelect(self, "文件存放位置", ["spider", "save_dir_name"], self.adjustSize),
          Setting.SLineEdit(self, "请求超时(秒)", ["spider", "timeout"], True),
          Setting.SLineEdit(self, "最大请求次数", ["spider", "request_max_count"], True),
          Setting.SCheckBox(self, "MD5匹配", ["spider", "md5_match"]),
          Setting.SCheckBox(self, "校正数据库", ["spider", "clear"]),
          Setting.SCheckBox(self, "每次下载完成后显示新增文件", ["__main__", "main", "print_new_file"]),
          Setting.SCheckBox(self, "存放新增文件快捷方式", ["__main__", "main", "save_new_file"]),
          Setting.SPathSelect(self, "新增文件快捷方式存放位置", ["__main__", "main", "save_as"], self.adjustSize),
          Setting.SComboBox(self, "图片存放方式", ["spider", "image_by_folder"], base_config["spider"]["image_by_folder_options"]),
          Setting.SDatabaseSelect(self, "数据库选择", ["spider", "database"]),
          Setting.SLogEdit(self, "日志（修改后需重启程序才能生效）", ["spider", "logs"])
        ]
      }, 
      {
        "title": Setting.STitle(self, "校正设置"),
        "options": 
        [
          Setting.SLineEdit(self, "记录输出文件", ["__main__", "check", "output"]),
          Setting.SCheckBox(self, "校正数据库", ["__main__", "check", "revise"])
        ]
      },
      {
        "title": Setting.STitle(self, "迁移设置"),
        "options": 
        [
          Setting.SLineEdit(self, "记录输出文件", ["__main__", "migrate", "output"]),
          Setting.SDatabaseSelect(self, "源数据库选择", ["__main__", "migrate", "source"]),
          Setting.SDatabaseSelect(self, "目标数据库选择", ["__main__", "migrate", "target"])
        ]
      }, 
      {
        "title": Setting.STitle(self, "数据库设置"),
        "options": 
        [
          Setting.SCheckBox(self, "若数据库名不存在是否自动创建（仅限mysql）", ["database", "create"]),
          Setting.SLogEdit(self, "日志（修改后需重启程序才能生效）", ["database", "logs"])
        ]
      },
      {
        "title": Setting.STitle(self, "图形客户端设置"),
        "options": 
        [
          Setting.SLogEdit(self, "日志（修改后需重启程序才能生效）", ["gui", "logs"])
        ]
      }
    ]

    # 设置滚动条中的布局
    layout_scroll = QVBoxLayout()
    self.sections = []
    for part in self.content:
      # 添加title
      section = QFrame()
      self.sections.append(section)
      layout_section = QVBoxLayout()
      layout_part = QHBoxLayout()
      layout_part.addWidget(part["title"])
      # 添加重置按钮
      button = ResetButton()
      # layout_part.addSpacing(5)
      layout_part.addWidget(button)
      layout_part.addStretch(1)
      layout_section.addLayout(layout_part)
      layout_section.addSpacing(5)
      # 添加设置项
      for option in part["options"]:
        layout_section.addWidget(option)
      section.setLayout(layout_section)
      section.setStyleSheet(
        """
        .QFrame {
          border-left-width: 2px;
          border-left-style: solid;
          border-left-color: black;
          padding-left: 4px;
        }
        """
      )
      layout_scroll.addWidget(section)
      layout_scroll.addSpacing(10)
      # 设置放弃按钮功能，这里闭包的特性一定要注意一下，同时要用val占住第一个位置
      button.clicked.connect(
        # 由于要执行循环，所以用列表推导式来单行实现，实际上并不需要该方法的返回值
        lambda val, _options = part["options"]:
          [one.cancelValue() for one in _options]
      )

    # 功能设置
    self.saveButton.clicked.connect(lambda val : self.save(False))
    self.cancelButton.clicked.connect(lambda val : self.cancel(True))
    self.resetButton.clicked.connect(lambda val : self.reset(True))

    # 设置功能按钮布局
    layout_function = QHBoxLayout()
    self.saveButton.setStyleSheet(
      """
      QPushButton {
        border: none;
        padding: 5px 10px 5px 10px;
        border-top-left-radius: 14px;
        border-bottom-left-radius: 14px;
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
        background-color: rgb(200, 200, 200);
      }
      QPushButton:pressed {
        background-color: rgb(150, 150, 150);
      }
      """
    )
    self.resetButton.setStyleSheet(
      """
      QPushButton {
        border: none;
        padding: 5px 10px 5px 10px;
        background-color: white;
        border-top-right-radius: 14px;
        border-bottom-right-radius: 14px;
        border-width: 1px;
        border-style: solid;
        border-color: gray;
        border-left: none;
      }
      QPushButton:hover {
        background-color: rgb(200, 200, 200);
      }
      QPushButton:pressed {
        background-color: rgb(150, 150, 150);
      }
      """
    )
    self.saveButton.setFixedWidth(100)
    self.cancelButton.setFixedWidth(100)
    self.resetButton.setFixedWidth(100)
    self.saveButton.setFont(Font.LEVEL4)
    self.cancelButton.setFont(Font.LEVEL4)
    self.resetButton.setFont(Font.LEVEL4)
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
    layout_function.addStretch(1)
    layout_function.setSpacing(0)
    layout_function.setContentsMargins(0, 6, 0, 6)

    # 最终布局设置
    layout_final = QVBoxLayout()
    scroll = QScrollArea()
    self.scroll_widget = scroll_widget = QFrame()
    scroll_widget.setLayout(layout_scroll)
    # 设置滚动区域的最小尺寸，因为在父亲上面设置了最小尺寸，所以这里就不用设置了
    # scroll.setMinimumSize(300, 400)
    # scrollarea 作为一个组件，可以设置窗口
    scroll.setWidget(scroll_widget)
    # 设置没有边框
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    layout_final.addWidget(scroll)
    function_widget = QFrame()
    function_widget.setLayout(layout_function)
    layout_final.addWidget(function_widget)
    layout_final.setContentsMargins(0, 0, 0, 0)
    layout_final.setSpacing(0)
    self.setLayout(layout_final)
    # 设置边框，因为子组件scroll已经有边框了，所以这里就不用加了
    # self.setFrameShape(QFrame.Shape.StyledPanel)

    # 最终样式修改
    scroll_widget.setStyleSheet(
      """
      QFrame {
        background-color: transparent;
      }
      """
    )
    qds = QGraphicsDropShadowEffect()
    qds.setOffset(0, 0)
    qds.setColor(QColor(200, 200, 200))
    qds.setBlurRadius(15)
    function_widget.setGraphicsEffect(qds)
    scroll_widget.setContentsMargins(8, 0, 0, 0)
    function_widget.setStyleSheet(
      """
      QFrame {
        background-color: rgb(240, 240, 240);
        background-color: white;
        background-color: transparent;
        background-color: rgb(250, 250, 250);
        background-color: rgb(238, 238, 238);
      }
      """
    )
    scroll.setStyleSheet(
      """
      QScrollArea {
        background-color: transparent;
      }
      QScrollBar:vertical
      {
        width:12px;
        background-color: rgb(200, 200, 200);
      }
      QScrollBar::handle:vertical
      {
        background-color: rgb(200, 200, 200);
        margin-left:0px;
        margin-right:0px;
      }
      QScrollBar::handle:vertical:hover
      {
        background:rgb(180, 180, 180);
      }
      QScrollBar:horizontal
      {
        height:12px;
        background-color: rgb(200, 200, 200);
      }
      QScrollBar::handle:horizontal
      {
        background-color: rgb(200, 200, 200);
        margin-left:0px;
        margin-right:0px;
      }
      QScrollBar::handle:horizontal:hover
      {
        background:rgb(180, 180, 180);
      }
      """
    )

  # 保存功能
  def save(self, alert = False):
    execute = False
    if alert:
      box = QMessageBox(self)
      box.setText("是否保存修改的设置信息？")
      box.setWindowTitle("Pixiv下载工具")
      box.setFont(Font.LEVEL3)
      yesButton = box.addButton("是(Y)", QMessageBox.ButtonRole.AcceptRole)
      noButton = box.addButton("否(N)", QMessageBox.ButtonRole.RejectRole)
      yesButton.setFont(Font.LEVEL4)
      noButton.setFont(Font.LEVEL4)
      box.setDefaultButton(yesButton)
      yesButton.setShortcut("Y")
      noButton.setShortcut("N")
      box.setStyleSheet(
        """
        QLabel {
          color: rgb(0, 51, 153);
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
        # 备份
        backup = copy.deepcopy(base_config)
        for section in self.content:
          for option in section["options"]:
            option.save()
        saveJson(base_config, os.path.abspath("config.json"))
      except Exception as e:
        logger.error("设置保存失败")
        # 还原
        cover(base_config, backup)
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
          }
          """
        )
        box.exec()
        return False
      else:
        logger.info("设置保存成功")
        self.settingChanged()
        # box = QMessageBox(self)
        # box.setText(f"配置文件保存成功")
        # box.setWindowTitle("Pixiv下载工具")
        # box.setFont(Font.LEVEL3)
        # okButton = box.addButton("好的", QMessageBox.ButtonRole.AcceptRole)
        # okButton.setFont(Font.LEVEL4)
        # box.setDefaultButton(okButton)
        # box.setStyleSheet(
        #   """
        #   QLabel {
        #     color: rgb(0, 51, 153);
        #   }
        #   """
        # )
        # box.exec()
        return True
    else:
      return False

  # 放弃功能
  def cancel(self, alert = True):
    execute = False
    if alert:
      box = QMessageBox(self)
      box.setText("是否放弃当前所有修改？")
      box.setWindowTitle("Pixiv下载工具")
      box.setFont(Font.LEVEL3)
      yesButton = box.addButton("是(Y)", QMessageBox.ButtonRole.AcceptRole)
      noButton = box.addButton("否(N)", QMessageBox.ButtonRole.RejectRole)
      yesButton.setFont(Font.LEVEL4)
      noButton.setFont(Font.LEVEL4)
      box.setDefaultButton(yesButton)
      yesButton.setShortcut("Y")
      noButton.setShortcut("N")
      box.setStyleSheet(
        """
        QLabel {
          color: rgb(0, 51, 153);
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
      box.setFont(Font.LEVEL3)
      yesButton = box.addButton("是(Y)", QMessageBox.ButtonRole.AcceptRole)
      noButton = box.addButton("否(N)", QMessageBox.ButtonRole.RejectRole)
      yesButton.setFont(Font.LEVEL4)
      noButton.setFont(Font.LEVEL4)
      box.setDefaultButton(yesButton)
      yesButton.setShortcut("Y")
      noButton.setShortcut("N")
      box.setStyleSheet(
        """
        QLabel {
          color: rgb(0, 51, 153);
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
        return self.save(False)
      elif box.clickedButton() == cancelButton:
        return self.cancel(False)
      else:
        return False
    else:
      return True
