"""
悬浮框管理器模块
管理悬浮框的创建、显示、隐藏和销毁，统一管理生命周期
支持Kivy覆盖层（PC开发）和Android原生覆盖层（跨App覆盖）
"""

from kivy.utils import platform
from app.utils.logger import logger
from app.utils.storage import OverlayStorage
from app.utils.config import ConfigManager


class OverlayManager:
    """
    悬浮框管理器
    提供统一的悬浮框生命周期管理接口
    支持Kivy和原生两种覆盖层模式
    """

    def __init__(self):
        self.overlay = None
        self.native_overlay = None
        self.storage = OverlayStorage()
        self.config = ConfigManager()
        self._is_running = False
        self._use_native = False

    @property
    def is_running(self):
        return self._is_running

    @property
    def use_native(self):
        return self._use_native

    def _should_use_native(self):
        """判断是否应使用原生覆盖层"""
        if platform != 'android':
            return False

        mode = self.config.get_overlay_mode()
        if mode == 'native':
            return True
        elif mode == 'kivy':
            return False
        else:
            return True

    def create(self, **kwargs):
        self._use_native = self._should_use_native()

        if self._use_native:
            return self._create_native(**kwargs)
        else:
            return self._create_kivy(**kwargs)

    def _create_kivy(self, **kwargs):
        from app.ui.overlay_widget import OverlayWidget

        saved_config = self._load_saved_config()
        config = {**saved_config, **kwargs}

        self.overlay = OverlayWidget(
            width=config.get('width', 200),
            height=config.get('height', 120),
            color=tuple(config.get('color', [0.5, 0.5, 0.5, 0.5]))
        )

        if config.get('x') is not None and config.get('y') is not None:
            self.overlay.x = config['x']
            self.overlay.y = config['y']

        logger.info('OverlayManager', f'Kivy悬浮框已创建: {config.get("width")}x{config.get("height")}')
        return self.overlay

    def _create_native(self, **kwargs):
        from app.services.android_window import NativeOverlay

        saved_config = self._load_saved_config()
        config = {**saved_config, **kwargs}

        self.native_overlay = NativeOverlay()

        logger.info('OverlayManager', f'原生悬浮框已创建: {config.get("width")}x{config.get("height")}')
        return self.native_overlay

    def show(self):
        if self._use_native:
            return self._show_native()
        else:
            return self._show_kivy()

    def _show_kivy(self):
        if self.overlay is None:
            self.create()

        self.overlay.open()
        self._is_running = True
        logger.info('OverlayManager', 'Kivy悬浮框已显示')

    def _show_native(self):
        if self.native_overlay is None:
            self.create()

        if not self.native_overlay.manager.check_permission():
            from app.core.permission_handler import PermissionHandler
            PermissionHandler().request_permission()
            raise PermissionError('悬浮窗权限未授权')

        saved_config = self._load_saved_config()
        x = saved_config.get('x', 100)
        y = saved_config.get('y', 100)
        width = saved_config.get('width', 200)
        height = saved_config.get('height', 120)
        color = saved_config.get('color', [0.5, 0.5, 0.5, 0.5])
        click_through = self.config.get_click_through()

        color_index = self._color_to_index(color)

        self.native_overlay.show(
            x=x, y=y,
            width=width, height=height,
            touch_through=click_through,
            color_index=color_index
        )
        self._is_running = True
        logger.info('OverlayManager', '原生悬浮框已显示')

    def hide(self):
        if self._use_native:
            return self._hide_native()
        else:
            return self._hide_kivy()

    def _hide_kivy(self):
        if self.overlay:
            self.save_current_config()
            self.overlay.close()
            self._is_running = False
            logger.info('OverlayManager', 'Kivy悬浮框已隐藏')

    def _hide_native(self):
        if self.native_overlay:
            self.native_overlay.hide()
            self._is_running = False
            logger.info('OverlayManager', '原生悬浮框已隐藏')

    def destroy(self):
        if self._use_native:
            return self._destroy_native()
        else:
            return self._destroy_kivy()

    def _destroy_kivy(self):
        if self.overlay:
            self.save_current_config()
            self.overlay.close()
            self.overlay = None
            self._is_running = False
            logger.info('OverlayManager', 'Kivy悬浮框已销毁')

    def _destroy_native(self):
        if self.native_overlay:
            self.native_overlay.hide()
            self.native_overlay = None
            self._is_running = False
            logger.info('OverlayManager', '原生悬浮框已销毁')

    def toggle(self):
        if self._is_running:
            self.hide()
        else:
            self.show()

    def get_overlay(self):
        if self._use_native:
            return self.native_overlay
        return self.overlay

    def _load_saved_config(self):
        config = {}

        pos = self.storage.get_position()
        if pos:
            config['x'] = pos[0]
            config['y'] = pos[1]

        size = self.storage.get_size()
        if size:
            config['width'] = size[0]
            config['height'] = size[1]

        color = self.storage.get_color()
        if color:
            config['color'] = color

        return config

    def save_current_config(self):
        if self._use_native:
            return self._save_native_config()
        else:
            return self._save_kivy_config()

    def _save_kivy_config(self):
        if self.overlay is None:
            return

        x, y = self.overlay.get_position()
        w, h = self.overlay.get_size()
        color = self.overlay.overlay_color

        self.storage.save_all_config(
            position=(x, y),
            size=(w, h),
            color=list(color)
        )
        logger.info('OverlayManager', f'配置已保存: pos=({x},{y}) size=({w},{h})')

    def _save_native_config(self):
        if self.native_overlay is None or not self.native_overlay.is_visible:
            return

        params = self.native_overlay.manager._params
        if params:
            self.storage.save_all_config(
                position=(params.x, params.y),
                size=(params.width, params.height),
                color=self._index_to_color(self.native_overlay.color_index)
            )

    def set_position(self, x, y):
        if self._use_native:
            if self.native_overlay:
                self.native_overlay.move(x, y)
        else:
            if self.overlay:
                self.overlay.x = x
                self.overlay.y = y
                self.overlay._draw_overlay()

    def set_size(self, width, height):
        if self._use_native:
            if self.native_overlay:
                self.native_overlay.resize(width, height)
        else:
            if self.overlay:
                self.overlay.resize(width, height)

    def set_color(self, r, g, b, a):
        if self._use_native:
            if self.native_overlay:
                color_index = self._color_to_index([r, g, b, a])
                self.native_overlay.set_color(color_index)
        else:
            if self.overlay:
                self.overlay.set_color(r, g, b, a)

    def minimize(self):
        if self._use_native:
            if self.native_overlay:
                self.native_overlay.minimize()
        else:
            if self.overlay:
                self.overlay.minimize()

    def restore(self):
        if self._use_native:
            if self.native_overlay:
                self.native_overlay.restore()
        else:
            if self.overlay:
                self.overlay.restore()

    def show_menu(self):
        """显示快捷菜单"""
        if self._use_native:
            if self.native_overlay:
                self.native_overlay.show_menu()
        else:
            if self.overlay:
                self.overlay._on_long_press(None)

    def toggle_click_through(self, enabled):
        """切换点击穿透模式"""
        self.config.set_click_through(enabled)
        if self._use_native and self.native_overlay:
            self.native_overlay.set_passthrough(enabled)

    def _color_to_index(self, color):
        """将RGB颜色转换为颜色索引"""
        if isinstance(color, (list, tuple)) and len(color) >= 3:
            r, g, b = color[0], color[1], color[2]
            if r < 0.2 and g < 0.2 and b < 0.2:
                return 0
            elif g > r and g > b:
                return 1
            elif b > r and b > g:
                return 2
            elif r > g and r > b:
                return 3
        return 0

    def _index_to_color(self, index):
        """将颜色索引转换为RGBA颜色列表"""
        from app.services.android_window import COLORS_ARGB
        r, g, b, a = COLORS_ARGB[index % len(COLORS_ARGB)]
        return [r / 255.0, g / 255.0, b / 255.0, a / 255.0]
