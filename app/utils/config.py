"""
配置管理模块
负责读取和保存应用配置，支持Android SharedPreferences存储
"""

import json
import os
from kivy.utils import platform


class ConfigManager:
    """
    配置管理器
    管理应用的配置数据，包括悬浮框位置、大小、颜色等
    """

    def __init__(self):
        import copy
        self.default_config = {
            'overlay': {
                'width': 200,
                'height': 120,
                'x': None,
                'y': None,
                'color': [0.5, 0.5, 0.5, 0.5],
                'border_width': 2,
                'click_through': False,
                'overlay_mode': 'auto'  # 'kivy' | 'native' | 'auto'
            },
            'behavior': {
                'min_visible_percent': 0.2,
                'long_press_threshold': 0.5,
                'double_tap_threshold': 0.3
            },
            'memory': {
                'remember_position': True,
                'remember_size': True,
                'remember_color': False
            }
        }
        self.config = copy.deepcopy(self.default_config)
        self._load_config_into()

    def _load_config_into(self):
        loaded = self._load_config()
        self._deep_update(self.config, loaded)

    def _deep_update(self, base, update):
        for key, value in update.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value

    def _load_config(self):
        """
        加载配置

        Returns:
            dict: 配置数据
        """
        if platform == 'android':
            return self._load_from_shared_preferences()
        else:
            return self._load_from_file()

    def _load_from_shared_preferences(self):
        """
        从Android SharedPreferences加载配置

        Returns:
            dict: 配置数据
        """
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity

            # 获取SharedPreferences
            prefs = activity.getPreferences(0)  # MODE_PRIVATE = 0

            # 读取配置JSON
            config_json = prefs.getString('floatmask_config', None)

            if config_json:
                return json.loads(config_json)
            else:
                return self.default_config.copy()

        except Exception as e:
            print(f"从SharedPreferences加载配置失败: {e}")
            return self.default_config.copy()

    def _load_from_file(self):
        """
        从文件加载配置（非Android平台）

        Returns:
            dict: 配置数据
        """
        config_file = self._get_config_file_path()

        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"从文件加载配置失败: {e}")
                return self.default_config.copy()
        else:
            return self.default_config.copy()

    def save_config(self):
        """
        保存配置
        """
        if platform == 'android':
            self._save_to_shared_preferences()
        else:
            self._save_to_file()

    def _save_to_shared_preferences(self):
        """
        保存配置到Android SharedPreferences
        """
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity

            # 获取SharedPreferences
            prefs = activity.getPreferences(0)  # MODE_PRIVATE = 0

            # 将配置转换为JSON字符串
            config_json = json.dumps(self.config)

            # 保存配置
            editor = prefs.edit()
            editor.putString('floatmask_config', config_json)
            editor.apply()

            print("配置已保存到SharedPreferences")

        except Exception as e:
            print(f"保存配置到SharedPreferences失败: {e}")

    def _save_to_file(self):
        """
        保存配置到文件（非Android平台）
        """
        config_file = self._get_config_file_path()

        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(config_file), exist_ok=True)

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)

            print(f"配置已保存到文件: {config_file}")

        except Exception as e:
            print(f"保存配置到文件失败: {e}")

    def _get_config_file_path(self):
        """
        获取配置文件路径

        Returns:
            str: 配置文件路径
        """
        if platform == 'android':
            # Android内部存储
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            return os.path.join(activity.getFilesDir().getAbsolutePath(), 'floatmask_config.json')
        else:
            # PC上的用户目录
            return os.path.join(os.path.expanduser('~'), '.floatmask_config.json')

    def get(self, section, key, default=None):
        """
        获取配置值

        Args:
            section: 配置节
            key: 配置键
            default: 默认值

        Returns:
            配置值
        """
        if section in self.config and key in self.config[section]:
            return self.config[section][key]
        return default

    def set(self, section, key, value):
        """
        设置配置值

        Args:
            section: 配置节
            key: 配置键
            value: 配置值
        """
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save_config()

    def get_overlay_config(self):
        """
        获取悬浮框配置

        Returns:
            dict: 悬浮框配置
        """
        return self.config.get('overlay', self.default_config['overlay'])

    def set_overlay_position(self, x, y):
        """
        设置悬浮框位置

        Args:
            x: x坐标
            y: y坐标
        """
        self.set('overlay', 'x', x)
        self.set('overlay', 'y', y)

    def set_overlay_size(self, width, height):
        """
        设置悬浮框大小

        Args:
            width: 宽度
            height: 高度
        """
        self.set('overlay', 'width', width)
        self.set('overlay', 'height', height)

    def set_overlay_color(self, r, g, b, a):
        """
        设置悬浮框颜色

        Args:
            r: 红色分量 (0-1)
            g: 绿色分量 (0-1)
            b: 蓝色分量 (0-1)
            a: 透明度 (0-1)
        """
        self.set('overlay', 'color', [r, g, b, a])

    def get_click_through(self):
        """
        获取点击穿透模式状态

        Returns:
            bool: 是否启用点击穿透
        """
        return self.get('overlay', 'click_through', False)

    def set_click_through(self, enabled):
        """
        设置点击穿透模式

        Args:
            enabled: 是否启用点击穿透
        """
        self.set('overlay', 'click_through', enabled)

    def get_overlay_mode(self):
        """
        获取覆盖层模式

        Returns:
            str: 覆盖层模式 ('kivy' | 'native' | 'auto')
        """
        return self.get('overlay', 'overlay_mode', 'auto')

    def set_overlay_mode(self, mode):
        """
        设置覆盖层模式

        Args:
            mode: 覆盖层模式 ('kivy' | 'native' | 'auto')
        """
        if mode not in ['kivy', 'native', 'auto']:
            raise ValueError(f"无效的覆盖层模式: {mode}")
        self.set('overlay', 'overlay_mode', mode)

    def reset_to_default(self):
        import copy
        self.config = copy.deepcopy(self.default_config)
        self.save_config()
