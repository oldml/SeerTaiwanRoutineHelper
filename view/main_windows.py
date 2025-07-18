# coding:utf-8
import os

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from qfluentwidgets import MSFluentWindow, SplashScreen
from qfluentwidgets import FluentIcon as FIF

from .fight_interface import FightInterface
from .home_interface import HomeInterface
from .login_interface import LoginInterface
from .settings_interface import SettingsInterface
from .daily_interface import DailyInterface


class Window(MSFluentWindow):

    def __init__(self):
        super().__init__()
        self.homeInterface = HomeInterface()
        self.loginInterface = LoginInterface()
        self.fightInterface = FightInterface()
        self.settingsInterface = SettingsInterface()
        self.dailyInterface = DailyInterface()
        self.initNavigation()
        self.initWindow()

        # 1. 先显示主界面
        self.show()

        # 2. 创建启动页面（在主界面显示后）
        try:
            self.splashScreen = SplashScreen(self.windowIcon(), self)
            self.splashScreen.setIconSize(QSize(102, 102))
        except Exception as e:
            print(f"SplashScreen创建失败: {e}")
            self.splashScreen = None

        # 3. 安全地隐藏启动页面
        if self.splashScreen:
            try:
                self.splashScreen.finish()
            except Exception as e:
                print(f"SplashScreen关闭失败: {e}")

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, '主页')
        self.addSubInterface(self.loginInterface, FIF.PEOPLE, '登录')
        self.addSubInterface(self.dailyInterface, FIF.CALENDAR, '一键日常')
        self.addSubInterface(self.fightInterface, FIF.GAME, '巅峰对战')
        self.addSubInterface(self.settingsInterface, FIF.SETTING, '通用设置')

    def initWindow(self):
        # 设置主题（可选）
        self.setMicaEffectEnabled(False)

        # 禁用最大化
        self.titleBar.maxBtn.setHidden(True)
        self.titleBar.maxBtn.setDisabled(True)
        self.titleBar.setDoubleClickEnabled(False)
        self.setResizeEnabled(False)
        self.setWindowFlags(Qt.WindowCloseButtonHint)

        # 强制设置窗口大小 - 多次调用确保生效
        self.resize(903, 829)
        self.setFixedSize(903, 829)  # 临时固定大小

        # 获取当前工作目录
        current_dir = os.path.dirname(__file__)
        # 设置窗口图标为绝对路径下的图标
        icon_path = os.path.join(current_dir, '../resource/image/favicon.ico')
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle('SeerTaiwanRoutineHelper')

        # 居中窗口
        screen = QApplication.primaryScreen().availableGeometry()
        w, h = screen.width(), screen.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
