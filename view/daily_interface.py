import time
from PySide6.QtWidgets import QWidget, QHBoxLayout, QStackedWidget
from PySide6.QtCore import QThread, Signal, Qt
from qfluentwidgets import (CardWidget, BodyLabel, StrongBodyLabel,
                           PrimaryPushButton, ProgressBar, InfoBar, InfoBarPosition,
                           VBoxLayout, SegmentedWidget, SpinBox,
                           SwitchButton, ScrollArea, FluentIcon, IndeterminateProgressBar)
from core.client import webSocketClient
from core.config_manager import config_manager


class DailyTaskThread(QThread):
    """日常任务执行线程"""
    taskStarted = Signal(str)  # 任务开始信号
    taskCompleted = Signal(str, bool)  # 任务完成信号 (任务名, 是否成功)
    allTasksCompleted = Signal()  # 所有任务完成信号
    progressUpdated = Signal(int)  # 进度更新信号
    
    def __init__(self, selected_tasks):
        super().__init__()
        self.selected_tasks = selected_tasks
        self.main_instance = None
        
    def run(self):
        """执行日常任务"""
        self.main_instance = webSocketClient.get_main_instance()
        if not self.main_instance:
            return

        total_tasks = len(self.selected_tasks)
        completed_tasks = 0

        # 定义需要宠物检查的战斗任务
        battle_tasks = {
            'g', 'h', 'i', 'j', 'k', 'e', 'f'  # 勇者之塔、泰坦矿洞、泰坦源脉、精灵王试炼、X战队密室、经验战场、学习力战场
        }

        # 检查选中的任务中是否包含战斗任务
        selected_task_keys = {task_key for task_key, _, _ in self.selected_tasks}
        has_battle_tasks = bool(selected_task_keys & battle_tasks)

        # 如果包含战斗任务，在开始前进行一次宠物检查
        if has_battle_tasks and hasattr(self.main_instance, 'pet_fight_packet_manager') and self.main_instance.pet_fight_packet_manager:
            pet_ids_needed = (3512, 3437, 3045)  # 需要的精灵ID
            if self.main_instance.pet_fight_packet_manager.message_callback:
                self.main_instance.pet_fight_packet_manager.message_callback("检测到战斗任务|开始前检查宠物")
            self.main_instance.pet_fight_packet_manager.check_backpack_pets(pet_ids_needed)
            time.sleep(0.3)  # 检查后稍作延迟

        for task_key, task_name, task_function in self.selected_tasks:
            self.taskStarted.emit(task_name)

            try:
                if hasattr(self.main_instance, 'pet_fight_packet_manager') and self.main_instance.pet_fight_packet_manager:
                    task_function()
                    self.taskCompleted.emit(task_name, True)
                else:
                    self.taskCompleted.emit(task_name, False)
            except Exception as e:
                print(f"任务 {task_name} 执行失败: {e}")
                self.taskCompleted.emit(task_name, False)

            completed_tasks += 1
            progress = int((completed_tasks / total_tasks) * 100)
            self.progressUpdated.emit(progress)

            # 任务间延迟
            time.sleep(0.5)

        self.allTasksCompleted.emit()


