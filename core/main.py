import threading
import time
from function.Algorithms import Algorithms
from .Login import Login
from .SendPacketProcessing import SendPacketProcessing
from .ReceivePacketAnalysis import ReceivePacketAnalysis
from .PetFightPacketManager import PetFightPacketManager
from .config_manager import config_manager

class Main:
    def __init__(self):
        self.algorithms = Algorithms()
        self.login = Login(self.algorithms)
        self.tcp_socket = None
        self.send_packet_processing = None
        self.receive_packet_analysis = None

    def initialize(self, userid, password, message_callback=None, disconnect_callback=None):
        # 从配置中获取服务器设置
        server = int(config_manager.get_setting('通用设置', 'server', '32'))
        self.tcp_socket = self.login.login(userid, password, server)
        self.receive_packet_analysis = ReceivePacketAnalysis(self.algorithms, self.tcp_socket, userid, message_callback, disconnect_callback)
        self.send_packet_processing = SendPacketProcessing(self.algorithms, self.tcp_socket, userid, message_callback)
        self.pet_fight_packet_manager = PetFightPacketManager(self.send_packet_processing, self.receive_packet_analysis, message_callback)

    def start_receive_thread(self):
        """启动接收数据线程"""
        receive_thread = threading.Thread(target=self.receive_packet_analysis.receive_data, daemon=True)
        receive_thread.start()
        return receive_thread


    def apply_general_settings(self):
        if not self.pet_fight_packet_manager:
            return "请先登录并初始化"

        results = []
        try:
            # 应用能力装备
            capability_equipment = config_manager.get_setting('通用设置', 'capability_equipment', '装备1')
            self.pet_fight_packet_manager.set_capability_equipment(capability_equipment)
            results.append(f"能力装备设置为：{capability_equipment}")

            # 应用能力称号
            capability_title = config_manager.get_setting('通用设置', 'capability_title', '称号1')
            self.pet_fight_packet_manager.set_capability_title(capability_title)
            results.append(f"能力称号设置为：{capability_title}")

            # 设置自爆精灵
            self_destructing_elf = config_manager.get_setting('通用设置', 'self_destructing_elf', '帝皇之御')
            self.pet_fight_packet_manager.set_self_destructing_elf(self_destructing_elf)
            results.append(f"自爆精灵设置为：{self_destructing_elf}")

            # 设置弹伤精灵
            rebound_damage_elf = config_manager.get_setting('通用设置', 'rebound_damage_elf', '六界神王')
            self.pet_fight_packet_manager.set_rebound_damage_elf(rebound_damage_elf)
            results.append(f"弹伤精灵设置为：{rebound_damage_elf}")

            # 设置补刀精灵
            mending_blade_elf = config_manager.get_setting('通用设置', 'mending_blade_elf', '圣灵谱尼')
            self.pet_fight_packet_manager.set_mending_blade_elf(mending_blade_elf)
            results.append(f"补刀精灵设置为：{mending_blade_elf}")

        except Exception as e:
            results.append(f"应用通用设置时出错：{str(e)}")

        return "\n".join(results)

    def execute_daily_tasks(self):
        if not self.pet_fight_packet_manager:
            return "请先登录并初始化"

        daily_settings = config_manager.get_daily_settings()
        results = []

        tasks = [
            ('daily_check_in', '日常签到', self.pet_fight_packet_manager.daily_props_collection),
            ('a', '刻印抽奖', self.pet_fight_packet_manager.engraved_raffle_machine),
            ('b', 'VIP礼包', self.pet_fight_packet_manager.vip_package),
            ('c', '战队日常', self.pet_fight_packet_manager.team_contribution),
            ('d', '六界神王殿', None),
            ('e', '经验战场', self.pet_fight_packet_manager.experience_training_ground),
            ('f', '学习力战场', self.pet_fight_packet_manager.learning_training_ground),
            ('g', '勇者之塔', self.pet_fight_packet_manager.brave_tower),
            ('h', '泰坦矿洞', self.pet_fight_packet_manager.titan_mines),
            ('i', '泰坦源脉', self.pet_fight_packet_manager.titan_vein),
            ('j', '精灵王试炼', self.pet_fight_packet_manager.trial_of_the_elf_king),
            ('k', 'X战队密室', self.pet_fight_packet_manager.x_team_chamber),
            ('l', '星愿漂流瓶许愿', self.pet_fight_packet_manager.make_a_wish),
        ]

        for setting, task_name, task_function in tasks:
            if daily_settings.get(setting) != '禁止':
                try:
                    task_function()
                    results.append(f"{task_name}：√")
                except Exception as e:
                    results.append(f"{task_name}：× ({str(e)})")
                time.sleep(0.3)

        return "\n".join(results)

    def run(self, userid, password):
        self.initialize(userid, password)
        return self.start_receive_thread()
