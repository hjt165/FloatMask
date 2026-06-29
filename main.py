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

# 注册中文字体
from kivy.core.text import LabelBase
FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'fonts')
CHINESE_FONT = os.path.join(FONT_DIR, 'msyh.ttc')
if os.path.exists(CHINESE_FONT):
    LabelBase.register(name='Chinese', fn_regular=CHINESE_FONT)
    logger.info(f"已注册中文字体: {CHINESE_FONT}")
else:
    logger.warning(f"中文字体不存在: {CHINESE_FONT}")

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
import utils.storage as storage
import utils.compat as compat

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
            self.ids.status_icon.text = 'ON'
            self.ids.status_icon.color = (0.3, 0.8, 0.3, 1)  # 绿色
            self.ids.status_text.text = '悬浮窗已激活'
            self.ids.toggle_button.text = '停止悬浮窗'
            self.ids.status_desc.text = '悬浮窗正在运行中'
        else:
            self.ids.status_icon.text = 'FM'
            self.ids.status_icon.color = (0.13, 0.59, 0.95, 1)  # 蓝色
            self.ids.status_text.text = '悬浮窗未激活'
            self.ids.toggle_button.text = '启动悬浮窗'
            self.ids.status_desc.text = '点击下方按钮启动悬浮窗'

    def toggle_overlay(self):
        """切换悬浮窗状态"""
        logger.info(f"toggle_overlay called, overlay_manager={self.overlay_manager}, active={self.overlay_manager.is_active() if self.overlay_manager else None}")
        if self.overlay_manager is None:
            # 初始化悬浮窗管理器
            self.overlay_manager = OverlayManager()
            self.overlay_manager.initialize(Window.width, Window.height)
            self.touch_handler = TouchHandler(self.overlay_manager)
            # 注册触摸处理器到悬浮窗管理器（TouchBridge回调用）
            self.overlay_manager.set_touch_handler(self.touch_handler)

        if self.overlay_manager.is_active():
            logger.info("Stopping overlay")
            self.overlay_manager.stop()
            self._stop_foreground_service()
            logger.info("悬浮窗已停止")
        else:
            if check_overlay_permission():
                # 启动前加载记忆状态
                self._load_memory_state()
                logger.info("Starting overlay")
                success = self.overlay_manager.start()
                if success:
                    self._start_foreground_service()
                    logger.info("悬浮窗已启动")
                else:
                    logger.error("悬浮窗启动失败")
            else:
                self.manager.current = PAGE_PERMISSION
                return

        self.update_status()

    def _load_memory_state(self):
        """从存储中加载上次的状态"""
        try:
            state = storage.load_all()
            if state['pos_x'] != 0 or state['pos_y'] != 0:
                self.overlay_manager._pos_x = state['pos_x']
                self.overlay_manager._pos_y = state['pos_y']
            if state['width'] != OVERLAY_DEFAULT_WIDTH:
                self.overlay_manager._width = state['width']
            if state['height'] != OVERLAY_DEFAULT_HEIGHT:
                self.overlay_manager._height = state['height']
            self.overlay_manager._color_index = state['color_index']
            self.overlay_manager._opacity = state['opacity']
            logger.info("已加载记忆状态")
        except Exception as e:
            logger.error(f"加载记忆状态失败: {e}")

    def _save_memory_state(self):
        """保存当前状态到存储"""
        if self.overlay_manager:
            try:
                pos = self.overlay_manager.get_position()
                size = self.overlay_manager.get_size()
                storage.save_all(
                    pos[0], pos[1],
                    size[0], size[1],
                    self.overlay_manager.get_color_index(),
                    self.overlay_manager._opacity
                )
                logger.info("已保存当前状态")
            except Exception as e:
                logger.error(f"保存状态失败: {e}")

    def _start_foreground_service(self):
        """启动前台服务保活"""
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            PythonService = autoclass('org.kivy.android.PythonService')
            context = PythonActivity.mActivity
            intent = Intent(context, PythonService)
            context.startService(intent)
            logger.info("前台服务已启动")
        except Exception as e:
            logger.error(f"启动前台服务失败: {e}")

    def _stop_foreground_service(self):
        """停止前台服务"""
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            PythonService = autoclass('org.kivy.android.PythonService')
            context = PythonActivity.mActivity
            intent = Intent(context, PythonService)
            context.stopService(intent)
            logger.info("前台服务已停止")
        except Exception as e:
            logger.error(f"停止前台服务失败: {e}")

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
        # 延迟检测权限，等待 Activity 完全恢复
        Clock.schedule_once(self._check_permission_delayed, 0.5)

    def _check_permission_delayed(self, dt):
        """延迟检测权限"""
        if check_overlay_permission():
            self.manager.current = PAGE_MAIN
        else:
            self._update_manufacturer_guide()

    def _update_manufacturer_guide(self):
        """根据厂商更新权限引导文案"""
        try:
            guide_text = compat.get_permission_guide_text()
            if hasattr(self.ids, 'guide_text'):
                self.ids.guide_text.text = guide_text
        except Exception as e:
            logger.error(f"获取厂商引导文案失败: {e}")


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

        # 注册广播接收器（用于ADB命令控制悬浮窗）
        self._receiver = None
        self._register_intent_poller()

        return self.screen_manager

    def _register_intent_poller(self):
        """注册Intent轮询器，用于接收ADB命令触发悬浮窗

        替代BroadcastReceiver（PyJNIus不支持继承抽象类）
        通过am start发送Intent，App定期检查Intent action
        支持的命令：
        - adb shell am start -a org.floatmask.START_OVERLAY -n org.floatmask.floatmask/org.kivy.android.PythonActivity
        - adb shell am start -a org.floatmask.STOP_OVERLAY -n org.floatmask.floatmask/org.kivy.android.PythonActivity
        - adb shell am start -a org.floatmask.TOGGLE_OVERLAY -n org.floatmask.floatmask/org.kivy.android.PythonActivity
        """
        try:
            from jnius import autoclass

            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            app = self

            def check_intent_action(dt):
                try:
                    activity = PythonActivity.mActivity
                    if activity is None:
                        return
                    intent = activity.getIntent()
                    if intent is None:
                        return
                    action = intent.getAction()
                    if action:
                        logger.info(f"检测到Intent action: {action}")
                        # 清除已处理的action，避免重复触发
                        intent.setAction(None)
                        Clock.schedule_once(lambda _: self._handle_intent_action(action), 0)
                except Exception as e:
                    logger.debug(f"Intent轮询检查失败: {e}")

            Clock.schedule_interval(check_intent_action, 1)
            logger.info("Intent轮询器已注册 (START/STOP/TOGGLE_OVERLAY)")
        except Exception as e:
            logger.error(f"注册Intent轮询器失败: {e}")

    def _handle_intent_action(self, action):
        """处理Intent action触发的操作"""
        try:
            main = self.screen_manager.get_screen(PAGE_MAIN)
            if action == 'org.floatmask.START_OVERLAY':
                if not main.overlay_manager or not main.overlay_manager.is_active():
                    main.toggle_overlay()
            elif action == 'org.floatmask.STOP_OVERLAY':
                if main.overlay_manager and main.overlay_manager.is_active():
                    main.toggle_overlay()
            elif action == 'org.floatmask.TOGGLE_OVERLAY':
                main.toggle_overlay()
        except Exception as e:
            logger.error(f"Intent action处理失败: {e}")

    def on_pause(self):
        """应用暂停时（切换到后台）"""
        logger.info("应用暂停")
        return True

    def on_resume(self):
        """应用恢复时（从后台返回，例如用户从设置页返回）"""
        logger.info("应用恢复，检测权限状态")
        if check_overlay_permission():
            logger.info("权限已授予，跳转到主页")
            self.screen_manager.current = PAGE_MAIN

    def on_stop(self):
        """应用退出时清理资源"""
        logger.info("应用退出，清理资源")

        # 获取主页并清理悬浮窗
        try:
            main_screen = self.screen_manager.get_screen(PAGE_MAIN)
            if main_screen.overlay_manager:
                # 保存状态
                main_screen._save_memory_state()
                # 停止悬浮窗
                main_screen.overlay_manager.stop()
                # 停止前台服务
                main_screen._stop_foreground_service()
                logger.info("悬浮窗已清理")
        except Exception as e:
            logger.error(f"清理资源失败: {e}")


if __name__ == '__main__':
    FloatMaskApp().run()
