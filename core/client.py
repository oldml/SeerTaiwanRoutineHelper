# coding:utf-8
from PySide6.QtCore import QObject, Signal
import threading


class WebSocketClient(QObject):
    """WebSocket客户端，用于处理游戏通信和登录管理"""
    new_message = Signal(str)  # 新消息信号
    connection_status_changed = Signal(bool)  # 连接状态变化信号

    def __init__(self):
        super().__init__()
        self.is_connected = False
        self.main_instance = None
        self.current_userid = None

    def login_game(self, userid, password):
        """登录游戏"""
        try:
            # 转换userid为整数
            if isinstance(userid, str):
                userid = int(userid)

            # 导入Main类并创建实例
            from .main import Main
            self.main_instance = Main()

            # 尝试连接
            if self.connect_to_server(userid, password):
                self.new_message.emit(f"登录|成功|用户ID: {userid}")
                return True
            else:
                self.new_message.emit(f"登录|失败|用户ID: {userid}")
                return False

        except Exception as e:
            self.new_message.emit(f"登录|错误|{str(e)}")
            return False

    def logout_game(self):
        """退出登录"""
        try:
            if not self.is_connected:
                self.new_message.emit("退出|警告|当前未连接")
                return True

            if self.disconnect():
                self.new_message.emit("退出|成功|已断开连接")
                return True
            else:
                self.new_message.emit("退出|失败|断开连接失败")
                return False

        except Exception as e:
            self.new_message.emit(f"退出|错误|{str(e)}")
            return False

    def connect_to_server(self, userid, password):
        """连接到服务器"""
        try:
            if self.main_instance:
                # 传递消息回调函数和断开连接回调函数
                message_callback = lambda msg: self.new_message.emit(msg)
                disconnect_callback = self.handle_disconnect
                self.main_instance.initialize(userid, password, message_callback, disconnect_callback)
                self.is_connected = True
                self.current_userid = userid
                # 发送连接状态变化信号
                self.connection_status_changed.emit(True)
                # 启动接收线程
                self.start_receive_thread()
                return True
        except Exception as e:
            self.new_message.emit(f"连接|失败|{str(e)}")
            self.is_connected = False
            self.connection_status_changed.emit(False)
            return False

    def start_receive_thread(self):
        """启动接收数据线程"""
        if self.main_instance and self.main_instance.receive_packet_analysis:
            receive_thread = threading.Thread(
                target=self.receive_data_wrapper,
                daemon=True
            )
            receive_thread.start()

    def receive_data_wrapper(self):
        """接收数据包装器"""
        try:
            self.main_instance.receive_packet_analysis.receive_data()
        except Exception as e:
            self.new_message.emit(f"接收|错误|{str(e)}")
            # 接收错误时也要更新连接状态
            self.handle_disconnect()

    def handle_disconnect(self):
        """处理连接断开"""
        if self.is_connected:
            self.is_connected = False
            # 清理资源
            if self.main_instance and self.main_instance.tcp_socket:
                try:
                    self.main_instance.tcp_socket.close()
                except:
                    pass  # 忽略关闭时的错误
            self.current_userid = None
            self.main_instance = None
            # 发送状态变化信号
            self.connection_status_changed.emit(False)
            self.new_message.emit("状态|断开|连接已断开，请重新登录")

    def send_message(self, message):
        """发送消息"""
        if not (self.main_instance and self.main_instance.send_packet_processing):
            return False

        try:
            self.main_instance.send_packet_processing.SendPacket(message)
            self.new_message.emit(f"发送|{message[:20]}...")
            return True
        except Exception as e:
            self.new_message.emit(f"发送|错误|{str(e)}")
            return False

    def disconnect(self):
        """断开连接"""
        try:
            # 发送断开连接消息
            user_msg = f"登录|断开|用户ID: {self.current_userid}" if self.current_userid else "连接|断开|已断开连接"
            self.new_message.emit(user_msg)

            # 关闭TCP连接
            if self.main_instance and self.main_instance.tcp_socket:
                try:
                    self.main_instance.tcp_socket.close()
                except Exception as e:
                    self.new_message.emit(f"断开|错误|{str(e)}")

            # 重置状态
            self.is_connected = False
            self.current_userid = None
            self.main_instance = None
            self.connection_status_changed.emit(False)

            return True
        except Exception as e:
            self.new_message.emit(f"断开|错误|{str(e)}")
            return False

    def get_connection_status(self):
        """获取当前连接状态"""
        return self.is_connected

    def get_current_user(self):
        """获取当前登录用户"""
        return self.current_userid

    def get_main_instance(self):
        """获取当前的主实例"""
        return self.main_instance


# 全局WebSocket客户端实例
webSocketClient = WebSocketClient()
