import hashlib, requests, socket, struct
from function.Algorithms import Algorithms

class Login():
    def __init__(self, algorithms: Algorithms):
        self.algorithms = algorithms
        self.serverList = {
        1: 1241, 2: 1242, 3: 1243, 4: 1244, 5: 1245, 6: 1246, 7: 1247, 8: 1248, 9: 1249, 10: 1250, 
        11: 1251, 12: 1252, 13: 1253, 14: 1254, 15: 1255, 16: 1256, 17: 1257, 18: 1258, 19: 1259, 20: 1260, 
        21: 1221, 22: 1222, 23: 1223, 24: 1224, 25: 1225, 26: 1226, 27: 1227, 28: 1228, 29: 1229, 30: 1230, 
        31: 1231, 32: 1232, 33: 1233, 34: 1234, 35: 1235, 36: 1236, 37: 1237, 38: 1238, 39: 1239, 40: 1240
        }

    def login(self, userid, password, server=32):
        double_md5_password = self.double_md5(password)
        # 获取登录凭证
        recv_data = self.login_verify(userid, double_md5_password)
        recv_body = recv_data[21:37]
        userid_bytes =recv_data[9:13]
        try:
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_socket.connect(('210.68.8.39', self.serverList[server]))
            self.tcp_socket.send(self.LOGIN_IN(userid_bytes, recv_body))
            return self.tcp_socket
        except KeyboardInterrupt:
            if self.tcp_socket:
                self.tcp_socket.close()
            print('断开连接')

    def get_server_addr(self):
        url = r'http://seer.61.com.tw/config/ip.txt'
        r = requests.get(url)
        server_addr = r.text.split('|')[0].split(':')
        return (server_addr[0], int(server_addr[1]))

    def send_login_packet(self, server_addr, send_data):
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(server_addr)
        tcp_socket.connect(server_addr)
        tcp_socket.send(send_data)
        recv_data = tcp_socket.recv(1024)
        tcp_socket.close()
        return recv_data # 返回封包体

    @staticmethod
    def double_md5(password: str) -> str:
        # 计算第一次MD5哈希值
        first_md5 = hashlib.md5(password.encode()).hexdigest()
        # 计算第二次MD5哈希值
        second_md5 = hashlib.md5(first_md5.encode()).hexdigest()
        return second_md5

    def login_verify(self, userid, double_md5_password, verification_code_num = b'\x00' * 16, verification_code = b'\x00' * 4):
        packet = b'\x00\x00\x00\x931\x00\x00\x00g\t\xc0\xb6\xf7\x00\x00\x00\x00b47906b7958676b2b686a6ec61b1016c\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\xe3^\xbf{\x1dd\xc3\xca\xb6/D/;HI\xd9AAAA\x00\x00unknown\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        packet = packet[:9] + struct.pack('>I', userid) + packet[13:17] + double_md5_password.encode() + packet[49:61] + verification_code_num + verification_code + packet[81:]
        recv_data = self.send_login_packet(self.get_server_addr(), packet)
        recv_packet_body = recv_data[17:]
        if recv_packet_body[3] == 0:
            print('登录成功')
        elif recv_packet_body[3] == 1:
            print('密码错误')
        elif recv_packet_body[3] == 2:
            print('验证码错误')
            with open(r'验证码.bmp', 'wb')as f:
                f.write(recv_packet_body[24:])
            _verification_code_num = recv_packet_body[4:4+16]
            _verification_code = input('请查看保存在代码运行目录下的验证码图片并输入验证码：').encode()
            if len(_verification_code) == 4:
                self.login_verify(userid, double_md5_password, _verification_code_num, _verification_code)
        return recv_data

    def LOGIN_IN(self, userid_bytes, recv_body):
        recv_body = recv_body + b'0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        result = self.algorithms.calculate_result(1001, recv_body)
        packet_data = b'\x00\x00\x00a1\x00\x00\x03\xe9' + userid_bytes + result.to_bytes(length = 4, byteorder = 'big') + recv_body
        cipher = self.algorithms.encrypt(packet_data)
        return cipher