class DailyInterface(ScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('dailyInterface')

        # 创建内部视图容器
        self.view = QWidget(self)

        # 主布局
        self.vBoxLayout = VBoxLayout(self.view)
        self.vBoxLayout.setContentsMargins(0, 0, 10, 30)
        self.vBoxLayout.setSpacing(10)



        # 任务执行线程
        self.task_thread = None

        # 任务控件字典
        self.task_switches = {}  # 开关控件
        self.task_spinboxes = {}  # 84选项控件

        # 定义永久禁用的任务列表
        self.permanently_disabled_tasks = ['d', 'h']  # 六界神王殿和泰坦矿洞

        # 创建分段导航栏和堆叠窗口
        self.pivot = SegmentedWidget(self)
        self.stackedWidget = QStackedWidget(self)

        # 创建两个页面
        self.taskControlPage = QWidget()
        self.taskSettingsPage = QWidget()

        # 初始化界面
        self.initDailyView()
        self.loadDailySettings()
        self.loadTaskSettings()

        # 初始化切换按钮文本
        self.updateToggleButtonText()

        # 设置 ScrollArea 属性
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.enableTransparentBackground()

    def initDailyView(self):
        # 设置页面
        self.setupTaskControlPage()
        self.setupTaskSettingsPage()

        # 添加页面到分段导航栏
        self.addSubInterface(self.taskControlPage, 'taskControlPage', '任务控制')
        self.addSubInterface(self.taskSettingsPage, 'taskSettingsPage', '任务设置')

        # 添加分段导航栏和堆叠窗口到主布局
        self.vBoxLayout.addWidget(self.pivot, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.stackedWidget, 0, Qt.AlignTop)

        # 设置默认页面
        self.stackedWidget.setCurrentWidget(self.taskControlPage)
        self.pivot.setCurrentItem(self.taskControlPage.objectName())
        self.pivot.currentItemChanged.connect(
            lambda k: self.stackedWidget.setCurrentWidget(self.findChild(QWidget, k)))

    def addSubInterface(self, widget: QWidget, objectName, text):
        """添加子界面到分段导航栏"""
        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(routeKey=objectName, text=text)

    def setupTaskControlPage(self):
        """设置任务控制页面"""
        layout = VBoxLayout(self.taskControlPage)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)

        # 控制面板
        self.createControlPanel(layout)

        # 任务选择卡片
        self.createTaskSelectionCard(layout)

        # 进度显示卡片
        self.createProgressCard(layout)

    def setupTaskSettingsPage(self):
        """设置任务设置页面"""
        layout = VBoxLayout(self.taskSettingsPage)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)

        # 创建任务设置界面
        self.createTaskSettingsCard(layout)

    def createControlPanel(self, parent_layout):
        """创建控制面板"""
        card = CardWidget()
        layout = QHBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)

        # 标题
        titleLabel = StrongBodyLabel("任务控制")

        # 按钮
        self.startSelectedButton = PrimaryPushButton(FluentIcon.PLAY, "开始任务")
        self.startSelectedButton.setFixedSize(120, 40)
        self.startSelectedButton.clicked.connect(self.startSelectedTasks)

        self.stopButton = PrimaryPushButton(FluentIcon.PAUSE, "停止任务")
        self.stopButton.setFixedSize(120, 40)
        self.stopButton.setEnabled(False)
        self.stopButton.clicked.connect(self.stopTasks)

        layout.addWidget(titleLabel)
        layout.addStretch()
        layout.addWidget(self.startSelectedButton)
        layout.addWidget(self.stopButton)

        parent_layout.addWidget(card)

    def createTaskSelectionCard(self, parent_layout):
        """创建任务选择卡片"""
        card = CardWidget()
        layout = VBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # 卡片标题
        titleLabel = StrongBodyLabel("任务选择")
        layout.addWidget(titleLabel)

        # 全选/取消全选切换按钮和保存按钮
        selectLayout = QHBoxLayout()
        self.toggleSelectButton = PrimaryPushButton("全选")
        self.toggleSelectButton.setFixedSize(80, 30)
        self.toggleSelectButton.clicked.connect(self.toggleSelectAllTasks)

        self.saveSelectionButton = PrimaryPushButton(FluentIcon.SAVE, "保存")
        self.saveSelectionButton.setFixedSize(80, 30)
        self.saveSelectionButton.clicked.connect(self.saveDailySettings)

        selectLayout.addWidget(self.toggleSelectButton)
        selectLayout.addWidget(self.saveSelectionButton)
        selectLayout.addStretch()
        layout.addLayout(selectLayout)

        # 任务列表
        self.createTaskList(layout)

        parent_layout.addWidget(card)

    def createTaskList(self, parent_layout):
        """创建任务列表"""
        # 定义所有可用的日常任务 (任务键, 任务名, 函数名) - 参考core/main.py的实际函数映射
        self.available_tasks = [
            ('daily_check_in', '日常签到', 'daily_props_collection'),
            ('a', '刻印抽奖', 'engraved_raffle_machine'),
            ('b', 'VIP礼包', 'vip_package'),
            ('c', '战队日常', 'team_contribution'),
            ('d', '六界神王殿', None),  # 暂时没有实现
            ('e', '经验战场', 'experience_training_ground'),
            ('f', '学习力战场', 'learning_training_ground'),
            ('g', '勇者之塔', 'brave_tower'),
            ('h', '泰坦矿洞', 'titan_mines'),
            ('i', '泰坦源脉', 'titan_vein'),
            ('j', '精灵王试炼', 'trial_of_the_elf_king'),
            ('k', 'X战队密室', 'x_team_chamber'),
            ('l', '星愿漂流瓶许愿', 'make_a_wish'),
        ]

        # 添加任务卡片到垂直布局，一行一行排列
        for task_key, task_name, _ in self.available_tasks:
            # 创建任务卡片
            taskCard = self.createTaskCard(task_key, task_name)
            parent_layout.addWidget(taskCard)

    def createTaskCard(self, task_key, task_name):
        """创建单个任务卡片"""
        card = CardWidget()
        # 设置卡片高度，宽度自适应
        card.setFixedHeight(60)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)

        # 任务名称标签
        nameLabel = StrongBodyLabel(task_name)
        # nameLabel.setStyleSheet("font-size: 14px; font-weight: bold; color: #0078d4;")
        layout.addWidget(nameLabel)

        # 添加弹性空间
        layout.addStretch()

        # 开关控件 - 根据ui_config.py的默认配置设置初始状态
        switch = SwitchButton()
        # 参考core/ui_config.py的默认配置
        default_config = {
            'daily_check_in': '启用',
            'a': '启用', 'b': '启用', 'c': '启用', 'd': '禁止',
            'e': '启用', 'f': '启用', 'g': '禁止', 'h': '禁止',  # 泰坦矿洞改为禁止
            'i': '禁止', 'j': '启用', 'k': '启用', 'l': '启用'
        }

        # 检查是否为永久禁用的任务
        if task_key in self.permanently_disabled_tasks:
            switch.setChecked(False)
            switch.setEnabled(False)  # 禁用开关，用户无法点击
            # 设置禁用状态的样式
            switch.setStyleSheet("QWidget { opacity: 0.5; }")
        else:
            default_enabled = default_config.get(task_key, '启用') != '禁止'
            switch.setChecked(default_enabled)
            # 连接开关状态改变信号到更新按钮文本的方法
            switch.checkedChanged.connect(self.updateToggleButtonText)

        self.task_switches[task_key] = switch

        layout.addWidget(switch)

        return card

    def createProgressCard(self, parent_layout):
        """创建进度显示卡片"""
        card = CardWidget()
        layout = VBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # 卡片标题
        titleLabel = StrongBodyLabel("执行进度")
        layout.addWidget(titleLabel)

        # 不确定进度条（任务开始时显示）
        self.indeterminateProgressBar = IndeterminateProgressBar()
        self.indeterminateProgressBar.setFixedHeight(5)
        self.indeterminateProgressBar.stop()  # 确保初始状态为停止
        self.indeterminateProgressBar.hide()  # 初始隐藏
        layout.addWidget(self.indeterminateProgressBar)

        # 确定进度条（有具体进度时显示）
        self.progressBar = ProgressBar()
        self.progressBar.setFixedHeight(5)
        self.progressBar.setValue(0)
        layout.addWidget(self.progressBar)

        # 状态标签
        self.statusLabel = BodyLabel("准备就绪")
        self.statusLabel.setStyleSheet("font-size: 14px; margin-top: 10px;")
        layout.addWidget(self.statusLabel)

        parent_layout.addWidget(card)

    def createTaskSettingsCard(self, parent_layout):
        """创建任务设置卡片"""
        card = CardWidget()
        layout = VBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # 卡片标题
        titleLabel = StrongBodyLabel("任务详细设置")
        layout.addWidget(titleLabel)

        # 创建设置项
        self.createTaskSettings(layout)

        parent_layout.addWidget(card)

    def createTaskSettings(self, parent_layout):
        """创建任务设置项"""
        # 任务执行间隔设置
        intervalCard = CardWidget()
        intervalLayout = VBoxLayout(intervalCard)
        intervalLayout.setContentsMargins(10, 10, 10, 10)
        intervalLayout.setSpacing(8)

        intervalTitle = StrongBodyLabel("任务执行间隔")
        intervalTitle.setStyleSheet("font-size: 14px; font-weight: bold;")
        intervalLayout.addWidget(intervalTitle)

        intervalDesc = BodyLabel("设置任务之间的执行间隔时间（秒）")
        intervalDesc.setStyleSheet("font-size: 12px; color: gray;")
        intervalLayout.addWidget(intervalDesc)

        intervalHLayout = QHBoxLayout()
        self.intervalSpinBox = SpinBox()
        self.intervalSpinBox.setRange(0, 60)
        self.intervalSpinBox.setValue(1)
        self.intervalSpinBox.setSuffix(" 秒")
        intervalHLayout.addWidget(self.intervalSpinBox)
        intervalHLayout.addStretch()
        intervalLayout.addLayout(intervalHLayout)

        parent_layout.addWidget(intervalCard)

        # 任务重试设置
        retryCard = CardWidget()
        retryLayout = VBoxLayout(retryCard)
        retryLayout.setContentsMargins(10, 10, 10, 10)
        retryLayout.setSpacing(8)

        retryTitle = StrongBodyLabel("任务重试设置")
        retryTitle.setStyleSheet("font-size: 14px; font-weight: bold;")
        retryLayout.addWidget(retryTitle)

        retryDesc = BodyLabel("设置任务失败时的重试次数")
        retryDesc.setStyleSheet("font-size: 12px; color: gray;")
        retryLayout.addWidget(retryDesc)

        retryHLayout = QHBoxLayout()
        self.retrySpinBox = SpinBox()
        self.retrySpinBox.setRange(0, 10)
        self.retrySpinBox.setValue(2)
        self.retrySpinBox.setSuffix(" 次")
        retryHLayout.addWidget(self.retrySpinBox)
        retryHLayout.addStretch()
        retryLayout.addLayout(retryHLayout)

        parent_layout.addWidget(retryCard)

        # 自动停止设置
        autoStopCard = CardWidget()
        autoStopLayout = VBoxLayout(autoStopCard)
        autoStopLayout.setContentsMargins(10, 10, 10, 10)
        autoStopLayout.setSpacing(8)

        autoStopTitle = StrongBodyLabel("自动停止设置")
        autoStopTitle.setStyleSheet("font-size: 14px; font-weight: bold;")
        autoStopLayout.addWidget(autoStopTitle)

        autoStopDesc = BodyLabel("遇到错误时是否自动停止所有任务")
        autoStopDesc.setStyleSheet("font-size: 12px; color: gray;")
        autoStopLayout.addWidget(autoStopDesc)

        autoStopHLayout = QHBoxLayout()
        self.autoStopSwitch = SwitchButton()
        self.autoStopSwitch.setChecked(False)
        autoStopHLayout.addWidget(self.autoStopSwitch)
        autoStopHLayout.addStretch()
        autoStopLayout.addLayout(autoStopHLayout)

        parent_layout.addWidget(autoStopCard)

        # 保存设置按钮
        buttonLayout = QHBoxLayout()
        self.saveSettingsButton = PrimaryPushButton(FluentIcon.SAVE, "保存设置")
        self.saveSettingsButton.setFixedSize(120, 40)
        self.saveSettingsButton.clicked.connect(self.saveTaskSettings)

        self.resetSettingsButton = PrimaryPushButton(FluentIcon.REMOVE_FROM, "重置设置")
        self.resetSettingsButton.setFixedSize(120, 40)
        self.resetSettingsButton.clicked.connect(self.resetTaskSettings)

        buttonLayout.addStretch()
        buttonLayout.addWidget(self.saveSettingsButton)
        buttonLayout.addWidget(self.resetSettingsButton)
        parent_layout.addLayout(buttonLayout)

    def loadDailySettings(self):
        """加载日常设置"""
        try:
            daily_settings = config_manager.get_daily_settings()

            # 根据配置设置开关状态
            for task_key, switch in self.task_switches.items():
                # 永久禁用的任务始终保持禁止状态
                if task_key in self.permanently_disabled_tasks:
                    switch.setChecked(False)
                else:
                    # 兼容"启用"/"禁止"配置格式
                    config_value = daily_settings.get(task_key, '启用')
                    enabled = config_value != '禁止'
                    switch.setChecked(enabled)

            # 更新切换按钮文本
            self.updateToggleButtonText()

        except Exception as e:
            self.showMessage(f"加载日常设置失败: {str(e)}", "error")

    def saveDailySettings(self):
        """保存日常设置"""
        try:
            # 保存开关状态，使用"启用"/"禁止"格式
            for task_key, switch in self.task_switches.items():
                # 永久禁用的任务始终保存为禁止状态
                if task_key in self.permanently_disabled_tasks:
                    config_manager.set_setting('日常设置', task_key, '禁止')
                else:
                    value = '启用' if switch.isChecked() else '禁止'
                    config_manager.set_setting('日常设置', task_key, value)

            self.showMessage("任务选择已保存", "success")

        except Exception as e:
            self.showMessage(f"保存日常设置失败: {str(e)}", "error")

    def updateToggleButtonText(self):
        """更新切换按钮的文本"""
        if hasattr(self, 'toggleSelectButton'):
            # 只检查非永久禁用的任务
            available_switches = {k: v for k, v in self.task_switches.items()
                                if k not in self.permanently_disabled_tasks}
            all_selected = all(switch.isChecked() for switch in available_switches.values())
            self.toggleSelectButton.setText("取消全选" if all_selected else "全选")

    def toggleSelectAllTasks(self):
        """切换全选/取消全选任务"""
        # 只检查非永久禁用的任务
        available_switches = {k: v for k, v in self.task_switches.items()
                            if k not in self.permanently_disabled_tasks}
        all_selected = all(switch.isChecked() for switch in available_switches.values())

        if all_selected:
            # 如果全部选中，则取消全选（跳过永久禁用的任务）
            for task_key, switch in self.task_switches.items():
                if task_key not in self.permanently_disabled_tasks:
                    switch.setChecked(False)
        else:
            # 如果不是全部选中，则全选（跳过永久禁用的任务）
            for task_key, switch in self.task_switches.items():
                if task_key not in self.permanently_disabled_tasks:
                    switch.setChecked(True)

        # 更新按钮文本
        self.updateToggleButtonText()

    def selectAllTasks(self):
        """全选任务"""
        for task_key, switch in self.task_switches.items():
            if task_key not in self.permanently_disabled_tasks:
                switch.setChecked(True)

    def deselectAllTasks(self):
        """取消全选任务"""
        for task_key, switch in self.task_switches.items():
            if task_key not in self.permanently_disabled_tasks:
                switch.setChecked(False)

    def startSelectedTasks(self):
        """开始选中的任务"""
        # 检查是否已登录
        main_instance = webSocketClient.get_main_instance()
        if not main_instance:
            self.showMessage("请先登录游戏", "error")
            return

        # 获取选中的任务
        selected_tasks = []
        for task_key, switch in self.task_switches.items():
            if switch.isChecked():
                # 找到对应的任务信息
                for key, name, func_name in self.available_tasks:
                    if key == task_key:
                        # 获取实际的函数引用
                        if func_name and hasattr(main_instance, 'pet_fight_packet_manager') and main_instance.pet_fight_packet_manager:
                            task_func = getattr(main_instance.pet_fight_packet_manager, func_name, None)
                            if task_func:
                                selected_tasks.append((key, name, task_func))
                            else:
                                print(f"警告: 函数 {func_name} 不存在")
                        elif func_name is None:
                            # 对于暂未实现的任务，添加占位函数
                            placeholder_func = lambda task_name=name: print(f"任务 {task_name} 暂未实现")
                            selected_tasks.append((key, name, placeholder_func))
                        break
        
        if not selected_tasks:
            self.showMessage("请至少选择一个任务", "warning")
            return
            
        # 保存设置
        self.saveDailySettings()
        
        # 开始执行任务
        self.task_thread = DailyTaskThread(selected_tasks)
        self.task_thread.taskStarted.connect(self.onTaskStarted)
        self.task_thread.taskCompleted.connect(self.onTaskCompleted)
        self.task_thread.allTasksCompleted.connect(self.onAllTasksCompleted)
        self.task_thread.progressUpdated.connect(self.onProgressUpdated)
        
        # 更新UI状态
        self.startSelectedButton.setEnabled(False)
        self.stopButton.setEnabled(True)

        # 显示不确定进度条，隐藏确定进度条
        self.progressBar.hide()
        self.indeterminateProgressBar.show()
        self.indeterminateProgressBar.start()

        self.statusLabel.setText("正在执行任务...")

        self.task_thread.start()

    def stopTasks(self):
        """停止任务"""
        if self.task_thread and self.task_thread.isRunning():
            self.task_thread.terminate()
            self.task_thread.wait()

        # 停止不确定进度条
        if self.indeterminateProgressBar.isVisible():
            self.indeterminateProgressBar.stop()

        self.resetUI()
        self.showMessage("任务已停止", "info")

    def onTaskStarted(self, task_name):
        """任务开始回调"""
        self.statusLabel.setText(f"正在执行: {task_name}")

    def onTaskCompleted(self, task_name, success):
        """任务完成回调"""
        status = "成功" if success else "失败"
        self.statusLabel.setText(f"{task_name}: {status}")

    def onAllTasksCompleted(self):
        """所有任务完成回调"""
        # 停止不确定进度条
        if self.indeterminateProgressBar.isVisible():
            self.indeterminateProgressBar.stop()
            self.indeterminateProgressBar.hide()
            self.progressBar.show()

        # 确保进度条显示100%
        self.progressBar.setValue(100)
        self.statusLabel.setText("所有任务执行完成")

        # 重置按钮状态
        self.startSelectedButton.setEnabled(True)
        self.stopButton.setEnabled(False)

        self.showMessage("所有任务执行完成", "success")

    def onProgressUpdated(self, progress):
        """进度更新回调"""
        # 当有具体进度时，切换到确定进度条
        if self.indeterminateProgressBar.isVisible():
            self.indeterminateProgressBar.stop()
            self.indeterminateProgressBar.hide()
            self.progressBar.show()
            self.progressBar.setValue(0)

        self.progressBar.setValue(progress)

    def resetUI(self):
        """重置UI状态"""
        self.startSelectedButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.statusLabel.setText("准备就绪")

        # 重置进度条状态
        self.indeterminateProgressBar.hide()
        self.progressBar.show()
        self.progressBar.setValue(0)

    def showMessage(self, message, type="info"):
        """显示消息"""
        if type == "success":
            InfoBar.success("成功", message, parent=self, position=InfoBarPosition.TOP)
        elif type == "error":
            InfoBar.error("错误", message, parent=self, position=InfoBarPosition.TOP)
        elif type == "warning":
            InfoBar.warning("警告", message, parent=self, position=InfoBarPosition.TOP)
        else:
            InfoBar.info("信息", message, parent=self, position=InfoBarPosition.TOP)

    def saveTaskSettings(self):
        """保存任务设置"""
        try:
            # 使用config_manager保存各项设置
            config_manager.set_setting('任务设置', '执行间隔', str(self.intervalSpinBox.value()))
            config_manager.set_setting('任务设置', '重试次数', str(self.retrySpinBox.value()))
            config_manager.set_setting('任务设置', '自动停止', str(self.autoStopSwitch.isChecked()))

            self.showMessage("任务设置已保存", "success")

        except Exception as e:
            self.showMessage(f"保存任务设置失败: {str(e)}", "error")

    def resetTaskSettings(self):
        """重置任务设置"""
        try:
            # 重置为默认值
            self.intervalSpinBox.setValue(1)
            self.retrySpinBox.setValue(2)
            self.autoStopSwitch.setChecked(False)

            self.showMessage("任务设置已重置", "info")

        except Exception as e:
            self.showMessage(f"重置任务设置失败: {str(e)}", "error")

    def loadTaskSettings(self):
        """加载任务设置"""
        try:
            # 使用config_manager加载各项设置
            interval = int(config_manager.get_setting('任务设置', '执行间隔', '1'))
            retry_count = int(config_manager.get_setting('任务设置', '重试次数', '2'))
            auto_stop = config_manager.get_setting('任务设置', '自动停止', 'False') == 'True'

            self.intervalSpinBox.setValue(interval)
            self.retrySpinBox.setValue(retry_count)
            self.autoStopSwitch.setChecked(auto_stop)

        except Exception as e:
            self.showMessage(f"加载任务设置失败: {str(e)}", "error")
