import time

class PetFightPacketManager:
    def __init__(self, send_packet_processing, receive_packet_analysis, message_callback=None):
        self.send_packet_processing = send_packet_processing
        self.receive_packet_analysis = receive_packet_analysis
        self.message_callback = message_callback
        # 存储精灵ID和对应时间戳的字典
        self.pet_timestamps = {}

    def check_backpack_pets(self, pet_ids):
        """检查背包里是否有指定的宠物"""
        self.send_packet_processing.SendPacket('00 00 00 11 31 00 00 AA BA 00 00 00 00 00 00 00 00')
        packet_data = self.receive_packet_analysis.wait_for_specific_data(43706, timeout = 3)
        # Step 1: 取出封包头 (前17字节)
        packet_body = packet_data[17:]
        # Step 2: 判断背包是否为空
        if packet_body == b'\x00\x00\x00\x00\x00\x00\x00\x00':
            if self.message_callback:
                self.message_callback("背包|检查|背包为空，调用仓库存取")
            self.check_warehouse_pets(pet_ids)  # 调用仓库存取函数
            return
        # Step 3: 提取宠物数量 (前4字节) 并转换为整数
        pet_count = int.from_bytes(packet_body[:4], byteorder = 'big')
        if self.message_callback:
            self.message_callback(f"背包|检查|宠物数量: {pet_count}")
        # Step 4: 解析宠物信息，每只宠物占用390个字节
        pet_data_start = 4  # 宠物数据从第5个字节开始
        pet_data_length = 390  # 每只宠物信息占用390字节
        for i in range(pet_count):
            pet_data = packet_body[pet_data_start:pet_data_start + pet_data_length]
            pet_id = int.from_bytes(pet_data[:4], byteorder = 'big')  # 宠物ID在宠物数据的前4个字节
            # 提取时间戳 (假设时间戳在148-152字节处，4字节)
            timestamp_bytes = pet_data[148:152]
            timestamp = int.from_bytes(timestamp_bytes, byteorder = 'big')

            # 保存精灵时间戳到字典中
            self.pet_timestamps[pet_id] = timestamp_bytes.hex().upper()

            if self.message_callback:
                self.message_callback(f"背包|精灵|ID:{pet_id} 时间戳:{timestamp} 十六进制:{timestamp_bytes.hex().upper()}")
            self.send_packet_processing.SendPacket('00 00 00 19 31 00 00 09 00 00 00 00 00 00 00 00 00' + timestamp_bytes.hex().upper() + '00 00 00 00')
            pet_data_start += pet_data_length
        self.check_warehouse_pets(pet_ids)  # 调用仓库存取函数

    def check_warehouse_pets(self, pet_ids):
        """检查仓库里是否有指定的宠物，并返回对应的时间戳列表"""
        self.send_packet_processing.SendPacket('00 00 00 19 31 00 00 B1 E7 00 00 00 00 00 00 00 00 00 00 00 00 00 00 03 E7')
        packet_data = self.receive_packet_analysis.wait_for_specific_data(45543, timeout = 3)
        for pet_id in pet_ids:
            pet_id_hex = pet_id.to_bytes(4, byteorder = 'big').hex()
            pet_found = False
            # 从切片后的数据中找到与精灵ID匹配的时间戳
            for i in range(len(packet_data) - 8):
                current_id = packet_data[i:i+4]
                if current_id == bytes.fromhex(pet_id_hex):
                    pet_found = True
                    # 时间戳位于精灵ID的后四个字节
                    timestamp = packet_data[i+4:i+8]

                    # 保存精灵时间戳到字典中
                    self.pet_timestamps[pet_id] = timestamp.hex().upper()

                    if self.message_callback:
                        self.message_callback(f"仓库|精灵|ID:{pet_id} 时间戳:{int.from_bytes(timestamp, byteorder = 'big')} 十六进制:{timestamp.hex().upper()}")
                    self.send_packet_processing.SendPacket('00 00 00 19 31 00 00 09 00 00 00 00 00 00 00 00 00' + timestamp.hex().upper() + '00 00 00 01')
                    break
            if not pet_found:
                if self.message_callback:
                    self.message_callback(f"仓库|错误|精灵 {pet_id} 未找到")
                return None

    def get_pet_timestamp(self, pet_id, default_timestamp="00000000"):
        """获取精灵的时间戳，如果没有找到则返回默认值"""
        return self.pet_timestamps.get(pet_id, default_timestamp)

    def clear_pet_timestamps(self):
        """清空精灵时间戳缓存"""
        self.pet_timestamps.clear()

    def get_all_pet_timestamps(self):
        """获取所有已保存的精灵时间戳"""
        return self.pet_timestamps.copy()

    def daily_props_collection(self):
        data =  (
            # 星愿漂流瓶签到
            '00 00 00 19 31 00 00 B8 BE 00 00 00 00 00 00 00 00 00 00 00 09 00 00 00 01',
            '00 00 00 19 31 00 00 B8 BE 00 00 00 00 00 00 00 00 00 00 00 09 00 00 00 02',
            '00 00 00 19 31 00 00 B8 BE 00 00 00 00 00 00 00 00 00 00 00 09 00 00 00 03',
            '00 00 00 19 31 00 00 B8 BE 00 00 00 00 00 00 00 00 00 00 00 09 00 00 00 04',
            '00 00 00 19 31 00 00 B8 BE 00 00 00 00 00 00 00 00 00 00 00 09 00 00 00 05',
            '00 00 00 19 31 00 00 B8 BE 00 00 00 00 00 00 00 00 00 00 00 09 00 00 00 06',
            '00 00 00 19 31 00 00 B8 BE 00 00 00 00 00 00 00 00 00 00 00 09 00 00 00 07',
            # 荣誉大厅军阶商店签到
            '00 00 00 19 31 00 00 A5 8C 00 00 00 00 00 00 00 00 00 00 00 04 00 00 00 04',
            # 勇者之塔扫荡
            '00 00 00 15 31 00 00 A2 EC 00 00 00 00 00 00 00 00 00 00 00 01',

            '00 00 00 1D 31 00 00 B0 2E 00 00 00 00 00 00 00 00 00 00 00 01 5F 65 68 B7 00 00 00 00',
            # 全面药
            '00 00 00 15 31 00 00 B2 36 00 00 00 00 00 00 00 00 00 00 00 01',
            '00 00 00 15 31 00 00 B2 36 00 00 00 00 00 00 00 00 00 00 00 02',
            '00 00 00 15 31 00 00 B2 36 00 00 00 00 00 00 00 00 00 00 00 03',
            '00 00 00 15 31 00 00 B2 36 00 00 00 00 00 00 00 00 00 00 00 04',
            '00 00 00 15 31 00 00 B2 36 00 00 00 00 00 00 00 00 00 00 00 05',
            '00 00 00 15 31 00 00 B2 36 00 00 00 00 00 00 00 00 00 00 00 01',
            '00 00 00 15 31 00 00 B2 36 00 00 00 00 00 00 00 00 00 00 00 02',
            '00 00 00 15 31 00 00 B2 36 00 00 00 00 00 00 00 00 00 00 00 03',
            '00 00 00 15 31 00 00 B2 36 00 00 00 00 00 00 00 00 00 00 00 04',
            '00 00 00 15 31 00 00 B2 36 00 00 00 00 00 00 00 00 00 00 00 05',
            '00 00 00 15 31 00 00 B2 36 00 00 00 00 00 00 00 00 00 00 00 01',
            '00 00 00 15 31 00 00 B2 36 00 00 00 00 00 00 00 00 00 00 00 02',
            '00 00 00 15 31 00 00 B2 36 00 00 00 00 00 00 00 00 00 00 00 03',
            '00 00 00 15 31 00 00 B2 36 00 00 00 00 00 00 00 00 00 00 00 04',
            '00 00 00 15 31 00 00 B2 36 00 00 00 00 00 00 00 00 00 00 00 05',
            # 王萨签到
            '00 00 00 19 31 00 00 B4 EB 00 00 00 00 00 00 00 00 00 00 00 0B 00 00 00 00',
            # 爬哈签到
            '00 00 00 15 31 00 00 B2 35 00 00 00 00 00 00 00 00 00 00 00 01',
        )

        for i in data:
            self.send_packet_processing.SendPacket(i)
            time.sleep(0.3)

    def engraved_raffle_machine(self):
        data = (
            # 刻印抽奖机
            '00 00 00 19 31 00 00 B4 DD 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 00',
        )

        self.send_packet_processing.SendPacket(data[0])

    def vip_package(self):
        data = (
            # VIP相关
            '00 00 00 15 31 00 00 A5 08 00 00 00 00 00 00 00 00 00 00 00 01',
            '00 00 00 15 31 00 00 A2 2E 00 00 00 00 00 00 00 00 00 00 00 01',
            '00 00 00 15 31 00 00 A2 2E 00 00 00 00 00 00 00 00 00 00 00 02',
            '00 00 00 15 31 00 00 A2 2E 00 00 00 00 00 00 00 00 00 00 00 03',
            '00 00 00 11 31 00 00 B4 82 00 00 00 00 00 00 00 00',
            '00 00 00 15 31 00 00 B4 83 00 00 00 00 00 00 00 00 00 00 00 01',
        )

        for i in data:
            self.send_packet_processing.SendPacket(i)
            time.sleep(0.3)

    def team_contribution(self):
        data = (
            # 战队贡献
            '00 00 00 19 31 00 00 24 8E 00 00 00 00 00 00 00 00 00 00 00 02 00 00 00 00',
            '00 00 00 19 31 00 00 24 8E 00 00 00 00 00 00 00 00 00 00 00 02 00 00 00 00',
            '00 00 00 19 31 00 00 24 8E 00 00 00 00 00 00 00 00 00 00 00 02 00 00 00 00',
            '00 00 00 19 31 00 00 24 8E 00 00 00 00 00 00 00 00 00 00 00 02 00 00 00 00',
            '00 00 00 19 31 00 00 24 8E 00 00 00 00 00 00 00 00 00 00 00 02 00 00 00 00',
        )

        for i in data:
            self.send_packet_processing.SendPacket(i)
            time.sleep(0.3)

    def make_a_wish(self):
        data = (
            # 星愿漂流瓶许愿培养道具
            '00 00 00 19 31 00 00 A9 35 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 04',
        )

        for i in range(10):
            self.send_packet_processing.SendPacket(data[0])
            time.sleep(0.3)

    def experience_training_ground(self):
        data =  (
            '00 00 00 1D 31 00 00 A5 9C 00 00 00 00 00 00 00 00 00 00 00 67 00 00 00 06 00 00 00 01',
            '00 00 00 1D 31 00 00 A5 9C 00 00 00 00 00 00 00 00 00 00 00 67 00 00 00 06 00 00 00 02',
            '00 00 00 1D 31 00 00 A5 9C 00 00 00 00 00 00 00 00 00 00 00 67 00 00 00 06 00 00 00 03',
            '00 00 00 1D 31 00 00 A5 9C 00 00 00 00 00 00 00 00 00 00 00 67 00 00 00 06 00 00 00 04',
            '00 00 00 1D 31 00 00 A5 9C 00 00 00 00 00 00 00 00 00 00 00 67 00 00 00 06 00 00 00 05',
            '00 00 00 1D 31 00 00 A5 9C 00 00 00 00 00 00 00 00 00 00 00 67 00 00 00 06 00 00 00 06'
        )

        c = 0
        while c < 6:
            for i in data:
                self.send_packet_processing.SendPacket(i)
                time.sleep(0.3)
                for j in self.fight_84_packets():
                    self.send_packet_processing.SendPacket(j)
                    time.sleep(0.3)
            c += 1
        time.sleep(0.3)
        self.send_packet_processing.SendPacket('00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 67 00 00 00 03 00 00 00 00 00 00 00 00')

    def learning_training_ground(self):
        data =  (
            '00 00 00 1D 31 00 00 A5 9C 00 00 00 00 00 00 00 00 00 00 00 66 00 00 00 06 00 00 00 01',
            '00 00 00 1D 31 00 00 A5 9C 00 00 00 00 00 00 00 00 00 00 00 66 00 00 00 06 00 00 00 02',
            '00 00 00 1D 31 00 00 A5 9C 00 00 00 00 00 00 00 00 00 00 00 66 00 00 00 06 00 00 00 03',
            '00 00 00 1D 31 00 00 A5 9C 00 00 00 00 00 00 00 00 00 00 00 66 00 00 00 06 00 00 00 04',
            '00 00 00 1D 31 00 00 A5 9C 00 00 00 00 00 00 00 00 00 00 00 66 00 00 00 06 00 00 00 05'
        )

        c = 0
        while c < 6:
            for i in data:
                self.send_packet_processing.SendPacket(i)
                time.sleep(0.3)
                for j in self.fight_84_packets():
                    self.send_packet_processing.SendPacket(j)
                    time.sleep(0.3)
            c += 1
        time.sleep(0.3)
        self.send_packet_processing.SendPacket('00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 66 00 00 00 03 00 00 00 00 00 00 00 00')

    def trial_of_the_elf_king(self):
        data =  (
            '00 00 00 1D 31 00 00 A5 9C 00 00 00 00 00 00 00 00 00 00 00 6A 00 00 00 0F 00 00 00 03'
        )

        c = 0
        while c < 15:
            self.send_packet_processing.SendPacket(data)
            time.sleep(0.3)
            for j in self.fight_84_packets():
                self.send_packet_processing.SendPacket(j)
                time.sleep(0.3)
            c += 1

    def x_team_chamber(self):
        data =  (
            #开启副本
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 69 00 00 00 01 00 00 00 01 00 00 00 00',
            #开启挑战
            '00 00 00 1D 31 00 00 A5 9C 00 00 00 00 00 00 00 00 00 00 00 69 00 00 00 07 00 00 00 00',
            #通关奖励
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 69 00 00 00 02 00 00 00 00 00 00 00 00'
        )

        c = 0
        while c < 3:
            self.send_packet_processing.SendPacket(data[0])
            time.sleep(0.3)
            self.send_packet_processing.SendPacket(data[1])
            time.sleep(0.3)
            for j in self.fight_84_packets():
                self.send_packet_processing.SendPacket(j)
                time.sleep(0.3)
            c += 1
        time.sleep(0.3)
        self.send_packet_processing.SendPacket(data[2])

    def brave_tower(self):
        data =  (
            '00 00 00 15 31 00 00 09 6E 00 00 00 00 00 00 00 00 00 00 00 00',
            '00 00 00 11 31 00 00 09 6F 00 00 00 00 00 00 00 00'
        )

        self.send_packet_processing.SendPacket(data[0])
        packet_data = self.receive_packet_analysis.wait_for_specific_data(2414, timeout = 3)
        packet_body = packet_data[17:]
        count = 80 - int.from_bytes(packet_body[:4], byteorder = 'big')
        bar_length = 10
        self.send_packet_processing.SendPacket('00 00 00 11 31 00 00 B8 20 00 00 00 00 00 00 00 00')
        time.sleep(0.3)
        for i in range(count):
            progress = i / count
            bar = '>' * int(progress * bar_length)
            # print(f'当前进度: [{bar:<{bar_length}}] {int(progress * 100)}%')
            if self.message_callback:
                self.message_callback(f'勇者之塔|进度|[{bar:<{bar_length}}] {i + 1}/{count}')
            self.send_packet_processing.SendPacket(data[1])
            if not self.receive_packet_analysis.wait_for_specific_data(2503, timeout = 1):
                self.send_packet_processing.SendPacket(data[1])
            time.sleep(0.3)
            for j in self.fight_aggressive_packets():
                self.send_packet_processing.SendPacket(j)
                time.sleep(0.3)

    def titan_mines(self):
        data = (
            # 难度选择：简单
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 01 00 00 00 01 00 00 00 00',
            # 难度选择：普通
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 01 00 00 00 02 00 00 00 00',
            # 难度选择：困难
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 01 00 00 00 03 00 00 00 00',
            # 以下为困难难度的关卡封包
            # 打开通道，击败守卫
            '00 00 00 1D 31 00 00 A5 9C 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 03 00 00 00 01',
            # 清扫矿区，16次
            '00 00 00 1D 31 00 00 A5 9C 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 03 00 00 00 02',
            # 矿洞开采
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 02 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 03 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 04 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 05 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 06 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 07 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 08 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 09 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 0A 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 0B 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 16 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 15 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 14 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 13 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 12 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 11 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 10 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 0F 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 0E 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 1D 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 1C 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 17 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 18 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 19 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 1A 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 1B 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 1C 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 1D 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 1E 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 1F 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 20 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 21 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 2C 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 2B 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 2A 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 29 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 28 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 27 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 26 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 25 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 24 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 23 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 22 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 2D 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 2E 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 2F 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 30 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 31 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 32 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 33 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 34 00 00 00 00',
            '00 00 00 21 31 00 00 A5 9B 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 02 00 00 00 35 00 00 00 00',
            # 安全撤离
            '00 00 00 1D 31 00 00 A5 9C 00 00 00 00 00 00 00 00 00 00 00 68 00 00 00 03 00 00 00 04',
        )

        self.send_packet_processing.SendPacket(data[2])  # 困难模式
        time.sleep(0.3)
        # 第一关
        self.send_packet_processing.SendPacket(data[3])
        if not self.receive_packet_analysis.wait_for_specific_data(2503, timeout = 1):
                self.send_packet_processing.SendPacket(data[3])
        time.sleep(0.3)
        for j in self.fight_84_packets():
            self.send_packet_processing.SendPacket(j)
            time.sleep(0.3)
        # 第二关
        time.sleep(0.3)
        pet_ids_needed = (3437, )
        self.check_backpack_pets(pet_ids_needed)
        time.sleep(0.3)
        self.send_packet_processing.SendPacket('00 00 00 6D 31 00 00 B3 DE 00 00 00 00 00 00 00 00 00 00 00 16 00 01 A6 1B 00 00 49 24 00 00 49 25 00 00 49 26 00 00 49 27 00 00 49 28 00 00 49 29 00 00 49 2A 00 00 49 2B 00 00 49 2C 00 00 49 2D 00 00 49 2E 00 00 49 2F 00 00 49 30 00 00 49 31 00 00 49 32 00 00 49 33 00 00 49 34 00 00 49 35 00 00 49 36 00 00 49 37 00 00 49 3C')
        packet_data = self.receive_packet_analysis.wait_for_specific_data(46046, timeout = 3)[17:]
        count = 16 - int(packet_data[19])
        bar_length = 10
        for i in range(count + 1):
            progress = i / count
            bar = '>' * int(progress * bar_length)
            if self.message_callback:
                self.message_callback(f'泰坦矿洞|进度|[{bar:<{bar_length}}] {int(progress * 100)}%')
            self.send_packet_processing.SendPacket(data[4])
            if not self.receive_packet_analysis.wait_for_specific_data(2503, timeout = 1):
                self.send_packet_processing.SendPacket(data[4])
            time.sleep(0.3)
            # 载入战斗
            self.send_packet_processing.SendPacket('00 00 00 11 31 00 00 09 64 00 00 00 00 00 00 00 00')
            time.sleep(0.3)
            # 艾欧使用有女初长成
            self.send_packet_processing.SendPacket('00 00 00 15 31 00 00 09 65 00 00 00 00 00 00 00 00 00 00 79 8C')
            time.sleep(0.3)
            # 艾欧使用有女初长成
            self.send_packet_processing.SendPacket('00 00 00 15 31 00 00 09 65 00 00 00 00 00 00 00 00 00 00 79 8C')
            time.sleep(0.3)
            # 发包逃跑，以防万一（防止的情况是出现了意料之外的情况导致我方和对方精灵都还没死，如果不发逃跑包就会卡死在对战里）
            self.send_packet_processing.SendPacket('00 00 00 11 31 00 00 09 6A 00 00 00 00 00 00 00 00')
            # 回血
            self.send_packet_processing.SendPacket('00 00 00 11 31 00 00 B8 20 00 00 00 00 00 00 00 00')
        # 第三关
        for i in range(5, 57):
            self.send_packet_processing.SendPacket(data[i])
            time.sleep(0.3)
        # 第四关
        time.sleep(0.3)
        pet_ids_needed = (3512, 3437, 3045)
        self.check_backpack_pets(pet_ids_needed)
        time.sleep(0.3)
        self.send_packet_processing.SendPacket(data[-1])
        if not self.receive_packet_analysis.wait_for_specific_data(2503, timeout = 1):
            self.send_packet_processing.SendPacket(data[-1])
        time.sleep(0.3)
        for j in self.fight_84_packets():
            self.send_packet_processing.SendPacket(j)
            time.sleep(0.3)

    def titan_vein(self):
        data = (
            # 难度选择：一般模式
            '00 00 00 21 31 00 00 B4 C4 00 00 00 00 00 00 00 00 00 00 00 0C 00 00 00 02 00 00 00 00 00 00 00 00',
            # 第一关
            '00 00 00 15 31 00 00 A0 A9 00 00 00 00 00 00 00 00 00 00 23 76',
            # 第二关
            '00 00 00 15 31 00 00 A0 A9 00 00 00 00 00 00 00 00 00 00 20 84',
            # 第四关
            '00 00 00 15 31 00 00 A0 A9 00 00 00 00 00 00 00 00 00 00 20 86',
            '00 00 00 15 31 00 00 A0 A9 00 00 00 00 00 00 00 00 00 00 20 87',
            '00 00 00 15 31 00 00 A0 A9 00 00 00 00 00 00 00 00 00 00 20 88',
            '00 00 00 15 31 00 00 A0 A9 00 00 00 00 00 00 00 00 00 00 20 89',
            '00 00 00 15 31 00 00 A0 A9 00 00 00 00 00 00 00 00 00 00 20 8A',
        )

        pet_ids_needed = (3512, 3437, 3045)
        self.check_backpack_pets(pet_ids_needed)
        time.sleep(0.3)
        self.send_packet_processing.SendPacket(data[0])
        time.sleep(0.3)
        # 第一关
        # self.send_packet_processing.SendPacket(data[1])
        # if not self.receive_packet_analysis.wait_for_specific_data(2503, timeout = 1):
        #         self.send_packet_processing.SendPacket(data[1])
        # time.sleep(0.3)
        # for j in self.fight_84_packets():
        #     self.send_packet_processing.SendPacket(j)
        #     time.sleep(0.3)
        # 第二关
        self.send_packet_processing.SendPacket(data[2])
        if not self.receive_packet_analysis.wait_for_specific_data(2503, timeout = 1):
                self.send_packet_processing.SendPacket(data[2])
        time.sleep(0.3)
        for j in self.fight_84_packets():
            self.send_packet_processing.SendPacket(j)
            time.sleep(0.3)
        # 第三关
        # for i in range(5, 57):
        #     self.send_packet_processing.SendPacket(data[i])
        #     time.sleep(0.3)
        # 第四关
        # time.sleep(0.3)
        # pet_ids_needed = (3437, )
        # self.check_backpack_pets(pet_ids_needed)
        # time.sleep(0.3)
        # count = 5
        # bar_length = 10
        # for i in range(count + 1):
        #     progress = i / count
        #     bar = '>' * int(progress * bar_length)
        #     print(f'当前进度: [{bar:<{bar_length}}] {int(progress * 100)}%')
        #     self.send_packet_processing.SendPacket(data[4])
        #     if not self.receive_packet_analysis.wait_for_specific_data(2503, timeout = 1):
        #         self.send_packet_processing.SendPacket(data[4])
        #     time.sleep(0.3)
        #     # 载入战斗
        #     self.send_packet_processing.SendPacket('00 00 00 11 31 00 00 09 64 00 00 00 00 00 00 00 00')
        #     time.sleep(0.3)
        #     # 艾欧使用有女初长成
        #     self.send_packet_processing.SendPacket('00 00 00 15 31 00 00 09 65 00 00 00 00 00 00 00 00 00 00 79 8C')
        #     time.sleep(0.3)
        #     # 艾欧使用有女初长成
        #     self.send_packet_processing.SendPacket('00 00 00 15 31 00 00 09 65 00 00 00 00 00 00 00 00 00 00 79 8C')
        #     time.sleep(0.3)
        #     # 发包逃跑，以防万一（防止的情况是出现了意料之外的情况导致我方和对方精灵都还没死，如果不发逃跑包就会卡死在对战里）
        #     self.send_packet_processing.SendPacket('00 00 00 11 31 00 00 09 6A 00 00 00 00 00 00 00 00')
        #     # 回血
        #     self.send_packet_processing.SendPacket('00 00 00 11 31 00 00 B8 20 00 00 00 00 00 00 00 00')

    def diandeng(self):
        return (
            '00 00 00 15 31 00 00 A0 A9 00 00 00 00 00 00 00 00 00 00 29 44',
            '00 00 00 15 31 00 00 A0 A9 00 00 00 00 00 00 00 00 00 00 29 45',
        )

    def pony_last(self):
        c = 0
        while c < 1000:
            self.send_packet_processing.SendPacket('00 00 00 15 31 00 00 A0 A9 00 00 00 00 00 00 00 00 00 00 29 46')
            time.sleep(0.3)
            for j in self.fight_84_packets():
                self.send_packet_processing.SendPacket(j)
                time.sleep(0.3)
            c += 1

    def hamo(self):
        c = 0
        while c < 20:
            self.send_packet_processing.SendPacket('00 00 00 15 31 00 00 A0 A9 00 00 00 00 00 00 00 00 00 00 19 59 ')
            time.sleep(0.3)
            for j in self.fight_84_packets():
                self.send_packet_processing.SendPacket(j)
                time.sleep(0.3)
            c += 1

    def prepare_packets(self, battle_type):
        """根据战斗类型准备封包"""
        if battle_type == "84":
            self.packets = self.fight_84_packets()
        elif battle_type == "aggressive":
            self.packets = self.fight_aggressive_packets()
        elif battle_type == "battlefield":
            self.packets = self.fight_battlefield_packets()
        else:
            raise ValueError(f"Unknown battle type: {battle_type}")

    def fight_84_packets(self):
        # 根据常用的精灵ID推测：
        # 3437 可能是艾欧 (从代码中看经常单独使用)
        # 其他精灵ID需要根据实际情况确定
        # 这里使用默认的硬编码时间戳作为后备

        # 获取动态时间戳，如果没有找到则使用原来的硬编码值
        liujie_timestamp = self.get_pet_timestamp(3045, "66AB2705")  # 假设3045是六界
        aio_timestamp = self.get_pet_timestamp(3437, "6690B4A1")     # 假设3437是艾欧

        if self.message_callback:
            self.message_callback(f"战斗|时间戳|六界(3045):{liujie_timestamp} 艾欧(3437):{aio_timestamp}")

        return (
            # 载入战斗
            '00 00 00 11 31 00 00 09 64 00 00 00 00 00 00 00 00',
            # 首发表姐，使用守御八方
            '00 00 00 15 31 00 00 09 65 00 00 00 00 00 00 00 00 00 00 7B 11',
            # 切换六界 (使用动态时间戳)
            f'00 00 00 15 31 00 00 09 67 00 00 00 00 00 00 00 00 {liujie_timestamp}',
            # 六界使用剑挥四方
            '00 00 00 15 31 00 00 09 65 00 00 00 00 00 00 00 00 00 00 4B 72',
            # 切换艾欧 (使用动态时间戳)
            f'00 00 00 15 31 00 00 09 67 00 00 00 00 00 00 00 00 {aio_timestamp}',
            # 艾欧使用有女初长成
            '00 00 00 15 31 00 00 09 65 00 00 00 00 00 00 00 00 00 00 79 8C',
            # 艾欧使用有女初长成
            '00 00 00 15 31 00 00 09 65 00 00 00 00 00 00 00 00 00 00 79 8C',
            # 艾欧使用有女初长成
            '00 00 00 15 31 00 00 09 65 00 00 00 00 00 00 00 00 00 00 79 8C',
            # 发包逃跑，以防万一（防止的情况是出现了意料之外的情况导致我方和对方精灵都还没死，如果不发逃跑包就会卡死在对战里）
            '00 00 00 11 31 00 00 09 6A 00 00 00 00 00 00 00 00',
            # 回血
            '00 00 00 11 31 00 00 B8 20 00 00 00 00 00 00 00 00',
        )

    def fight_aggressive_packets(self):
        """创建强攻类型的封包"""
        return (
            # 载入战斗
            '00 00 00 11 31 00 00 09 64 00 00 00 00 00 00 00 00',
            # 设置首发
            # '00 00 00 15 31 00 00 09 04 00 00 00 00 00 00 00 00 66 90 B4 A1',
            # 艾欧使用疾击之刺
            '00 00 00 15 31 00 00 09 65 00 00 00 00 00 00 00 00 00 00 79 8A',
            # 艾欧使用冰魄风暴
            '00 00 00 15 31 00 00 09 65 00 00 00 00 00 00 00 00 00 00 64 42',
            # 艾欧使用有女初长成
            '00 00 00 15 31 00 00 09 65 00 00 00 00 00 00 00 00 00 00 79 8C',
            # 艾欧使用疾击之刺
            '00 00 00 15 31 00 00 09 65 00 00 00 00 00 00 00 00 00 00 79 8A',
            # 艾欧使用冰魄风暴
            '00 00 00 15 31 00 00 09 65 00 00 00 00 00 00 00 00 00 00 64 42',
            # 艾欧使用有女初长成
            '00 00 00 15 31 00 00 09 65 00 00 00 00 00 00 00 00 00 00 79 8C',
            # 艾欧使用疾击之刺
            '00 00 00 15 31 00 00 09 65 00 00 00 00 00 00 00 00 00 00 79 8A',
            # 艾欧使用冰魄风暴
            '00 00 00 15 31 00 00 09 65 00 00 00 00 00 00 00 00 00 00 64 42',
            # 艾欧使用有女初长成
            '00 00 00 15 31 00 00 09 65 00 00 00 00 00 00 00 00 00 00 79 8C',
            # 艾欧使用疾击之刺
            '00 00 00 15 31 00 00 09 65 00 00 00 00 00 00 00 00 00 00 79 8A',
            # 艾欧使用冰魄风暴
            '00 00 00 15 31 00 00 09 65 00 00 00 00 00 00 00 00 00 00 64 42',
            # 艾欧使用有女初长成
            '00 00 00 15 31 00 00 09 65 00 00 00 00 00 00 00 00 00 00 79 8C',
            # 艾欧使用疾击之刺
            '00 00 00 15 31 00 00 09 65 00 00 00 00 00 00 00 00 00 00 79 8A',
            # 艾欧使用冰魄风暴
            '00 00 00 15 31 00 00 09 65 00 00 00 00 00 00 00 00 00 00 64 42',
            # 艾欧使用有女初长成
            '00 00 00 15 31 00 00 09 65 00 00 00 00 00 00 00 00 00 00 79 8C',
            # 发包逃跑，以防万一（防止的情况是出现了意料之外的情况导致我方和对方精灵都还没死，如果不发逃跑包就会卡死在对战里）
            '00 00 00 11 31 00 00 09 6A 00 00 00 00 00 00 00 00',
            # 回血
            '00 00 00 11 31 00 00 B8 20 00 00 00 00 00 00 00 00',
        )

    def fight_battlefield_packets(self):
        """创建战场类型的封包"""
        return ["Packet1_Battlefield", "Packet2_Battlefield", "Packet3_Battlefield"]

    def fire_buffer(self):
        self.send_packet_processing.SendPacket('00 00 00 15 31 00 00 10 C4 00 00 00 00 00 00 00 00 02 63 43 9C')
        self.send_packet_processing.SendPacket('00 00 00 15 31 00 00 10 C4 00 00 00 00 00 00 00 00 02 2B F9 3F')

    def battery_dormant_switch(self):
        self.send_packet_processing.SendPacket('00 00 00 15 31 00 00 A0 CA 00 00 00 00 00 00 00 00 00 00 00 00')