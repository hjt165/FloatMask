"""
存储管理模块
封装SharedPreferences（Android）和JSON文件（PC）的读写操作
"""

import json
import os
from kivy.utils import platform


class StorageManager:
    """
    存储管理器
    提供统一的键值对存储接口
    """

    def __init__(self, namespace='floatmask'):
        self.namespace = namespace
        self._cache = {}
        self._file_path = self._get_file_path()

    def _get_file_path(self):
        if platform == 'android':
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.renpy.android.PythonActivity')
                activity = PythonActivity.mActivity
                return os.path.join(
                    activity.getFilesDir().getAbsolutePath(),
                    f'{self.namespace}_storage.json'
                )
            except Exception:
                pass

        return os.path.join(os.path.expanduser('~'), f'.{self.namespace}_storage.json')

    def get(self, key, default=None):
        if key in self._cache:
            return self._cache[key]

        data = self._load_all()
        value = data.get(key, default)
        self._cache[key] = value
        return value

    def set(self, key, value):
        self._cache[key] = value
        data = self._load_all()
        data[key] = value
        self._save_all(data)

    def delete(self, key):
        if key in self._cache:
            del self._cache[key]
        data = self._load_all()
        if key in data:
            del data[key]
            self._save_all(data)

    def has(self, key):
        if key in self._cache:
            return True
        data = self._load_all()
        return key in data

    def clear(self):
        self._cache.clear()
        self._save_all({})

    def get_all(self):
        data = self._load_all()
        data.update(self._cache)
        return data

    def _load_all(self):
        if platform == 'android':
            return self._load_from_shared_preferences()
        else:
            return self._load_from_file()

    def _save_all(self, data):
        if platform == 'android':
            self._save_to_shared_preferences(data)
        else:
            self._save_to_file(data)

    def _load_from_shared_preferences(self):
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.renpy.android.PythonActivity')
            activity = PythonActivity.mActivity

            prefs = activity.getPreferences(0)
            json_str = prefs.getString(f'{self.namespace}_data', None)

            if json_str:
                return json.loads(json_str)
            return {}
        except Exception:
            return {}

    def _save_to_shared_preferences(self, data):
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.renpy.android.PythonActivity')
            activity = PythonActivity.mActivity

            prefs = activity.getPreferences(0)
            editor = prefs.edit()
            editor.putString(f'{self.namespace}_data', json.dumps(data))
            editor.apply()
        except Exception:
            pass

    def _load_from_file(self):
        if os.path.exists(self._file_path):
            try:
                with open(self._file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_to_file(self, data):
        try:
            os.makedirs(os.path.dirname(self._file_path), exist_ok=True)
            with open(self._file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass


class OverlayStorage:
    """
    悬浮框专用存储
    封装悬浮框的位置、大小、颜色等配置的读写
    """

    def __init__(self):
        self._storage = StorageManager(namespace='overlay')

    def get_position(self):
        x = self._storage.get('x')
        y = self._storage.get('y')
        if x is not None and y is not None:
            return (x, y)
        return None

    def set_position(self, x, y):
        self._storage.set('x', x)
        self._storage.set('y', y)

    def get_size(self):
        w = self._storage.get('width')
        h = self._storage.get('height')
        if w is not None and h is not None:
            return (w, h)
        return None

    def set_size(self, width, height):
        self._storage.set('width', width)
        self._storage.set('height', height)

    def get_color(self):
        return self._storage.get('color', [0.5, 0.5, 0.5, 0.5])

    def set_color(self, r, g, b, a):
        self._storage.set('color', [r, g, b, a])

    def get_all_config(self):
        return {
            'position': self.get_position(),
            'size': self.get_size(),
            'color': self.get_color(),
        }

    def save_all_config(self, position=None, size=None, color=None):
        if position:
            self.set_position(*position)
        if size:
            self.set_size(*size)
        if color:
            self.set_color(*color)

    def clear(self):
        self._storage.clear()
