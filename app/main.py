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
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.utils import platform
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp
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
    Window.size = (400, 720)

BG_COLOR = (0.102, 0.102, 0.180, 1)
CARD_COLOR = (0.086, 0.129, 0.243, 1)
STATUS_CARD_COLOR = (0.059, 0.204, 0.376, 1)
TEXT_PRIMARY = (1, 1, 1, 1)
TEXT_SECONDARY = (0.7, 0.7, 0.75, 1)
GREEN = (0, 0.784, 0.325, 1)
RED = (0.898, 0.224, 0.208, 1)
BLUE = (0.129, 0.588, 0.953, 1)
ORANGE = (1, 0.596, 0, 1)
GRAY = (0.259, 0.259, 0.259, 1)
DARK_GRAY = (0.18, 0.18, 0.18, 1)


class CardBackground(Widget):
    def __init__(self, color=CARD_COLOR, radius=12, **kwargs):
        super().__init__(**kwargs)
        self.card_color = color
        self.radius = radius
        self.bind(pos=self._update, size=self._update)
        self._update()

    def _update(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.card_color)
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(self.radius)]
            )


class RoundedButton(Button):
    def __init__(self, bg_color=GRAY, radius=10, **kwargs):
        super().__init__(**kwargs)
        self.bg_color_normal = bg_color
        self.bg_color_down = [c * 0.7 for c in bg_color[:3]] + [1]
        self._radius = radius
        self.background_normal = ''
        self.background_down = ''
        self.background_color = self.bg_color_normal
        self.bold = True
        self.bind(pos=self._update_canvas, size=self._update_canvas, state=self._on_state)
        self._update_canvas()

    def _on_state(self, *args):
        if self.state == 'down':
            self.background_color = self.bg_color_down
        else:
            self.background_color = self.bg_color_normal
        self._update_canvas()

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.background_color)
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(self._radius)]
            )


class RoundedToggleButton(ToggleButton):
    def __init__(self, bg_color_normal=GRAY, bg_color_active=GREEN, radius=10, **kwargs):
        super().__init__(**kwargs)
        self._bg_normal = bg_color_normal
        self._bg_active = bg_color_active
        self._radius = radius
        self.background_normal = ''
        self.background_down = ''
        self.bold = True
        self.bind(pos=self._update_canvas, size=self._update_canvas, state=self._on_state)
        self._on_state()
        self._update_canvas()

    def _on_state(self, *args):
        if self.state == 'down':
            self.background_color = self._bg_active
        else:
            self.background_color = self._bg_normal
        self._update_canvas()

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.background_color)
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(self._radius)]
            )


class StatusCard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = [dp(20), dp(16), dp(20), dp(16)]
        self.spacing = dp(8)
        self.bind(pos=self._update, size=self._update)

    def _update(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*STATUS_CARD_COLOR)
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(14)]
            )


