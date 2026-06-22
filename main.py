"""
FloatMask - 智能字幕遮挡工具
应用主入口
职责：初始化Kivy应用，管理页面切换，协调各模块工作
"""

import logging
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import platform
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 导入常量
from utils.constants import (
    APP_NAME, APP_VERSION,
    PAGE_SPLASH, PAGE_MAIN, PAGE_PERMISSION, PAGE_SETTINGS,
    OVERLAY_DEFAULT_WIDTH, OVERLAY_DEFAULT_HEIGHT,
    THEME_PRIMARY_COLOR, THEME_BACKGROUND_COLOR
)

# 导入核心模块
from core.overlay_manager import OverlayManager
from core.touch_handler import TouchHandler

# 导入工具模块
from utils.permissions import (
    check_overlay_permission,
    request_overlay_permission,
    open_overlay_settings
)

# 获取UI目录路径
UI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui')


def load_kv_files():
    """加载所有KV样式文件"""
    kv_files = [
        'splash.kv',
        'main.kv',
        'permission.kv',
        'settings.kv',
        'overlay.kv'
    ]

    for kv_file in kv_files:
        kv_path = os.path.join(UI_DIR, kv_file)
        if os.path.exists(kv_path):
            Builder.load_file(kv_path)
            logger.info(f"已加载KV文件: {kv_file}")
        else:
            logger.warning(f"KV文件不存在: {kv_path}")


class SplashScreen(Screen):
    """启动页"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self):
        """进入页面时执行"""
        logger.info("进入启动页")
        # 延迟跳转到下一个页面
        Clock.schedule_once(self.transition_next, 2.0)

    def transition_next(self, dt):
        """跳转到下一个页面"""
        if check_overlay_permission():
            self.manager.current = PAGE_MAIN
        else:
            self.manager.current = PAGE_PERMISSION


class MainScreen(Screen):
    """主页"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.overlay_manager = None
        self.touch_handler = None

    def on_enter(self):
        """进入页面时刷新状态"""
        self.update_status()

    def update_status(self):
        """更新悬浮窗状态显示"""
        if self.overlay_manager and self.overlay_manager.is_active():
            self.ids.status_icon.text = '◉'
            self.ids.status_icon.color = (0.3, 0.8, 0.3, 1)  # 绿色
            self.ids.status_text.text = '悬浮窗已激活'
            self.ids.toggle_button.text = '停止悬浮窗'
        else:
            self.ids.status_icon.text = '◎'
            self.ids.status_icon.color = (0.7, 0.7, 0.7, 1)  # 灰色
            self.ids.status_text.text = '悬浮窗未激活'
            self.ids.toggle_button.text = '启动悬浮窗'

    def toggle_overlay(self):
        """切换悬浮窗状态"""
        if self.overlay_manager is None:
            # 初始化悬浮窗管理器
            self.overlay_manager = OverlayManager()
            self.overlay_manager.initialize(Window.width, Window.height)
            self.touch_handler = TouchHandler(self.overlay_manager)

        if self.overlay_manager.is_active():
            self.overlay_manager.stop()
            logger.info("悬浮窗已停止")
        else:
            if check_overlay_permission():
                self.overlay_manager.start()
                logger.info("悬浮窗已启动")
            else:
                self.manager.current = PAGE_PERMISSION
                return

        self.update_status()

    def check_permission(self):
        """检测权限"""
        if check_overlay_permission():
            self.ids.status_text.text = '权限已授予'
        else:
            self.ids.status_text.text = '权限未授予'
            request_overlay_permission()

    def open_settings_page(self):
        """打开设置页"""
        self.manager.current = PAGE_SETTINGS


class PermissionScreen(Screen):
    """权限引导页"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def open_settings(self):
        """打开系统设置"""
        open_overlay_settings()

    def go_back(self):
        """返回主页"""
        self.manager.current = PAGE_MAIN

    def on_enter(self):
        """进入页面时检测权限状态"""
        if check_overlay_permission():
            self.manager.current = PAGE_MAIN


class SettingsScreen(Screen):
    """设置页"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def go_back(self):
        """返回主页"""
        self.manager.current = PAGE_MAIN


class FloatMaskApp(App):
    """FloatMask应用主类"""

    def build(self):
        """构建应用"""
        logger.info(f"启动 {APP_NAME} v{APP_VERSION}")

        # 加载KV样式文件
        load_kv_files()

        # 创建屏幕管理器
        self.screen_manager = ScreenManager()

        # 添加页面
        self.screen_manager.add_widget(SplashScreen(name=PAGE_SPLASH))
        self.screen_manager.add_widget(MainScreen(name=PAGE_MAIN))
        self.screen_manager.add_widget(PermissionScreen(name=PAGE_PERMISSION))
        self.screen_manager.add_widget(SettingsScreen(name=PAGE_SETTINGS))

        # 设置初始页面
        self.screen_manager.current = PAGE_SPLASH

        return self.screen_manager

    def on_pause(self):
        """应用暂停时（切换到后台）"""
        logger.info("应用暂停")
        return True

    def on_resume(self):
        """应用恢复时（从后台返回）"""
        logger.info("应用恢复")
        # 重新检测权限状态
        if check_overlay_permission():
            logger.info("权限已授予")


if __name__ == '__main__':
    FloatMaskApp().run()