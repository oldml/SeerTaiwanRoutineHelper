from PySide6.QtWidgets import QWidget, QGridLayout, QHBoxLayout
from qfluentwidgets import (TextEdit, BodyLabel, SimpleCardWidget, PrimaryPushButton,
                           StrongBodyLabel, CardWidget, VBoxLayout, Flyout, FlyoutView, FlyoutAnimationType, FluentIcon)

from component.PetView import PetCard


class FightInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('fightInterface')
        
        # 主布局
        self.layout = QGridLayout()
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(20)
        
        # 控制面板
        self.controlCard = CardWidget()
        self.controlCard.setFixedHeight(80)
        controlLayout = QHBoxLayout(self.controlCard)
        controlLayout.setContentsMargins(15, 15, 15, 15)
        
        self.startFight = PrimaryPushButton(FluentIcon.GAME, "开始战斗")
        self.startFight.setFixedSize(120, 40)
        self.startFight.clicked.connect(self.onStartFightClicked)
        self.stopFight = PrimaryPushButton(FluentIcon.PAUSE, "停止战斗")
        self.stopFight.setFixedSize(120, 40)
        self.stopFight.setEnabled(False)
        
        controlLayout.addWidget(StrongBodyLabel("巅峰对战控制"))
        controlLayout.addStretch()
        controlLayout.addWidget(self.startFight)
        controlLayout.addWidget(self.stopFight)
        
        # 战斗详情
        self.fightDetail = FightView()
        
        # 添加到主布局
        self.layout.addWidget(self.controlCard, 0, 0, 1, 1)
        self.layout.addWidget(self.fightDetail, 1, 0, 1, 1)
        
        self.setLayout(self.layout)

    def onStartFightClicked(self):
        """开始战斗按钮点击事件处理"""
        # 创建带图片的浮出控件
        view = FlyoutView(
            title='未完待续',
            content="你在想屁吃！",
            image='resource/image/？.jpg',
            isClosable=False
        )

        # 显示浮出控件，显示在按钮左边
        w = Flyout.make(view, self.startFight, self, aniType=FlyoutAnimationType.SLIDE_LEFT)
        view.closed.connect(w.close)


class FightView(SimpleCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.layout = QGridLayout()
        self.layout.setSpacing(12)
        self.layout.setContentsMargins(15, 15, 15, 15)

        # 战斗信息显示区域
        self.userDetail = TextEdit()
        self.rivalDetail = TextEdit()
        self.userDetail.setFixedSize(350, 400)
        self.rivalDetail.setFixedSize(350, 400)
        self.userDetail.setPlaceholderText("我方战斗信息将在这里显示...")
        self.rivalDetail.setPlaceholderText("对方战斗信息将在这里显示...")
        
        # 对战信息标签
        self.rivalUidLabel = BodyLabel("对战赛尔ID: 未连接")
        self.rivalUidLabel.setStyleSheet("font-size: 14px; font-weight: bold;")
        
        # 精灵信息
        self.userPetInfo = ["5000", "NULL", "NULL", "NULL", "NULL", "NULL"]
        self.rivalPetInfo = ["5000", "NULL", "NULL", "NULL", "NULL", "NULL"]
        
        # 当前出战精灵
        self.userCurrentPet = PetCard("NULL")
        self.userCurrentPet.imgWidget.setFixedSize(60, 60)
        self.userCurrentPet.setFixedSize(60, 60)
        self.rivalCurrentPet = PetCard("NULL")
        self.rivalCurrentPet.imgWidget.setFixedSize(60, 60)
        self.rivalCurrentPet.setFixedSize(60, 60)

        # 精灵队伍布局
        self.userPetView = QGridLayout()
        self.rivalPetView = QGridLayout()

        self.init_pet_view()

        # 布局设置
        self.layout.addWidget(BodyLabel("我方当前精灵:"), 0, 0, 1, 1)
        self.layout.addWidget(self.userCurrentPet, 0, 1, 1, 1)
        self.layout.addWidget(BodyLabel("对方当前精灵:"), 0, 6, 1, 1)
        self.layout.addWidget(self.rivalCurrentPet, 0, 7, 1, 1)
        
        self.layout.addWidget(BodyLabel("我方精灵队伍:"), 1, 0, 1, 4)
        self.layout.addWidget(BodyLabel("对方精灵队伍:"), 1, 4, 1, 4)
        self.layout.addLayout(self.userPetView, 2, 0, 1, 4)
        self.layout.addLayout(self.rivalPetView, 2, 4, 1, 4)
        
        self.layout.addWidget(self.rivalUidLabel, 3, 0, 1, 8)
        self.layout.addWidget(BodyLabel("我方战斗详情:"), 4, 0, 1, 4)
        self.layout.addWidget(BodyLabel("对方战斗详情:"), 4, 4, 1, 4)
        self.layout.addWidget(self.userDetail, 5, 0, 1, 4)
        self.layout.addWidget(self.rivalDetail, 5, 4, 1, 4)

        self.setFixedSize(800, 650)
        self.setLayout(self.layout)

    def init_pet_view(self):
        """初始化精灵队伍视图"""
        self._create_pet_cards(self.userPetInfo, self.userPetView)
        self._create_pet_cards(self.rivalPetInfo, self.rivalPetView)

    def _create_pet_cards(self, pet_info, layout):
        """创建精灵卡片的辅助方法"""
        for i in range(6):
            pet_id = pet_info[i] if pet_info[i] != "NULL" else "NULL"
            pet_card = PetCard(pet_id)
            pet_card.imgWidget.setFixedSize(50, 50)
            pet_card.setFixedSize(50, 50)
            layout.addWidget(pet_card, 0, i)

    def change_rival_uid(self, data):
        """更新对战赛尔ID"""
        try:
            uid = str(int(data.replace(' ', ''), 16))
            self.rivalUidLabel.setText(f"对战赛尔ID: {uid}")
        except:
            self.rivalUidLabel.setText("对战赛尔ID: 解析失败")
