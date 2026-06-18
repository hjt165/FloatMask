"""
手势处理器模块
处理悬浮框的拖动、缩放、双击、长按等手势操作
"""

import time
from kivy.core.window import Window


class GestureHandler:
    """
    手势处理器
    识别和处理各种手势操作
    """

    def __init__(self, callback=None):
        """
        初始化手势处理器

        Args:
            callback: 手势回调函数，接收(gesture_type, data)参数
        """
        self.callback = callback

        # 手势状态
        self.touch_start_time = 0
        self.touch_start_pos = (0, 0)
        self.last_touch_time = 0
        self.tap_count = 0
        self.long_press_threshold = 0.5  # 长按阈值（秒）
        self.double_tap_threshold = 0.3  # 双击阈值（秒）
        self.move_threshold = 10  # 移动阈值（像素）

        # 多点触控状态
        self.touches = {}
        self.initial_distance = 0
        self.initial_size = (0, 0)

    def on_touch_down(self, touch, overlay_pos, overlay_size):
        """
        触摸按下事件处理

        Args:
            touch: 触摸事件
            overlay_pos: 悬浮框位置 (x, y)
            overlay_size: 悬浮框大小 (width, height)

        Returns:
            str: 手势类型或None
        """
        # 记录触摸信息
        self.touch_start_time = time.time()
        self.touch_start_pos = (touch.x, touch.y)

        # 检查是否为双击
        current_time = time.time()
        if current_time - self.last_touch_time < self.double_tap_threshold:
            self.tap_count += 1
            if self.tap_count >= 2:
                self.tap_count = 0
                self._trigger_callback('double_tap', {
                    'pos': (touch.x, touch.y)
                })
                return 'double_tap'
        else:
            self.tap_count = 1

        self.last_touch_time = current_time

        # 检查触摸位置（边角用于调整大小）
        edge = self._detect_edge(touch.x, touch.y, overlay_pos, overlay_size)
        if edge:
            self._trigger_callback('resize_start', {
                'edge': edge,
                'pos': (touch.x, touch.y)
            })
            return 'resize_start'

        return None

    def on_touch_move(self, touch, overlay_pos, overlay_size):
        """
        触摸移动事件处理

        Args:
            touch: 触摸事件
            overlay_pos: 悬浮框位置 (x, y)
            overlay_size: 悬浮框大小 (width, height)

        Returns:
            str: 手势类型或None
        """
        # 计算移动距离
        dx = touch.x - self.touch_start_pos[0]
        dy = touch.y - self.touch_start_pos[1]
        distance = (dx**2 + dy**2)**0.5

        # 超过移动阈值，识别为拖动
        if distance > self.move_threshold:
            self._trigger_callback('drag', {
                'pos': (touch.x, touch.y),
                'delta': (dx, dy)
            })
            return 'drag'

        return None

    def on_touch_up(self, touch):
        """
        触摸释放事件处理

        Args:
            touch: 触摸事件

        Returns:
            str: 手势类型或None
        """
        # 检查是否为长按
        duration = time.time() - self.touch_start_time
        if duration >= self.long_press_threshold:
            self._trigger_callback('long_press', {
                'pos': (touch.x, touch.y),
                'duration': duration
            })
            return 'long_press'

        return None

    def _detect_edge(self, x, y, overlay_pos, overlay_size):
        """
        检测触摸位置是否在悬浮框边缘

        Args:
            x: 触摸x坐标
            y: 触摸y坐标
            overlay_pos: 悬浮框位置 (x, y)
            overlay_size: 悬浮框大小 (width, height)

        Returns:
            str: 边缘位置或None ('left', 'right', 'top', 'bottom', 'corner')
        """
        ox, oy = overlay_pos
        ow, oh = overlay_size
        edge_threshold = 20  # 边缘检测阈值（像素）

        # 检测四角
        if abs(x - ox) < edge_threshold and abs(y - oy) < edge_threshold:
            return 'bottom_left'
        if abs(x - (ox + ow)) < edge_threshold and abs(y - oy) < edge_threshold:
            return 'bottom_right'
        if abs(x - ox) < edge_threshold and abs(y - (oy + oh)) < edge_threshold:
            return 'top_left'
        if abs(x - (ox + ow)) < edge_threshold and abs(y - (oy + oh)) < edge_threshold:
            return 'top_right'

        # 检测四边
        if abs(x - ox) < edge_threshold:
            return 'left'
        if abs(x - (ox + ow)) < edge_threshold:
            return 'right'
        if abs(y - oy) < edge_threshold:
            return 'bottom'
        if abs(y - (oy + oh)) < edge_threshold:
            return 'top'

        return None

    def calculate_resize(self, touch_pos, edge, overlay_pos, overlay_size, min_size, max_size):
        """
        计算调整大小后的新尺寸和位置

        Args:
            touch_pos: 当前触摸位置 (x, y)
            edge: 边缘位置
            overlay_pos: 悬浮框位置 (x, y)
            overlay_size: 悬浮框大小 (width, height)
            min_size: 最小尺寸 (width, height)
            max_size: 最大尺寸 (width, height)

        Returns:
            tuple: ((new_x, new_y), (new_width, new_height))
        """
        ox, oy = overlay_pos
        ow, oh = overlay_size
        tx, ty = touch_pos

        new_x, new_y = ox, oy
        new_w, new_h = ow, oh

        # 根据边缘计算新尺寸
        if 'left' in edge:
            new_w = ow + (ox - tx)
            new_x = tx
        elif 'right' in edge:
            new_w = tx - ox

        if 'bottom' in edge:
            new_h = oh + (oy - ty)
            new_y = ty
        elif 'top' in edge:
            new_h = ty - oy

        # 应用尺寸限制
        new_w = max(min_size[0], min(new_w, max_size[0]))
        new_h = max(min_size[1], min(new_h, max_size[1]))

        # 确保位置正确
        if 'left' in edge:
            new_x = ox + ow - new_w
        if 'bottom' in edge:
            new_y = oy + oh - new_h

        return (new_x, new_y), (new_w, new_h)

    def _trigger_callback(self, gesture_type, data):
        """
        触发回调函数

        Args:
            gesture_type: 手势类型
            data: 手势数据
        """
        if self.callback:
            self.callback(gesture_type, data)


