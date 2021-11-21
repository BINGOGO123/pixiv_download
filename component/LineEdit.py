# 单行文本编辑

from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtWidgets import QFrame, QLabel, QLineEdit, QVBoxLayout

class LineEdit(QFrame):

  def __init__(self, name, val, inform, font, number = False, letter = False, password = False, *args):
    """
    number和letter表示是否仅限输入数字和字母, password表示是否对输入内容进行隐藏

    number = False and letter = False 表示无限制，但是不能输入空白符号

    number = True and letter = False 表示仅限输入数字，范围为0-999999

    number = False and letter = True 表示仅限输入字母

    number = True and letter = True 表示仅限输入数字和字母
    """
    super().__init__(*args)
    self.name = name
    self.val = val
    self.inform = inform
    self.font = font
    self.number = number
    self.letter = letter
    self.password = password
    self.initUI()

  def initUI(self):
    layout = QVBoxLayout()

    # 添加标题
    title = QLabel(self.name)
    title.setFont(self.font)
    layout.addWidget(title)

    self.edit = QLineEdit(self.val)
    self.edit.setFixedWidth(200)
    self.edit.setFont(self.font)
    self.edit.setClearButtonEnabled(True)

    # 是否开启密码模式
    if self.password:
      self.edit.setEchoMode(QLineEdit.EchoMode.Password)
    # 是否仅限输入数字
    if self.number and self.letter:
      self.edit.setValidator(QRegularExpressionValidator(QRegularExpression('^\w*$')))
    elif self.number:
      self.edit.setValidator(QRegularExpressionValidator(QRegularExpression('^[1-9]\d{0,5}$')))
      # self.edit.setValidator(QIntValidator(0, 1000))
    elif self.letter:
      self.edit.setValidator(QRegularExpressionValidator(QRegularExpression('^[a-zA-Z]*$')))
    else:
      # 不能输入空白符号
      self.edit.setValidator(QRegularExpressionValidator(QRegularExpression('^\\S*$')))
    self.edit.setStyleSheet(
      """
      QLineEdit {
        background-color: rgb(240, 240, 240);
        border: none;
        padding: 3px 5px 3px 5px;
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
    # 这里原本想要设置阴影效果，最后还是采用边框效果
    # qds = QGraphicsDropShadowEffect()
    # qds.setOffset(0, 0)
    # qds.setColor(QColor(100, 100, 100))
    # qds.setBlurRadius(20)
    # edit.setGraphicsEffect(qds)

    layout.addWidget(self.edit)

    # 设置最后的修改样式
    layout.setContentsMargins(0, 0, 0, 0)
    self.setLayout(layout)

    # 触发事件
    self.edit.textChanged.connect(self.inform)
    
  # 设置新值
  def setValue(self, new_val):
    self.edit.setText(new_val)
    
  # 获取当前值
  def getValue(self):
    return self.edit.text()