# coding:utf-8
import webbrowser
import random
import numpy as np
from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPainterPath, QImage
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsDropShadowEffect
from qfluentwidgets import TextEdit, PushButton, FluentIcon


class BannerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFixedHeight(448)

        self.vBoxLayout = QVBoxLayout(self)
        self.galleryLabel = QLabel('赛尔号护肝小助手\nSeerTaiwanRoutineHelper', self)
        self.galleryLabel.setStyleSheet("color: white;font-size: 30px; font-weight: 600;")

        # 创建阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)  # 阴影模糊半径
        shadow.setColor(Qt.black)  # 阴影颜色
        shadow.setOffset(1.2, 1.2)     # 阴影偏移量

        # 将阴影效果应用于小部件
        self.galleryLabel.setGraphicsEffect(shadow)

        # 随机选择背景图片
        bg_images = ["resource/image/bg.jpg", "resource/image/bg2.png"]
        selected_bg = random.choice(bg_images)
        self.img = Image.open(selected_bg)
        self.banner = None
        self.path = None

        self.galleryLabel.setObjectName('galleryLabel')

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 20, 0, 0)
        self.vBoxLayout.addWidget(self.galleryLabel)
        self.vBoxLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.SmoothPixmapTransform | QPainter.Antialiasing)

        if not self.banner or not self.path:
            image_height = self.img.width * self.height() // self.width()
            crop_area = (0, 0, self.img.width, image_height)  # (left, upper, right, lower)
            cropped_img = self.img.crop(crop_area)
            img_data = np.array(cropped_img)  # Convert PIL Image to numpy array
            height, width, channels = img_data.shape
            bytes_per_line = channels * width
            self.banner = QImage(img_data.data, width, height, bytes_per_line, QImage.Format_RGB888)

            path = QPainterPath()
            rect = self.rect()
            path.addRoundedRect(rect.x(), rect.y(), rect.width(), rect.height(), 10, 10)  # 使用实际widget的rect
            self.path = path.simplified()

        painter.setClipPath(self.path)
        painter.drawImage(self.rect(), self.banner)


class HomeInterface(QWidget):
    """ Home interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.banner = BannerWidget(self)
        self.vBoxLayout = QVBoxLayout(self)

        # 创建富文本框
        self.textEdit = TextEdit()

        # 创建QQ群按钮
        self.qqGroupButton = PushButton('点击加入QQ群聊', self)
        self.qqGroupButton.setIcon(FluentIcon.PEOPLE)
        self.qqGroupButton.clicked.connect(self.openQQGroup)

        self.__initWidget()

    def __initWidget(self):
        self.setObjectName('homeInterface')

        self.vBoxLayout.setContentsMargins(10, 10, 10, 10)
        self.vBoxLayout.setSpacing(25)
        self.vBoxLayout.addWidget(self.banner)

        # 设置富文本框内容和样式
        self.textEdit.setMarkdown("#### 烂尾了🤯 \n #### 精灵仅配置了表姐+六界帝神+艾欧丽娅，可自动更换，如果仓库精灵太多可能会失效😀 \n #### 系统中仍遗留部分原因不明的程序异常🤔 \n\n #### by:Adai")
        self.vBoxLayout.addWidget(self.textEdit)

        # 添加QQ群按钮
        self.vBoxLayout.addWidget(self.qqGroupButton)

        self.vBoxLayout.setAlignment(Qt.AlignTop)

    def openQQGroup(self):
        """直接打开QQ群链接"""
        webbrowser.open('https://qm.qq.com/q/jEWdNP4EWA')