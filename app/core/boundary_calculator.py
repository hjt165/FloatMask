"""
边界计算器模块
计算悬浮框的位置和尺寸限制，确保悬浮框在屏幕可视区域内
"""

from kivy.core.window import Window


class BoundaryCalculator:
    """
    边界计算器
    负责计算悬浮框的位置和尺寸约束
    """

    def __init__(self):
        """
        初始化边界计算器
        """
        # 屏幕尺寸
        self.screen_width = Window.width
        self.screen_height = Window.height

        # 尺寸限制
        self.min_width = 80
        self.min_height = 80
        self.max_width_ratio = 0.3  # 屏幕宽度的30%
        self.max_height_ratio = 0.3  # 屏幕高度的30%

        # 可视区域限制
        self.visible_area_percent = 0.2  # 至少20%在可视区域内

        # 绑定窗口大小变化事件
        Window.bind(on_resize=self._on_window_resize)

    def _on_window_resize(self, window, width, height):
        """
        窗口大小变化事件处理

        Args:
            window: Window对象
            width: 新宽度
            height: 新高度
        """
        self.screen_width = width
        self.screen_height = height

    def get_max_size(self):
        """
        获取最大允许尺寸

        Returns:
            tuple: (max_width, max_height)
        """
        max_width = int(self.screen_width * self.max_width_ratio)
        max_height = int(self.screen_height * self.max_height_ratio)
        return (max_width, max_height)

    def get_min_size(self):
        """
        获取最小允许尺寸

        Returns:
            tuple: (min_width, min_height)
        """
        return (self.min_width, self.min_height)

    def constrain_size(self, width, height):
        """
        约束尺寸在允许范围内

        Args:
            width: 目标宽度
            height: 目标高度

        Returns:
            tuple: (约束后的width, 约束后的height)
        """
        min_w, min_h = self.get_min_size()
        max_w, max_h = self.get_max_size()

        # 约束宽度
        constrained_width = max(min_w, min(width, max_w))

        # 约束高度
        constrained_height = max(min_h, min(height, max_h))

        return (constrained_width, constrained_height)

    def constrain_position(self, x, y, width, height):
        """
        约束位置确保至少指定百分比的悬浮框在可视区域内

        Args:
            x: 目标x坐标
            y: 目标y坐标
            width: 悬浮框宽度
            height: 悬浮框高度

        Returns:
            tuple: (约束后的x, 约束后的y)
        """
        # 计算最小可见区域
        min_visible_x = width * self.visible_area_percent
        min_visible_y = height * self.visible_area_percent

        # 约束x坐标
        if x < -width + min_visible_x:
            x = -width + min_visible_x
        elif x > self.screen_width - min_visible_x:
            x = self.screen_width - min_visible_x

        # 约束y坐标
        if y < -height + min_visible_y:
            y = -height + min_visible_y
        elif y > self.screen_height - min_visible_y:
            y = self.screen_height - min_visible_y

        return (x, y)

    def calculate_initial_position(self, width, height):
        """
        计算初始位置（屏幕中央偏右）

        Args:
            width: 悬浮框宽度
            height: 悬浮框高度

        Returns:
            tuple: (x, y) 初始位置
        """
        # 屏幕中央偏右
        x = self.screen_width - width - 50
        y = (self.screen_height - height) / 2

        # 确保在边界内
        x, y = self.constrain_position(x, y, width, height)

        return (x, y)

    def check_collision(self, pos1, size1, pos2, size2):
        """
        检查两个矩形是否碰撞

        Args:
            pos1: 矩形1位置 (x, y)
            size1: 矩形1大小 (width, height)
            pos2: 矩形2位置 (x, y)
            size2: 矩形2大小 (width, height)

        Returns:
            bool: 是否碰撞
        """
        x1, y1 = pos1
        w1, h1 = size1
        x2, y2 = pos2
        w2, h2 = size2

        # 检查是否重叠
        return (x1 < x2 + w2 and
                x1 + w1 > x2 and
                y1 < y2 + h2 and
                y1 + h1 > y2)

    def get_visible_area(self, x, y, width, height):
        """
        计算悬浮框在屏幕内的可见面积比例

        Args:
            x: 悬浮框x坐标
            y: 悬浮框y坐标
            width: 悬浮框宽度
            height: 悬浮框高度

        Returns:
            float: 可见面积比例 (0-1)
        """
        # 计算在屏幕内的部分
        visible_x1 = max(0, x)
        visible_y1 = max(0, y)
        visible_x2 = min(self.screen_width, x + width)
        visible_y2 = min(self.screen_height, y + height)

        # 计算可见面积
        visible_width = max(0, visible_x2 - visible_x1)
        visible_height = max(0, visible_y2 - visible_y1)
        visible_area = visible_width * visible_height

        # 计算总面积
        total_area = width * height

        # 返回比例
        if total_area > 0:
            return visible_area / total_area
        return 0

    def is_position_valid(self, x, y, width, height):
        """
        检查位置是否有效（满足最小可见区域要求）

        Args:
            x: 悬浮框x坐标
            y: 悬浮框y坐标
            width: 悬浮框宽度
            height: 悬浮框高度

        Returns:
            bool: 位置是否有效
        """
        visible_percent = self.get_visible_area(x, y, width, height)
        return visible_percent >= self.visible_area_percent
