"""
FloatMask应用主入口
负责初始化Kivy应用并启动主界面
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.utils import platform
import atexit

_FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'fonts')
FONT_PATH = os.path.join(_FONT_DIR, 'msyh.ttc')
if os.path.exists(FONT_PATH):
    LabelBase.register(name='Chinese', fn_regular=FONT_PATH)
    CN_FONT = 'Chinese'
else:
    CN_FONT = 'Roboto'

from app.core.overlay_manager import OverlayManager
from app.core.permission_handler import PermissionHandler
from app.services.overlay_service import OverlayService
from app.services.keep_alive_service import KeepAliveService
from app.utils.logger import logger
from app.utils.compat import compat
from app.utils.config import ConfigManager

if platform != 'android':
    Window.size = (400, 600)


class FloatMaskMain(BoxLayout):
    """主界面布局"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 10
        self._exiting = False

        self.config = ConfigManager()
        self.overlay_manager = OverlayManager()
        self.permission_handler = PermissionHandler()
        self.overlay_service = OverlayService()
        self.keep_alive_service = KeepAliveService()

        logger.info('Main', 'FloatMask应用启动')

        self.title_label = Label(
            text='FloatMask\n智能字幕遮挡工具',
            font_name=CN_FONT,
            font_size=24,
            size_hint_y=0.2,
            bold=True
        )
        self.add_widget(self.title_label)

        self.status_label = Label(
            text='悬浮框状态: 未启动',
            font_name=CN_FONT,
            font_size=16,
            size_hint_y=0.1
        )
        self.add_widget(self.status_label)

        self.permission_label = Label(
            text='',
            font_name=CN_FONT,
            font_size=14,
            size_hint_y=0.08
        )
        self.add_widget(self.permission_label)

        self.device_label = Label(
            text='',
            font_name=CN_FONT,
            font_size=12,
            size_hint_y=0.08
        )
        self.add_widget(self.device_label)

        self.toggle_btn = ToggleButton(
            text='启动悬浮框',
            font_name=CN_FONT,
            font_size=18,
            size_hint_y=0.15,
            on_press=self.toggle_overlay
        )
        self.add_widget(self.toggle_btn)

        self.permission_btn = Button(
            text='检测悬浮窗权限',
            font_name=CN_FONT,
            font_size=18,
            size_hint_y=0.12,
            on_press=self.check_permission
        )
        self.add_widget(self.permission_btn)

        self.click_through_btn = ToggleButton(
            text='穿透模式: 关闭',
            font_name=CN_FONT,
            font_size=18,
            size_hint_y=0.12,
            on_press=self.toggle_click_through
        )
        self.add_widget(self.click_through_btn)

        self.exit_btn = Button(
            text='退出应用',
            font_name=CN_FONT,
            font_size=18,
            size_hint_y=0.12,
            on_press=self.exit_app
        )
        self.add_widget(self.exit_btn)

        atexit.register(self._cleanup)
        Window.bind(on_close=self._on_window_close)

        self._show_device_info()
        self.check_permission(None)

        click_through_enabled = self.config.get_click_through()
        if click_through_enabled:
            self.click_through_btn.state = 'down'
            self.click_through_btn.text = '穿透模式: 开启'

    def _show_device_info(self):
        if platform == 'android':
            info = compat.get_device_info()
            self.device_label.text = (
                f'设备: {info["manufacturer"]} {info["model"]} '
                f'(API {info["sdk_version"]})'
            )
        else:
            self.device_label.text = '平台: PC (开发模式)'

    def toggle_overlay(self, instance):
        if instance.state == 'down':
            self.start_overlay()
        else:
            self.stop_overlay()

    def start_overlay(self):
        try:
            self.overlay_manager.create()

            overlay = self.overlay_manager.get_overlay()
            self.overlay_manager.show()

            if self.overlay_manager.use_native:
                self.keep_alive_service.start()
                mode_text = '原生'
            else:
                self.overlay_service.start(overlay)
                self.keep_alive_service.start()
                mode_text = 'Kivy'

            self.status_label.text = f'悬浮框状态: 运行中 ({mode_text}模式)'
            self.toggle_btn.text = '停止悬浮框'
            logger.info('Main', f'悬浮框已启动 ({mode_text}模式)')

        except Exception as e:
            self.status_label.text = f'启动失败: {str(e)}'
            self.toggle_btn.state = 'normal'
            logger.error('Main', f'启动失败: {e}')

    def stop_overlay(self):
        if not self.overlay_manager.is_running:
            return

        self.overlay_manager.save_current_config()
        was_native = self.overlay_manager.use_native
        self.overlay_manager.destroy()

        if was_native:
            self.keep_alive_service.stop()
        else:
            self.overlay_service.stop()
            self.keep_alive_service.stop()

        self.status_label.text = '悬浮框状态: 已停止'
        self.toggle_btn.text = '启动悬浮框'
        logger.info('Main', '悬浮框已停止')

    def check_permission(self, instance):
        try:
            if self.permission_handler.check_permission():
                self.permission_label.text = '权限状态: 已授权'
                self.permission_label.color = (0, 1, 0, 1)
            else:
                self.permission_label.text = '权限状态: 未授权（点击下方按钮开启）'
                self.permission_label.color = (1, 0, 0, 1)

        except Exception as e:
            self.permission_label.text = f'权限检测失败: {str(e)}'
            self.permission_label.color = (1, 0, 0, 1)
            logger.error('Main', f'权限检测失败: {e}')

    def toggle_click_through(self, instance):
        enabled = instance.state == 'down'
        self.config.set_click_through(enabled)

        if enabled:
            self.click_through_btn.text = '穿透模式: 开启'
        else:
            self.click_through_btn.text = '穿透模式: 关闭'

        if self.overlay_manager.is_running:
            try:
                self.overlay_manager.toggle_click_through(enabled)
                logger.info('Main', f'点击穿透模式已{"开启" if enabled else "关闭"}')
            except Exception as e:
                logger.error('Main', f'切换点击穿透模式失败: {e}')

        logger.info('Main', f'点击穿透模式设置为: {enabled}')

    def exit_app(self, instance):
        self._do_cleanup()
        App.get_running_app().stop()

    def _on_window_close(self):
        self._do_cleanup()
        return False

    def _do_cleanup(self):
        if self._exiting:
            return
        self._exiting = True
        self.stop_overlay()
        logger.info('Main', '应用已退出')

    def _cleanup(self):
        self._do_cleanup()


class FloatMaskApp(App):
    """FloatMask应用类"""

    def build(self):
        self.title = 'FloatMask'
        return FloatMaskMain()

    def on_pause(self):
        return True

    def on_resume(self):
        pass

    def on_stop(self):
        pass


if __name__ == '__main__':
    FloatMaskApp().run()
