from PyQt6.QtWidgets import QApplication
import sys

from component.MainWindow import MainWindow


if __name__ == '__main__':
  app = QApplication(sys.argv)
  ex = MainWindow()
  sys.exit(app.exec())