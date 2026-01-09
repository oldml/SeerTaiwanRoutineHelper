import sys
from PySide6.QtWidgets import QApplication
from qfluentwidgets import setTheme, Theme, setThemeColor

from view.main_windows import Window

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 设置主题色和浅色主题
    setThemeColor('#0078d4')  # 设置蓝色主题
    setTheme(Theme.LIGHT)  # 设置浅色主题

    w = Window()
    w.show()
    app.exec()
