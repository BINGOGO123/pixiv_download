from PyQt6.QtGui import QFont


class Font(object):
  LEVEL1 = QFont("宋体", 16, QFont.Weight.Bold)
  LEVEL2 = QFont("宋体", 14, QFont.Weight.Bold)
  LEVEL3 = QFont("宋体", 12, QFont.Weight.Bold)
  LEVEL4 = QFont("宋体", 12)
  LEVEL5 = QFont("宋体", 10)
  ENGLISH_LEVEL4 = QFont("Georgia", 12)
  ENGLISH_LEVEL5 = QFont("Georgia", 10)