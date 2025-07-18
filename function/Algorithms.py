import hashlib

class Algorithms:
    def __init__(self):
        self.key = b'!crAckmE4nOthIng:-)'  # 初始化 key
        self.result = 0  # 初始化 result

    def encrypt(self, plain: bytes) -> bytes:
        cipher_len = len(plain) + 1  # 计算封包长度（密文长度比明文长度大一）
        plain = plain[4:]  # 跳过前4个字节（封包长度）
        cipher = bytearray(len(plain) + 1)  # cipher 长度为 plain 长度 + 1
        # 加密操作
        j = 0
        need_become_zero = False
        for i in range(len(plain)):
            if j == 1 and need_become_zero:
                j = 0
                need_become_zero = False
            if j == len(self.key):
                j = 0
                need_become_zero = True
            cipher[i] = plain[i] ^ self.key[j]
            j += 1
        # 设置最后一个字节为0
        cipher[-1] = 0
        # 执行位操作变换
        for i in range(len(cipher) - 1, 0, -1):
            cipher[i] = ((cipher[i] << 5) & 0xFF) | (cipher[i - 1] >> 3)
        cipher[0] = ((cipher[0] << 5) & 0xFF) | 3
        # 计算旋转索引并进行数组旋转
        result = self.key[len(plain) % len(self.key)] * 13 % len(cipher)
        cipher = cipher[result:len(cipher)] + cipher[0:result]
        # 返回拼接封包长度与加密后的数据
        return cipher_len.to_bytes(length = 4, byteorder = 'big') + bytes(cipher)

    def decrypt(self, cipher: bytes) -> bytes:
        plain_len = len(cipher) - 1  # 计算封包长度（密文长度比明文长度大一）
        cipher = cipher[4:]  # 跳过前4个字节（封包长度）
        # 计算旋转索引
        result = self.key[(len(cipher) - 1) % len(self.key)] * 13 % len(cipher)
        # 进行数组旋转
        cipher = cipher[len(cipher) - result:len(cipher)] + cipher[0:len(cipher) - result]
        # 初始化明文字节数组
        plain = bytearray(len(cipher) - 1)
        # 进行位操作还原
        for i in range(len(cipher) - 1):
            plain[i] = ((cipher[i] >> 5) & 0xFF) | ((cipher[i + 1] << 3) & 0xFF)
        # 解密操作
        j = 0
        need_become_zero = False
        for i in range(len(plain)):
            if j == 1 and need_become_zero:
                j = 0
                need_become_zero = False
            if j == len(self.key):
                j = 0
                need_become_zero = True
            plain[i] = plain[i] ^ self.key[j]
            j += 1
        # 返回拼接封包长度与解密后的数据
        return plain_len.to_bytes(length = 4, byteorder = 'big') + bytes(plain)

    def InitKey(self, packet_data: bytes, userid: int):
        # 提取最后4个字节
        last_four_bytes = packet_data[-4:]
        # 将最后4个字节转换为无符号整数（大端）
        last_uint = int.from_bytes(last_four_bytes, byteorder = 'big')
        # 与米米号进行异或操作
        xor_result = last_uint ^ userid
        # 将异或结果转换为字符串
        xor_str = str(xor_result)
        # 计算字符串的MD5哈希值
        md5_hash = hashlib.md5(xor_str.encode()).hexdigest()
        # 取MD5哈希值的前10个字节作为新的通信密钥
        new_key = md5_hash[:10]
        # 更新新的通信密钥
        self.key = new_key.encode('utf-8')
        print("Updated encryption key to:", self.key)

    def MSerial(self, a, b, c, d):
        return a + c + int(a / -3) + (b % 17) + (d % 23) + 120

    def calculate_result(self, cmdId, body):
        crc8_val = 0
        if cmdId > 1000:  # 命令号大于1000的封包要计算序列号
            for byte in body:
                crc8_val ^= byte
        new_result = self.MSerial(self.result, len(body), crc8_val, cmdId)
        self.result = new_result
        print("Updated result to:", new_result)
        return new_result
