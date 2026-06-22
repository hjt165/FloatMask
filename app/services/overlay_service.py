"""
悬浮窗后台服务模块
负责在后台保持悬浮框运行
前台服务保活由KeepAliveService统一管理
"""

from kivy.utils import platform
from app.utils.logger import logger


class OverlayService:
    """
    悬浮窗后台服务
    管理悬浮框生命周期引用
    前台服务保活由main.py通过KeepAliveService统一管理
    """

    def __init__(self):
        self.is_running = False
        self.overlay_widget = None

    def start(self, overlay_widget):
        if self.is_running:
            logger.warning('OverlayService', '服务已在运行，跳过重复启动')
            return

        self.overlay_widget = overlay_widget
        self.is_running = True
        logger.info('OverlayService', '悬浮窗服务已启动')

    def stop(self):
        if not self.is_running:
            return

        self.is_running = False
        self.overlay_widget = None
        logger.info('OverlayService', '悬浮窗服务已停止')

    def is_service_running(self):
        return self.is_running
