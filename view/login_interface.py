from datetime import datetime

from PySide6.QtWidgets import QWidget, QGridLayout, QTableWidgetItem, QHBoxLayout
from PySide6.QtCore import QTimer
from qfluentwidgets import (LineEdit, PasswordLineEdit, PrimaryPushButton, TableWidget,
                           BodyLabel, StrongBodyLabel, CardWidget, VBoxLayout,
                           SwitchButton, ComboBox, Flyout, InfoBarIcon, FluentIcon)

from core.client import webSocketClient
from core.config_manager import config_manager


class LoginInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('loginInterface')
        self.loginBtn = None
        self.layout = None
        self.account = None
        self.password = None
        self.messageList = None
        self.savePasswordSwitch = None
        self.serverCombo = None
        self.initHomeView()
        self.load_saved_account_info()

    def initHomeView(self):
        self.layout = QGridLayout()
        
        # 创建登录卡片
        self.loginCard = CardWidget()
        self.loginCard.setFixedHeight(280)
        loginLayout = VBoxLayout(self.loginCard)
        
        # 标题
        titleLabel = StrongBodyLabel("登录游戏")
        
        # 输入框
        self.account = LineEdit()
        self.account.setPlaceholderText("请输入用户ID")
        self.account.setFixedHeight(40)

        self.password = PasswordLineEdit()
        self.password.setPlaceholderText("请输入密码")
        self.password.setFixedHeight(40)

        # 服务器选择和保存密码在同一行
        serverAndSaveLayout = QHBoxLayout()

        # 服务器选择
        serverLabel = BodyLabel("服务器:")
        self.serverCombo = ComboBox()
        self.serverCombo.addItems([f"{i}服" for i in range(1, 41)])
        self.serverCombo.setCurrentText("32服")  # 默认32服
        self.serverCombo.setFixedWidth(100)

        # 保存密码开关
        savePasswordLabel = BodyLabel("保存密码:")
        self.savePasswordSwitch = SwitchButton()

        # 添加到同一行布局
        serverAndSaveLayout.addWidget(serverLabel)
        serverAndSaveLayout.addWidget(self.serverCombo)
        serverAndSaveLayout.addStretch()
        serverAndSaveLayout.addWidget(savePasswordLabel)
        serverAndSaveLayout.addWidget(self.savePasswordSwitch)

        # 登录按钮
        self.loginBtn = PrimaryPushButton(FluentIcon.SEND, '开始登录')
        self.loginBtn.setFixedHeight(40)
        self.loginBtn.clicked.connect(self.login_btn_clicked)

        # 添加到登录卡片
        loginLayout.addWidget(titleLabel)
        loginLayout.addWidget(self.account)
        loginLayout.addWidget(self.password)
        loginLayout.addLayout(serverAndSaveLayout)
        loginLayout.addWidget(self.loginBtn)
        
        # 消息列表
        self.messageList = TableWidget()
        self.init_table()

        # 连接信号
        webSocketClient.new_message.connect(self.get_new_message)
        webSocketClient.connection_status_changed.connect(self.on_connection_status_changed)

        # 布局设置
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(20)
        self.layout.addWidget(self.loginCard, 0, 0, 1, 1)
        self.layout.addWidget(self.messageList, 1, 0, 1, 1)
        self.setLayout(self.layout)

        # 初始化按钮状态
        self.update_login_button_state()

    def login_btn_clicked(self):
        # 检查当前连接状态，决定是登录还是退出
        if webSocketClient.get_connection_status():
            self.logout()
        else:
            self.login()

    def login(self):
        """执行登录操作"""
        if not self.account.text() or not self.password.text():
            webSocketClient.new_message.emit("错误|请输入完整的登录信息")
            return

        self.loginBtn.setText("登录中...")
        self.loginBtn.setEnabled(False)

        try:
            # 保存账号信息（如果用户选择了保存）
            self.save_account_info()

            success = webSocketClient.login_game(self.account.text(), self.password.text())
            if success:
                # 连接成功后，按钮状态会通过信号自动更新
                # 延迟显示赛尔号启动浮出控件，确保UI完全初始化
                QTimer.singleShot(100, self.showStartupFlyout)
            else:
                self.loginBtn.setText("登录失败")
                self.loginBtn.setEnabled(True)
                # 延迟重置按钮状态
                QTimer.singleShot(2000, self.update_login_button_state)
        except Exception as e:
            self.loginBtn.setText("登录失败")
            self.loginBtn.setEnabled(True)
            webSocketClient.new_message.emit(f"错误|登录异常: {str(e)}")
            # 延迟重置按钮状态
            QTimer.singleShot(2000, self.update_login_button_state)

    def logout(self):
        """执行退出登录操作"""
        self.loginBtn.setText("退出中...")
        self.loginBtn.setEnabled(False)

        try:
            success = webSocketClient.logout_game()
            if success:
                # 断开成功后，按钮状态会通过信号自动更新
                pass
            else:
                self.loginBtn.setText("退出失败")
                self.loginBtn.setEnabled(True)
                # 延迟重置按钮状态
                QTimer.singleShot(2000, self.update_login_button_state)
        except Exception as e:
            self.loginBtn.setText("退出失败")
            self.loginBtn.setEnabled(True)
            webSocketClient.new_message.emit(f"错误|退出异常: {str(e)}")
            # 延迟重置按钮状态
            QTimer.singleShot(2000, self.update_login_button_state)

    def load_saved_account_info(self):
        """加载保存的账号信息"""
        try:
            userid, password, save_password = config_manager.get_account_info()

            if userid:
                self.account.setText(userid)

            if save_password and password:
                self.password.setText(password)
                self.savePasswordSwitch.setChecked(True)

            # 加载服务器设置
            server = config_manager.get_setting('通用设置', 'server', '32')
            self.serverCombo.setCurrentText(f"{server}服")

        except Exception as e:
            webSocketClient.new_message.emit(f"错误|加载账号信息失败: {str(e)}")

    def save_account_info(self):
        """保存账号信息"""
        try:
            userid = self.account.text()
            password = self.password.text()
            save_password = self.savePasswordSwitch.isChecked()

            config_manager.save_account_info(userid, password, save_password)

            # 保存服务器设置
            server_text = self.serverCombo.currentText()
            server_num = server_text.replace('服', '')
            config_manager.set_setting('通用设置', 'server', server_num)

        except Exception as e:
            webSocketClient.new_message.emit(f"错误|保存账号信息失败: {str(e)}")

    def on_connection_status_changed(self, connected):
        """连接状态变化处理"""
        self.update_login_button_state()

        if connected:
            # 连接成功时的处理
            webSocketClient.new_message.emit("状态|已连接|游戏连接成功")
        else:
            # 断开连接时的处理
            webSocketClient.new_message.emit("状态|已断开|游戏连接断开")

    def update_login_button_state(self):
        """更新登录按钮状态"""
        if webSocketClient.get_connection_status():
            # 已连接状态 - 显示退出登录
            self.loginBtn.setText("退出登录")
            self.loginBtn.setIcon(FluentIcon.POWER_BUTTON)
            self.loginBtn.setEnabled(True)
            # 禁用输入框
            self.account.setEnabled(False)
            self.password.setEnabled(False)
            self.serverCombo.setEnabled(False)
            self.savePasswordSwitch.setEnabled(False)
        else:
            # 未连接状态 - 显示开始登录
            self.loginBtn.setText("开始登录")
            self.loginBtn.setIcon(FluentIcon.SEND)
            self.loginBtn.setEnabled(True)
            # 启用输入框
            self.account.setEnabled(True)
            self.password.setEnabled(True)
            self.serverCombo.setEnabled(True)
            self.savePasswordSwitch.setEnabled(True)

    def showStartupFlyout(self):
        """显示赛尔号启动浮出控件"""
        try:
            # 确保按钮存在且可见
            if self.loginBtn and self.loginBtn.isVisible():
                Flyout.create(
                    icon=InfoBarIcon.SUCCESS,
                    title='启动成功',
                    content="赛尔号启动！",
                    target=self.loginBtn,
                    parent=self,
                    isClosable=True  # 允许关闭
                )
            else:
                # 如果按钮不可用，使用简单的消息提示
                webSocketClient.new_message.emit("登录|成功|赛尔号启动成功！")
        except Exception as e:
            print(f"Flyout显示失败: {e}")
            # 备用方案：使用消息提示
            webSocketClient.new_message.emit("登录|成功|赛尔号启动成功！")



    def get_new_message(self, message):
        formatted_now = datetime.now().strftime("%m-%d %H:%M:%S")
        parts = message.split('|')
        row_position = self.messageList.rowCount()
        self.messageList.insertRow(row_position)
        self.messageList.setItem(row_position, 0, QTableWidgetItem(formatted_now))
        for i, part in enumerate(parts):
            if i + 1 < self.messageList.columnCount():
                self.messageList.setItem(row_position, i+1, QTableWidgetItem(part))
        
        # 自动滚动到最新消息
        self.messageList.scrollToBottom()

    def init_table(self):
        # 启用边框并设置圆角
        self.messageList.setBorderVisible(True)
        self.messageList.setBorderRadius(8)

        # 设置表格边距，确保边框显示
        self.messageList.setContentsMargins(2, 2, 2, 2)

        self.messageList.setWordWrap(False)
        self.messageList.setColumnCount(4)
        # 固定列宽
        self.messageList.setColumnWidth(0, 120)
        self.messageList.setColumnWidth(1, 100)
        self.messageList.setColumnWidth(2, 100)
        self.messageList.setColumnWidth(3, 500)

        self.messageList.setHorizontalHeaderLabels(['时间','类型', '状态', '详细信息'])
        self.messageList.verticalHeader().hide()

        # 设置表格样式
        self.messageList.setAlternatingRowColors(True)
