from PySide6.QtWidgets import QWidget, QHBoxLayout
from qfluentwidgets import (CardWidget, BodyLabel, StrongBodyLabel,
                           ComboBox, SpinBox, SwitchButton, PrimaryPushButton,
                           InfoBar, InfoBarPosition, VBoxLayout, GroupHeaderCardWidget, FluentIcon)
from core.config_manager import config_manager


class SettingsInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('settingsInterface')

        # 主布局
        self.vBoxLayout = VBoxLayout(self)
        self.vBoxLayout.setContentsMargins(15, 15, 15, 15)
        self.vBoxLayout.setSpacing(20)

        # 初始化界面
        self.initSettingsView()
        self.loadSettings()

    def initSettingsView(self):
        # 通用设置卡片
        self.createGeneralSettingsCard()

        # 高级设置卡片
        self.createAdvancedSettingsCard()

        # 操作按钮
        self.createActionButtons()

    def createGeneralSettingsCard(self):
        """创建通用设置卡片"""
        card = GroupHeaderCardWidget()
        card.setTitle("通用设置")
        card.setBorderRadius(8)

        # 能力装备下拉框
        self.capabilityEquipmentCombo = ComboBox()
        self.capabilityEquipmentCombo.addItems(["装备1", "装备2", "装备3"])
        self.capabilityEquipmentCombo.setFixedWidth(200)
        self.capabilityEquipmentCombo.setCurrentText("装备1")

        # 能力称号下拉框
        self.capabilityTitleCombo = ComboBox()
        self.capabilityTitleCombo.addItems(["称号1", "称号2", "称号3"])
        self.capabilityTitleCombo.setFixedWidth(200)
        self.capabilityTitleCombo.setCurrentText("称号1")

        # 自爆精灵下拉框
        self.freeElfCombo = ComboBox()
        self.freeElfCombo.addItems(["帝皇之御", "幻影蝶", "仁天之君·刘备", "昭烈帝刘备", "众神之首·宙斯", "神王宙斯"])
        self.freeElfCombo.setFixedWidth(200)
        self.freeElfCombo.setCurrentText("帝皇之御")

        # 弹伤精灵下拉框
        self.godElfCombo = ComboBox()
        self.godElfCombo.addItems(["六界神王", "六界帝神", "乔特鲁", "乔特鲁德", "万人敌张飞", "盖世张飞", "埃尔尼亚", "埃尔文达"])
        self.godElfCombo.setFixedWidth(200)
        self.godElfCombo.setCurrentText("六界神王")

        # 补刀精灵下拉框
        self.mendingElfCombo = ComboBox()
        self.mendingElfCombo.addItems(["圣灵谱尼", "时空界皇", "深渊狱神·哈迪斯"])
        self.mendingElfCombo.setFixedWidth(200)
        self.mendingElfCombo.setCurrentText("圣灵谱尼")

        # 添加组到卡片
        card.addGroup(FluentIcon.GAME, "能力装备", "选择角色的能力装备", self.capabilityEquipmentCombo)
        card.addGroup(FluentIcon.CERTIFICATE, "能力称号", "选择角色的能力称号", self.capabilityTitleCombo)
        card.addGroup(FluentIcon.ROBOT, "自爆精灵", "选择自爆精灵类型", self.freeElfCombo)
        card.addGroup(FluentIcon.HEART, "弹伤精灵", "选择弹伤精灵类型", self.godElfCombo)
        card.addGroup(FluentIcon.CUT, "补刀精灵", "选择补刀精灵类型", self.mendingElfCombo)

        self.vBoxLayout.addWidget(card)

    def createAdvancedSettingsCard(self):
        """创建高级设置卡片"""
        card = CardWidget()
        layout = VBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # 卡片标题
        titleLabel = StrongBodyLabel("高级设置")
        layout.addWidget(titleLabel)
        
        # 调试模式
        debugLayout = QHBoxLayout()
        debugLayout.addWidget(BodyLabel("调试模式:"))
        self.debugModeSwitch = SwitchButton()
        debugLayout.addWidget(self.debugModeSwitch)
        debugLayout.addStretch()
        layout.addLayout(debugLayout)

        # 日志级别
        logLevelLayout = QHBoxLayout()
        logLevelLayout.addWidget(BodyLabel("日志级别:"))
        self.logLevelCombo = ComboBox()
        self.logLevelCombo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.logLevelCombo.setCurrentText("INFO")
        logLevelLayout.addWidget(self.logLevelCombo)
        logLevelLayout.addStretch()
        layout.addLayout(logLevelLayout)

        # 最大重试次数
        retryLayout = QHBoxLayout()
        retryLayout.addWidget(BodyLabel("最大重试次数:"))
        self.maxRetrySpinBox = SpinBox()
        self.maxRetrySpinBox.setRange(1, 10)
        self.maxRetrySpinBox.setValue(3)
        retryLayout.addWidget(self.maxRetrySpinBox)
        retryLayout.addStretch()
        layout.addLayout(retryLayout)
        
        self.vBoxLayout.addWidget(card)

    def createActionButtons(self):
        """创建操作按钮"""
        buttonLayout = QHBoxLayout()

        self.saveButton = PrimaryPushButton(FluentIcon.SAVE, "保存设置")
        self.saveButton.setFixedSize(120, 40)
        self.saveButton.clicked.connect(self.saveSettings)

        self.resetButton = PrimaryPushButton(FluentIcon.REMOVE_FROM, "重置设置")
        self.resetButton.setFixedSize(120, 40)
        self.resetButton.clicked.connect(self.resetSettings)

        buttonLayout.addStretch()
        buttonLayout.addWidget(self.saveButton)
        buttonLayout.addWidget(self.resetButton)

        self.vBoxLayout.addLayout(buttonLayout)

    def loadSettings(self):
        """加载设置"""
        try:
            # 使用config_manager加载设置
            capability_equipment = config_manager.get_setting('通用设置', 'capability_equipment', '装备1')
            self.capabilityEquipmentCombo.setCurrentText(capability_equipment)

            capability_title = config_manager.get_setting('通用设置', 'capability_title', '称号1')
            self.capabilityTitleCombo.setCurrentText(capability_title)

            free_elf = config_manager.get_setting('通用设置', 'self_destructing_elf', '帝皇之御')
            self.freeElfCombo.setCurrentText(free_elf)

            god_elf = config_manager.get_setting('通用设置', 'rebound_damage_elf', '六界神王')
            self.godElfCombo.setCurrentText(god_elf)

            mending_elf = config_manager.get_setting('通用设置', 'mending_blade_elf', '圣灵谱尼')
            self.mendingElfCombo.setCurrentText(mending_elf)

            # 加载其他设置
            debug_mode = config_manager.get_setting('通用设置', 'debug_mode', 'False') == 'True'
            self.debugModeSwitch.setChecked(debug_mode)

            log_level = config_manager.get_setting('通用设置', 'log_level', 'INFO')
            self.logLevelCombo.setCurrentText(log_level)

            max_retry = int(config_manager.get_setting('通用设置', 'max_retry', '3'))
            self.maxRetrySpinBox.setValue(max_retry)

        except Exception as e:
            self.showMessage(f"加载设置失败: {str(e)}", "error")

    def saveSettings(self):
        """保存设置"""
        try:
            # 使用config_manager保存设置
            config_manager.set_setting('通用设置', 'capability_equipment', self.capabilityEquipmentCombo.currentText())
            config_manager.set_setting('通用设置', 'capability_title', self.capabilityTitleCombo.currentText())
            config_manager.set_setting('通用设置', 'self_destructing_elf', self.freeElfCombo.currentText())
            config_manager.set_setting('通用设置', 'rebound_damage_elf', self.godElfCombo.currentText())
            config_manager.set_setting('通用设置', 'mending_blade_elf', self.mendingElfCombo.currentText())

            # 保存其他设置
            config_manager.set_setting('通用设置', 'debug_mode', str(self.debugModeSwitch.isChecked()))
            config_manager.set_setting('通用设置', 'log_level', self.logLevelCombo.currentText())
            config_manager.set_setting('通用设置', 'max_retry', str(self.maxRetrySpinBox.value()))

            self.showMessage("设置保存成功", "success")

        except Exception as e:
            self.showMessage(f"保存设置失败: {str(e)}", "error")

    def resetSettings(self):
        """重置设置"""
        # 重置通用设置
        self.capabilityEquipmentCombo.setCurrentText("装备1")
        self.capabilityTitleCombo.setCurrentText("称号1")
        self.freeElfCombo.setCurrentText("帝皇之御")
        self.godElfCombo.setCurrentText("六界神王")
        self.mendingElfCombo.setCurrentText("圣灵谱尼")

        # 重置其他设置
        self.debugModeSwitch.setChecked(False)
        self.logLevelCombo.setCurrentText("INFO")
        self.maxRetrySpinBox.setValue(3)

        self.showMessage("设置已重置", "info")

    def showMessage(self, message, type="info"):
        """显示消息"""
        if type == "success":
            InfoBar.success("成功", message, parent=self, position=InfoBarPosition.TOP)
        elif type == "error":
            InfoBar.error("错误", message, parent=self, position=InfoBarPosition.TOP)
        else:
            InfoBar.info("信息", message, parent=self, position=InfoBarPosition.TOP)