class FloatMaskMain(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = [dp(24), dp(20), dp(24), dp(20)]
        self.spacing = dp(14)
        self._exiting = False

        with self.canvas.before:
            Color(*BG_COLOR)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        self.config = ConfigManager()
        self.overlay_manager = OverlayManager()
        self.permission_handler = PermissionHandler()
        self.overlay_service = OverlayService()
        self.keep_alive_service = KeepAliveService()

        logger.info('Main', 'FloatMask应用启动')

        title_area = BoxLayout(orientation='vertical', size_hint_y=0.22, padding=[0, dp(16), 0, dp(8)])
        with title_area.canvas.before:
            Color(*CARD_COLOR)
            title_area._card = RoundedRectangle(pos=title_area.pos, size=title_area.size, radius=[dp(16)])
        title_area.bind(pos=self._update_card, size=self._update_card)

        self.title_label = Label(
            text='FloatMask',
            font_name=CN_FONT,
            font_size=dp(36),
            bold=True,
            color=TEXT_PRIMARY,
            size_hint_y=0.6
        )
        title_area.add_widget(self.title_label)

        self.subtitle_label = Label(
            text='智能字幕遮挡工具',
            font_name=CN_FONT,
            font_size=dp(18),
            color=TEXT_SECONDARY,
            size_hint_y=0.4
        )
        title_area.add_widget(self.subtitle_label)
        self.add_widget(title_area)

        status_card = StatusCard(size_hint_y=0.18)
        self.status_label = Label(
            text='悬浮框状态: 未启动',
            font_name=CN_FONT,
            font_size=dp(22),
            bold=True,
            color=TEXT_PRIMARY,
            size_hint_y=0.45
        )
        status_card.add_widget(self.status_label)

        self.permission_label = Label(
            text='',
            font_name=CN_FONT,
            font_size=dp(17),
            size_hint_y=0.3
        )
        status_card.add_widget(self.permission_label)

        self.device_label = Label(
            text='',
            font_name=CN_FONT,
            font_size=dp(14),
            color=TEXT_SECONDARY,
            size_hint_y=0.25
        )
        status_card.add_widget(self.device_label)
        self.add_widget(status_card)

        btn_area = BoxLayout(orientation='vertical', size_hint_y=0.48, spacing=dp(10))

        self.toggle_btn = RoundedToggleButton(
            text='启动悬浮框',
            font_name=CN_FONT,
            font_size=dp(26),
            bg_color_normal=GRAY,
            bg_color_active=(0, 0.6, 0.25, 1),
            size_hint_y=0.25,
            on_press=self.toggle_overlay
        )
        btn_area.add_widget(self.toggle_btn)

        self.permission_btn = RoundedButton(
            text='检测悬浮窗权限',
            font_name=CN_FONT,
            font_size=dp(22),
            bg_color=BLUE,
            size_hint_y=0.22,
            on_press=self.check_permission
        )
        btn_area.add_widget(self.permission_btn)

        self.click_through_btn = RoundedToggleButton(
            text='穿透模式: 关闭',
            font_name=CN_FONT,
            font_size=dp(22),
            bg_color_normal=GRAY,
            bg_color_active=ORANGE,
            size_hint_y=0.22,
            on_press=self.toggle_click_through
        )
        btn_area.add_widget(self.click_through_btn)

        self.exit_btn = RoundedButton(
            text='退出应用',
            font_name=CN_FONT,
            font_size=dp(22),
            bg_color=RED,
            size_hint_y=0.22,
            on_press=self.exit_app
        )
        btn_area.add_widget(self.exit_btn)
        self.add_widget(btn_area)

        atexit.register(self._cleanup)
        Window.bind(on_close=self._on_window_close)

        self._show_device_info()
        self.check_permission(None)

        click_through_enabled = self.config.get_click_through()
        if click_through_enabled:
            self.click_through_btn.state = 'down'
            self.click_through_btn.text = '穿透模式: 开启'

    def _update_bg(self, *args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def _update_card(self, instance, *args):
        instance._card.pos = instance.pos
        instance._card.size = instance.size

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
            self.status_label.color = GREEN
            self.toggle_btn.text = '停止悬浮框'
            self.toggle_btn._bg_active = (0, 0.6, 0.25, 1)
            self.toggle_btn._update_canvas()
            logger.info('Main', f'悬浮框已启动 ({mode_text}模式)')

        except Exception as e:
            self.status_label.text = f'启动失败: {str(e)}'
            self.status_label.color = RED
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
        self.status_label.color = TEXT_PRIMARY
        self.toggle_btn.text = '启动悬浮框'
        logger.info('Main', '悬浮框已停止')

    def check_permission(self, instance):
        try:
            if self.permission_handler.check_permission():
                self.permission_label.text = '权限状态: 已授权'
                self.permission_label.color = GREEN
            else:
                self.permission_label.text = '权限状态: 未授权（点击下方按钮开启）'
                self.permission_label.color = RED

        except Exception as e:
            self.permission_label.text = f'权限检测失败: {str(e)}'
            self.permission_label.color = RED
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
