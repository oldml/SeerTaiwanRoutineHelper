import json, threading
from function.Algorithms import Algorithms

class ReceivePacketAnalysis:
    def __init__(self, algorithms: Algorithms, tcp_socket, userid, message_callback=None, disconnect_callback=None):
        self.algorithms = algorithms
        self.tcp_socket = tcp_socket
        self.userid = userid
        self.message_callback = message_callback
        self.disconnect_callback = disconnect_callback  # 新增断开连接回调
        with open('function/Command.json', 'r') as file:
            self.command_dict = json.load(file)
        self.currentCommandId = None
        self.packet_data = None
        self.data_ready_event = threading.Event()  # 创建一个事件对象

    def receive_data(self):
        buffer = b''
        while True:
            try:
                if not self.tcp_socket:
                    if self.message_callback:
                        self.message_callback("连接|错误|未连接到服务器")
                    break

                recv_data = self.tcp_socket.recv(1024)
                if not recv_data:
                    if self.message_callback:
                        self.message_callback("连接|断开|服务器断开连接")
                    # 通知上层连接已断开
                    if self.disconnect_callback:
                        self.disconnect_callback()
                    break

                buffer += recv_data
                while len(buffer) >= 4:  # 至少要有4个字节来提取封包长度
                    packet_length = int.from_bytes(buffer[:4], byteorder = 'big')
                    if len(buffer) < packet_length:
                        break

                    packet_data = buffer[:packet_length]
                    buffer = buffer[packet_length:]

                    packet_data = self.algorithms.decrypt(packet_data)
                    cipher = packet_data.hex().upper()
                    formatted_hex_string = ' '.join([cipher[i:i+2] for i in range(0, len(cipher), 2)])
                    command_value = int.from_bytes(packet_data[5:9], byteorder = 'big')
                    command_str = self.command_dict.get(str(command_value), 'Unknown Command')
                    if self.message_callback:
                        self.message_callback(f"接收|{command_str}|{formatted_hex_string[:50]}...")

                    # 检查是否需要分析当前封包
                    if command_value == self.currentCommandId:
                        # print(f"需要分析的封包: {formatted_hex_string}")
                        self.packet_data = packet_data  # 返回封包数据以供主程序分析
                        self.data_ready_event.set()  # 设置事件为已触发，通知数据已准备好

                    if command_value == 1001:
                        self.algorithms.InitKey(packet_data, self.userid)
                        if self.message_callback:
                            self.message_callback("初始化|成功|密钥初始化完成")
                        result = int.from_bytes(packet_data[13:17], byteorder = 'big')
                        self.algorithms.result = result
                        if self.message_callback:
                            self.message_callback(f"初始化|更新|Result: {result}")
                        break

            except Exception as e:
                if self.message_callback:
                    self.message_callback(f"接收|错误|{str(e)}")
                # 异常时也通知上层连接已断开
                if self.disconnect_callback:
                    self.disconnect_callback()
                break

    def wait_for_specific_data(self, command_id, timeout = 5):
        self.currentCommandId = command_id
        self.data_ready_event.clear()
        if self.data_ready_event.wait(timeout):
            data = self.packet_data
            self.packet_data = None
            self.currentCommandId = None
            return data
        else:
            if self.message_callback:
                self.message_callback(f"等待|超时|命令 {command_id} 响应超时")
            return None