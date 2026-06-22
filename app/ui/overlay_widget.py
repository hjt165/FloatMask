"""
悬浮框组件模块
实现核心的悬浮遮挡框功能，包括显示、拖动、调整大小等
"""

import time
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.core.window import Window
from kivy.clock import Clock

from app.core.boundary_calculator import BoundaryCalculator
from app.core.gesture_handler import GestureHandler
from app.ui.quick_menu import QuickMenu


class OverlayWidget(Widget):
    """
    悬浮框组件
    一个半透明的矩形框，可拖动和调整大小，用于遮挡视频字幕
    """

    def __init__(self, **kwargs):
        self._init_color = kwargs.pop('color', (0.5, 0.5, 0.5, 0.5))
        self._init_border_width = kwargs.pop('border_width', 2)
        super().__init__(**kwargs)

        self.boundary = BoundaryCalculator()

        self.gesture_handler = GestureHandler(callback=self._on_gesture)

        self.overlay_width = kwargs.get('width', 200)
        self.overlay_height = kwargs.get('height', 120)
        self.overlay_color = self._init_color
        self.border_width = self._init_border_width

        self.overlay_width, self.overlay_height = self.boundary.constrain_size(
            self.overlay_width, self.overlay_height
        )

        if 'x' in kwargs and 'y' in kwargs:
            self.x = kwargs['x']
            self.y = kwargs['y']
        else:
            self.x, self.y = self.boundary.calculate_initial_position(
                self.overlay_width, self.overlay_height
            )

        self.isDragging = False
        self.drag_touch = None
        self.drag_offset = (0, 0)

        self.isResizing = False
        self.resize_touch = None
        self.resize_edge = None
        self.resize_start_pos = (0, 0)
        self.resize_start_size = (0, 0)

        self.long_press_timer = None
        self.long_press_threshold = 0.5

        self.color_modes = [
            (0.5, 0.5, 0.5, 0.5),
            (0.0, 0.0, 0.0, 0.5),
            (0.0, 0.0, 0.0, 1.0)
        ]
        self.current_color_index = 0

        self.handle_size = 20
        self.handle_color = (1, 1, 1, 0.8)

        self.is_minimized = False
        self.minimized_size = 30
        self.original_size = (self.overlay_width, self.overlay_height)
        self.original_pos = (self.x, self.y)

        self._draw_overlay()

    def _draw_overlay(self):
        """
        绘制悬浮框
        根据最小化状态绘制不同内容
        """
        self.canvas.clear()

        if self.is_minimized:
            self._draw_minimized()
        else:
            self._draw_normal()

    def _draw_minimized(self):
        """
        绘制最小化状态（小圆点）
        """
        with self.canvas:
            # 绘制小圆点
            Color(*self.overlay_color)
            Ellipse(
                pos=(self.x, self.y),
                size=(self.minimized_size, self.minimized_size)
            )

            # 绘制边框
            Color(1, 1, 1, 0.8)
            Line(
                circle=(self.x + self.minimized_size / 2,
                        self.y + self.minimized_size / 2,
                        self.minimized_size / 2),
                width=self.border_width
            )

    def _draw_normal(self):
        """
        绘制正常状态
        """
        with self.canvas:
            # 设置颜色（半透明灰色）
            Color(*self.overlay_color)

            # 绘制矩形
            self.rect = Rectangle(
                pos=(self.x, self.y),
                size=(self.overlay_width, self.overlay_height)
            )

            # 绘制边框
            Color(1, 1, 1, 0.8)  # 白色边框
            Line(
                rectangle=(self.x, self.y, self.overlay_width, self.overlay_height),
                width=self.border_width
            )

            # 绘制四个角的控制点（用于调整大小）
            self._draw_handles()

            # 绘制最小化按钮（右上角）
            self._draw_minimize_button()

    def _draw_handles(self):
        """
        绘制四个角的控制点
        """
        handle_size = self.handle_size
        half_handle = handle_size / 2

        # 左下角控制点
        Color(*self.handle_color)
        Ellipse(
            pos=(self.x - half_handle, self.y - half_handle),
            size=(handle_size, handle_size)
        )

        # 右下角控制点
        Ellipse(
            pos=(self.x + self.overlay_width - half_handle, self.y - half_handle),
            size=(handle_size, handle_size)
        )

        # 左上角控制点
        Ellipse(
            pos=(self.x - half_handle, self.y + self.overlay_height - half_handle),
            size=(handle_size, handle_size)
        )

        # 右上角控制点
        Ellipse(
            pos=(self.x + self.overlay_width - half_handle, self.y + self.overlay_height - half_handle),
            size=(handle_size, handle_size)
        )

    def _draw_minimize_button(self):
        """
        绘制最小化按钮（右上角的箭头）
        """
        btn_size = 20
        btn_x = self.x + self.overlay_width - btn_size - 5
        btn_y = self.y + self.overlay_height - btn_size - 5

        # 绘制按钮背景
        Color(0.5, 0.5, 0.5, 0.7)
        Rectangle(
            pos=(btn_x, btn_y),
            size=(btn_size, btn_size)
        )

        # 绘制向下箭头（表示最小化）
        Color(1, 1, 1, 0.9)
        # 箭头的三个点
        arrow_points = [
            btn_x + 5, btn_y + 15,  # 左上
            btn_x + 15, btn_y + 15,  # 右上
            btn_x + 10, btn_y + 5   # 下中
        ]
        Line(
            points=arrow_points,
            width=2
        )

    def _is_point_in_minimize_button(self, x, y):
        """
        检查点是否在最小化按钮内

        Args:
            x: x坐标
            y: y坐标

        Returns:
            bool: 点是否在最小化按钮内
        """
        btn_size = 20
        btn_x = self.x + self.overlay_width - btn_size - 5
        btn_y = self.y + self.overlay_height - btn_size - 5

        return (btn_x <= x <= btn_x + btn_size and
                btn_y <= y <= btn_y + btn_size)

    def toggle_minimize(self):
        """
        切换最小化状态
        """
        if self.is_minimized:
            self.restore()
        else:
            self.minimize()

    def minimize(self):
        """
        最小化悬浮框
        缩成小圆点
        """
        if self.is_minimized:
            return

        # 保存原始状态
        self.original_size = (self.overlay_width, self.overlay_height)
        self.original_pos = (self.x, self.y)

        # 切换到最小化状态
        self.is_minimized = True

        # 重新绘制
        self._draw_overlay()

    def restore(self):
        """
        恢复悬浮框
        从最小化状态恢复到正常状态
        """
        if not self.is_minimized:
            return

        # 恢复原始状态
        self.is_minimized = False
        self.overlay_width, self.overlay_height = self.original_size
        self.x, self.y = self.original_pos

        # 重新绘制
        self._draw_overlay()

    def open(self):
        """
        显示悬浮框
        将悬浮框添加到Window并绑定触摸事件
        """
        Window.add_widget(self)
        Window.bind(on_touch_down=self._on_window_touch_down)
        Window.bind(on_touch_move=self._on_window_touch_move)
        Window.bind(on_touch_up=self._on_window_touch_up)

    def close(self):
        """
        关闭悬浮框
        从Window移除悬浮框并解绑触摸事件
        """
        # 取消长按定时器
        if self.long_press_timer:
            self.long_press_timer.cancel()

        Window.remove_widget(self)
        Window.unbind(on_touch_down=self._on_window_touch_down)
        Window.unbind(on_touch_move=self._on_window_touch_move)
        Window.unbind(on_touch_up=self._on_window_touch_up)

    def _on_window_touch_down(self, window, touch):
        if self.is_minimized:
            if self._is_point_in_minimized(touch.x, touch.y):
                self.restore()
                return True
            return False

        if self._is_point_in_minimize_button(touch.x, touch.y):
            self.minimize()
            return True

        handle = self._detect_handle(touch.x, touch.y)
        if handle:
            self.isResizing = True
            self.resize_touch = touch
            self.resize_edge = handle
            self.resize_start_pos = (touch.x, touch.y)
            self.resize_start_size = (self.overlay_width, self.overlay_height)
            return True

        if self._is_point_in_overlay(touch.x, touch.y):
            self.gesture_handler.on_touch_down(
                touch,
                (self.x, self.y),
                (self.overlay_width, self.overlay_height)
            )

            self.long_press_timer = Clock.schedule_once(
                lambda dt: self._on_long_press(),
                self.long_press_threshold
            )

            self.isDragging = True
            self.drag_touch = touch
            self.drag_offset = (touch.x - self.x, touch.y - self.y)
            return True
        return False

    def _on_window_touch_move(self, window, touch):
        if self.is_minimized:
            if hasattr(self, '_minimized_dragging') and self._minimized_dragging:
                new_x = touch.x - self._minimized_drag_offset[0]
                new_y = touch.y - self._minimized_drag_offset[1]
                new_x, new_y = self.boundary.constrain_position(
                    new_x, new_y, self.minimized_size, self.minimized_size
                )
                self.x = new_x
                self.y = new_y
                self._draw_overlay()
                return True
            return False

        if self.long_press_timer and self.long_press_timer.is_triggered:
            self.long_press_timer.cancel()
            self.long_press_timer = None

        if self.isResizing and touch is self.resize_touch:
            self._handle_resize(touch)
            return True

        if self.isDragging and touch is self.drag_touch:
            new_x = touch.x - self.drag_offset[0]
            new_y = touch.y - self.drag_offset[1]
            new_x, new_y = self.boundary.constrain_position(
                new_x, new_y, self.overlay_width, self.overlay_height
            )
            self.x = new_x
            self.y = new_y
            self._draw_overlay()
            return True
        return False

    def _on_window_touch_up(self, window, touch):
        if self.is_minimized:
            self._minimized_dragging = False
            return False

        if self.long_press_timer and self.long_press_timer.is_triggered:
            self.long_press_timer.cancel()
            self.long_press_timer = None

        if touch is self.resize_touch:
            self.isResizing = False
            self.resize_touch = None
            self.resize_edge = None
            return True

        if touch is self.drag_touch:
            self.gesture_handler.on_touch_up(touch)
            self.isDragging = False
            self.drag_touch = None
            return True
        return False

    def _is_point_in_overlay(self, x, y):
        """
        检查点是否在悬浮框内

        Args:
            x: x坐标
            y: y坐标

        Returns:
            bool: 点是否在悬浮框内
        """
        return (self.x <= x <= self.x + self.overlay_width and
                self.y <= y <= self.y + self.overlay_height)

    def _is_point_in_minimized(self, x, y):
        """
        检查点是否在最小化圆点内

        Args:
            x: x坐标
            y: y坐标

        Returns:
            bool: 点是否在最小化圆点内
        """
        return (self.x <= x <= self.x + self.minimized_size and
                self.y <= y <= self.y + self.minimized_size)

    def _detect_handle(self, x, y):
        """
        检测触摸点是否在控制点上

        Args:
            x: x坐标
            y: y坐标

        Returns:
            str: 控制点位置或None
        """
        handle_size = self.handle_size
        half_handle = handle_size / 2

        # 左下角
        if (abs(x - self.x) < half_handle and
            abs(y - self.y) < half_handle):
            return 'bottom_left'

        # 右下角
        if (abs(x - (self.x + self.overlay_width)) < half_handle and
            abs(y - self.y) < half_handle):
            return 'bottom_right'

        # 左上角
        if (abs(x - self.x) < half_handle and
            abs(y - (self.y + self.overlay_height)) < half_handle):
            return 'top_left'

        # 右上角
        if (abs(x - (self.x + self.overlay_width)) < half_handle and
            abs(y - (self.y + self.overlay_height)) < half_handle):
            return 'top_right'

        return None

    def _handle_resize(self, touch):
        """
        处理尺寸调整

        Args:
            touch: 触摸事件
        """
        dx = touch.x - self.resize_start_pos[0]
        dy = touch.y - self.resize_start_pos[1]

        start_w, start_h = self.resize_start_size
        new_w, new_h = start_w, start_h

        # 根据控制点调整尺寸
        if 'right' in self.resize_edge:
            new_w = start_w + dx
        elif 'left' in self.resize_edge:
            new_w = start_w - dx

        if 'top' in self.resize_edge:
            new_h = start_h + dy
        elif 'bottom' in self.resize_edge:
            new_h = start_h - dy

        # 使用边界计算器约束尺寸
        new_w, new_h = self.boundary.constrain_size(new_w, new_h)

        # 计算新位置
        new_x, new_y = self.x, self.y

        if 'left' in self.resize_edge:
            new_x = self.x + self.overlay_width - new_w
        if 'bottom' in self.resize_edge:
            new_y = self.y + self.overlay_height - new_h

        # 使用边界计算器约束位置
        new_x, new_y = self.boundary.constrain_position(
            new_x, new_y, new_w, new_h
        )

        # 更新状态
        self.x = new_x
        self.y = new_y
        self.overlay_width = new_w
        self.overlay_height = new_h

        # 重新绘制
        self._draw_overlay()

    def _on_gesture(self, gesture_type, data):
        if gesture_type == 'double_tap':
            self._on_double_tap()
        elif gesture_type == 'long_press':
            self._on_long_press()
        elif gesture_type == 'resize_start':
            edge = data.get('edge')
            if edge:
                self.isResizing = True
                self.resize_edge = edge
                self.resize_start_pos = data.get('pos', (0, 0))
                self.resize_start_size = (self.overlay_width, self.overlay_height)

    def _on_double_tap(self):
        self.current_color_index = (self.current_color_index + 1) % len(self.color_modes)
        self.overlay_color = self.color_modes[self.current_color_index]
        self._draw_overlay()

    def _on_long_press(self):
        self.quick_menu = QuickMenu(overlay_widget=self)
        self.quick_menu.show(
            self.x + self.overlay_width / 2,
            self.y + self.overlay_height / 2
        )

    def resize(self, new_width, new_height):
        """
        调整悬浮框大小

        Args:
            new_width: 新宽度
            new_height: 新高度
        """
        # 使用边界计算器约束尺寸
        new_width, new_height = self.boundary.constrain_size(new_width, new_height)

        self.overlay_width = new_width
        self.overlay_height = new_height

        # 使用边界计算器约束位置
        self.x, self.y = self.boundary.constrain_position(
            self.x, self.y, self.overlay_width, self.overlay_height
        )

        # 重新绘制
        self._draw_overlay()

    def set_color(self, r, g, b, a):
        """
        设置悬浮框颜色

        Args:
            r: 红色分量 (0-1)
            g: 绿色分量 (0-1)
            b: 蓝色分量 (0-1)
            a: 透明度 (0-1)
        """
        self.overlay_color = (r, g, b, a)
        self._draw_overlay()

    def get_position(self):
        """
        获取悬浮框位置

        Returns:
            tuple: (x, y) 位置坐标
        """
        return (self.x, self.y)

    def get_size(self):
        """
        获取悬浮框大小

        Returns:
            tuple: (width, height) 宽度和高度
        """
        return (self.overlay_width, self.overlay_height)
