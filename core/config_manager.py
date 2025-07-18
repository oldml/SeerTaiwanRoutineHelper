# coding:utf-8
import configparser
import base64
import os
from typing import Optional, Tuple


class ConfigManager:
    """配置管理器，处理配置文件的读取、保存和密码加密"""
    
    def __init__(self, config_file='config.ini'):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file, encoding='utf-8')
        else:
            # 如果配置文件不存在，创建默认配置
            self.create_default_config()
    
    def create_default_config(self):
        """创建默认配置"""
        self.config['账号信息'] = {
            'userid': '',
            'password': '',
            'save_password': 'False'
        }
        
        self.config['通用设置'] = {
            'mending_blade_elf': '圣灵谱尼',
            'battle_delay': '1',
            'debug_mode': 'False',
            'auto_battle': 'False',
            'server': '32',
            'log_level': 'INFO',
            'max_retry': '3',
            'capability_equipment': '装备1',
            'capability_title': '称号1',
            'self_destructing_elf': '帝皇之御',
            'rebound_damage_elf': '六界神王'
        }
        
        self.config['日常设置'] = {
            'a': '禁止',
            'b': '禁止',
            'c': '禁止',
            'd': '禁止',
            'e': '启用',
            'f': '禁止',
            'g': '禁止',
            'h': '禁止',
            'i': '禁止',
            'j': '禁止',
            'k': '禁止',
            'l': '禁止',
            'daily_check_in': '禁止'
        }
        
        self.config['任务设置'] = {
            '执行间隔': '1',
            '重试次数': '2',
            '自动停止': 'False'
        }
        
        self.save_config()
    
    def save_config(self):
        """保存配置到文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)
    
    def _simple_encrypt(self, text: str) -> str:
        """简单的密码加密（Base64编码）"""
        if not text:
            return ''
        return base64.b64encode(text.encode('utf-8')).decode('utf-8')
    
    def _simple_decrypt(self, encrypted_text: str) -> str:
        """简单的密码解密（Base64解码）"""
        if not encrypted_text:
            return ''
        try:
            return base64.b64decode(encrypted_text.encode('utf-8')).decode('utf-8')
        except:
            return ''
    
    def get_account_info(self) -> Tuple[str, str, bool]:
        """获取账号信息

        Returns:
            Tuple[str, str, bool]: (userid, password, save_password)
        """
        if '账号信息' not in self.config:
            return '', '', False

        account_section = self.config['账号信息']
        userid = account_section.get('userid', '')
        encrypted_password = account_section.get('password', '')
        password = self._simple_decrypt(encrypted_password)
        save_password = account_section.getboolean('save_password', False)

        return userid, password, save_password
    
    def save_account_info(self, userid: str, password: str, save_password: bool):
        """保存账号信息

        Args:
            userid: 用户ID
            password: 密码
            save_password: 是否保存密码
        """
        if '账号信息' not in self.config:
            self.config.add_section('账号信息')

        self.config['账号信息']['userid'] = userid

        # 只有在选择保存密码时才加密保存密码
        if save_password:
            self.config['账号信息']['password'] = self._simple_encrypt(password)
        else:
            self.config['账号信息']['password'] = ''

        self.config['账号信息']['save_password'] = str(save_password)

        self.save_config()
    
    def get_setting(self, section: str, key: str, default=None):
        """获取配置项"""
        if section in self.config and key in self.config[section]:
            return self.config[section][key]
        return default
    
    def set_setting(self, section: str, key: str, value):
        """设置配置项"""
        if section not in self.config:
            self.config.add_section(section)
        self.config[section][key] = str(value)
        self.save_config()
    
    def get_daily_settings(self):
        """获取日常设置"""
        if '日常设置' not in self.config:
            return {}
        return dict(self.config['日常设置'])


# 全局配置管理器实例
config_manager = ConfigManager()
