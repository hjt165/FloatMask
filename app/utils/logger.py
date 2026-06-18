"""
日志工具模块
统一日志管理，支持控制台输出和文件记录
"""

import os
import time
from kivy.utils import platform


class Logger:
    """
    统一日志管理器
    支持多级别日志输出（DEBUG, INFO, WARNING, ERROR）
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.level = 'INFO'
        self.log_file = None
        self.buffer = []
        self.max_buffer_size = 1000

        self._levels = {
            'DEBUG': 0,
            'INFO': 1,
            'WARNING': 2,
            'ERROR': 3
        }

        if platform == 'android':
            self._init_android_log()

    def _init_android_log(self):
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.renpy.android.PythonActivity')
            activity = PythonActivity.mActivity
            log_dir = activity.getFilesDir().getAbsolutePath()
            self.log_file = os.path.join(log_dir, 'floatmask.log')
        except Exception:
            self.log_file = None

    def set_level(self, level):
        self.level = level.upper()

    def debug(self, tag, message):
        self._log('DEBUG', tag, message)

    def info(self, tag, message):
        self._log('INFO', tag, message)

    def warning(self, tag, message):
        self._log('WARNING', tag, message)

    def error(self, tag, message):
        self._log('ERROR', tag, message)

    def _log(self, level, tag, message):
        if self._levels.get(level, 0) < self._levels.get(self.level, 1):
            return

        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] [{level}] [{tag}] {message}"

        print(log_line)

        self.buffer.append(log_line)
        if len(self.buffer) > self.max_buffer_size:
            self.buffer = self.buffer[-self.max_buffer_size:]

        if self.log_file:
            self._write_to_file(log_line)

    def _write_to_file(self, log_line):
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_line + '\n')
        except Exception:
            pass

    def get_logs(self, count=100):
        return self.buffer[-count:]

    def clear_logs(self):
        self.buffer.clear()
        if self.log_file and os.path.exists(self.log_file):
            try:
                os.remove(self.log_file)
            except Exception:
                pass


logger = Logger()