class MultiTouchHandler:
    """
    多点触控处理器
    处理双指缩放等多点触控手势
    """

    def __init__(self, callback=None):
        """
        初始化多点触控处理器

        Args:
            callback: 手势回调函数
        """
        self.callback = callback
        self.touches = {}
        self.initial_distance = 0
        self.initial_size = (0, 0)

    def on_touch_down(self, touch, overlay_size):
        """
        触摸按下事件处理

        Args:
            touch: 触摸事件
            overlay_size: 悬浮框大小 (width, height)
        """
        self.touches[touch.uid] = (touch.x, touch.y)

        # 如果有两个触摸点，计算初始距离
        if len(self.touches) == 2:
            points = list(self.touches.values())
            self.initial_distance = self._calculate_distance(points[0], points[1])
            self.initial_size = overlay_size

    def on_touch_move(self, touch):
        """
        触摸移动事件处理

        Args:
            touch: 触摸事件

        Returns:
            float: 缩放比例或None
        """
        if touch.uid in self.touches:
            self.touches[touch.uid] = (touch.x, touch.y)

        # 如果有两个触摸点，计算缩放比例
        if len(self.touches) == 2:
            points = list(self.touches.values())
            current_distance = self._calculate_distance(points[0], points[1])

            if self.initial_distance > 0:
                scale = current_distance / self.initial_distance
                self._trigger_callback('pinch', {'scale': scale})
                return scale

        return None

    def on_touch_up(self, touch):
        """
        触摸释放事件处理

        Args:
            touch: 触摸事件
        """
        if touch.uid in self.touches:
            del self.touches[touch.uid]

    def _calculate_distance(self, point1, point2):
        """
        计算两点之间的距离

        Args:
            point1: 点1 (x, y)
            point2: 点2 (x, y)

        Returns:
            float: 两点距离
        """
        dx = point2[0] - point1[0]
        dy = point2[1] - point1[1]
        return (dx**2 + dy**2)**0.5

    def _trigger_callback(self, gesture_type, data):
        """
        触发回调函数

        Args:
            gesture_type: 手势类型
            data: 手势数据
        """
        if self.callback:
            self.callback(gesture_type, data)
