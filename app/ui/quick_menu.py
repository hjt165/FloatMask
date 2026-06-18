"""
快捷菜单模块
长按悬浮框时弹出的快捷操作菜单
使用Canvas绘制，包含清晰的文字标签和精确的触摸区域
"""

from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line
from kivy.core.window import Window
from kivy.core.text import Label as CoreLabel


class QuickMenu(Widget):
    """
    快捷菜单组件
    提供悬浮框的快捷操作
    """

    def __init__(self, overlay_widget=None, **kwargs):
        super().__init__(**kwargs)

        self.overlay_widget = overlay_widget
        self.menu_width = 200
        self.menu_height = 180
        self.is_visible = False

        self.menu_x = 0
        self.menu_y = 0

        self.color_options = [
            ((0.5, 0.5, 0.5, 0.5), "半透明灰色"),
            ((0.0, 0.0, 0.0, 0.5), "半透明黑色"),
            ((0.0, 0.0, 0.0, 1.0), "纯黑色")
        ]
        self.current_color_index = 0

        self.item_height = 40
        self.padding = 10

        self._touch_areas = []

    def show(self, x, y):
        if self.is_visible:
            return

        self.menu_x = max(0, min(x - self.menu_width // 2, Window.width - self.menu_width))
        self.menu_y = max(0, min(y - self.menu_height // 2, Window.height - self.menu_height))

        self.is_visible = True
        self._calculate_touch_areas()
        self._draw_menu()
        Window.bind(on_touch_down=self._on_touch_down)

    def hide(self):
        if not self.is_visible:
            return

        self.is_visible = False
        self.canvas.clear()
        self._touch_areas = []
        Window.unbind(on_touch_down=self._on_touch_down)

    def _calculate_touch_areas(self):
        self._touch_areas = []
        ih = self.item_height
        p = self.padding
        btn_w = self.menu_width - 2 * p

        y1 = self.menu_y + self.menu_height - p - ih
        self._touch_areas.append({
            'rect': (self.menu_x + p, y1, btn_w, ih),
            'action': 'color'
        })

        y2 = y1 - ih - p
        self._touch_areas.append({
            'rect': (self.menu_x + p, y2, btn_w, ih),
            'action': 'opacity'
        })

        y3 = y2 - ih - p
        self._touch_areas.append({
            'rect': (self.menu_x + p, y3, btn_w, ih),
            'action': 'close'
        })

    def _draw_menu(self):
        self.canvas.clear()

        with self.canvas:
            Color(0.15, 0.15, 0.15, 0.95)
            Rectangle(
                pos=(self.menu_x, self.menu_y),
                size=(self.menu_width, self.menu_height)
            )

            Color(0.8, 0.8, 0.8, 0.6)
            Line(
                rectangle=(self.menu_x, self.menu_y, self.menu_width, self.menu_height),
                width=1
            )

            for area in self._touch_areas:
                x, y, w, h = area['rect']
                action = area['action']

                if action == 'color':
                    Color(0.25, 0.25, 0.25, 1)
                    text = "切换颜色"
                elif action == 'opacity':
                    Color(0.25, 0.25, 0.25, 1)
                    text = "调节透明度"
                else:
                    Color(0.4, 0.15, 0.15, 1)
                    text = "关闭悬浮框"

                Rectangle(pos=(x, y), size=(w, h))
                Color(0.5, 0.5, 0.5, 0.5)
                Line(rectangle=(x, y, w, h), width=1)

                label = CoreLabel(text=text, font_name='Chinese', font_size=14)
                label.refresh()
                tw, th = label.size
                tx = x + (w - tw) / 2
                ty = y + (h - th) / 2

                Color(1, 1, 1, 0.95)
                Rectangle(
                    pos=(tx, ty),
                    size=(tw, th),
                    texture=label.texture
                )

    def _on_touch_down(self, touch):
        if not self.is_visible:
            return False

        tx, ty = touch.x, touch.y

        for area in self._touch_areas:
            ax, ay, aw, ah = area['rect']
            if ax <= tx <= ax + aw and ay <= ty <= ay + ah:
                action = area['action']
                self.hide()

                if action == 'color':
                    self._on_color_change()
                elif action == 'opacity':
                    self._on_opacity_change()
                elif action == 'close':
                    self._on_close()

                return True

        self.hide()
        return False

    def _on_color_change(self):
        if self.overlay_widget:
            self.current_color_index = (self.current_color_index + 1) % len(self.color_options)
            color, _ = self.color_options[self.current_color_index]
            self.overlay_widget.set_color(*color)

    def _on_opacity_change(self):
        if self.overlay_widget:
            r, g, b, a = self.overlay_widget.overlay_color
            if a >= 0.8:
                a = 0.2
            else:
                a = min(1.0, a + 0.2)
            self.overlay_widget.set_color(r, g, b, a)

    def _on_close(self):
        if self.overlay_widget:
            from kivy.app import App
            app = App.get_running_app()
            if app and hasattr(app, 'root') and app.root:
                app.root.stop_overlay()
