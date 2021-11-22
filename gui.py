from PyQt6 import QtCore
from PyQt6.QtCore import QCoreApplication, Qt
from PyQt6.QtWidgets import QApplication
import sys

from gui.MainWindow import MainWindow


if __name__ == '__main__':
  # QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_Use96Dpi, True)
  app = QApplication(sys.argv)
  ex = MainWindow()
  sys.exit(app.exec())