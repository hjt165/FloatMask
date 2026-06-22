"""
边界检测模块
职责：检测悬浮窗是否在屏幕边界内，确保至少20%在可视区域
作用：防止用户将悬浮窗完全拖出屏幕导致无法操作
"""

import logging
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.constants import BOUNDARY_MIN_VISIBLE_RATIO

logger = logging.getLogger(__name__)


class BoundaryChecker:
    """
    边界检测器类
    
    用于检测悬浮窗位置是否在屏幕边界内，
    确保至少指定比例的面积在可视区域内
    """
    
    def __init__(self, screen_width, screen_height):
        """
        初始化边界检测器
        
        参数:
            screen_width (int): 屏幕宽度
            screen_height (int): 屏幕高度
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        logger.info(f"边界检测器初始化: 屏幕尺寸 {screen_width}x{screen_height}")
    
    def update_screen_size(self, width, height):
        """
        更新屏幕尺寸（例如屏幕旋转时）
        
        参数:
            width (int): 新的屏幕宽度
            height (int): 新的屏幕高度
        """
        self.screen_width = width
        self.screen_height = height
        logger.info(f"屏幕尺寸更新: {width}x{height}")
    
    def calculate_visible_area(self, x, y, width, height):
        """
        计算悬浮窗在屏幕内的可见面积
        
        参数:
            x (int): 悬浮窗左上角X坐标
            y (int): 悬浮窗左上角Y坐标
            width (int): 悬浮窗宽度
            height (int): 悬浮窗高度
        
        返回:
            float: 可见面积（像素平方）
        """
        # 计算悬浮窗四个角的坐标
        left = x
        right = x + width
        top = y
        bottom = y + height
        
        # 计算在屏幕内的可见区域
        visible_left = max(0, left)
        visible_right = min(self.screen_width, right)
        visible_top = max(0, top)
        visible_bottom = min(self.screen_height, bottom)
        
        # 如果完全在屏幕外，返回0
        if visible_left >= visible_right or visible_top >= visible_bottom:
            return 0.0
        
        # 计算可见面积
        visible_width = visible_right - visible_left
        visible_height = visible_bottom - visible_top
        return visible_width * visible_height
    
    def calculate_visible_ratio(self, x, y, width, height):
        """
        计算悬浮窗在屏幕内的可见比例
        
        参数:
            x (int): 悬浮窗左上角X坐标
            y (int): 悬浮窗左上角Y坐标
            width (int): 悬浮窗宽度
            height (int): 悬浮窗高度
        
        返回:
            float: 可见比例 (0.0-1.0)
        """
        total_area = width * height
        if total_area == 0:
            return 0.0
        
        visible_area = self.calculate_visible_area(x, y, width, height)
        return visible_area / total_area
    
    def is_within_boundary(self, x, y, width, height, min_ratio=None):
        """
        检测悬浮窗是否在边界内（至少指定比例在屏幕内）
        
        参数:
            x (int): 悬浮窗左上角X坐标
            y (int): 悬浮窗左上角Y坐标
            width (int): 悬浮窗宽度
            height (int): 悬浮窗高度
            min_ratio (float): 最小可见比例，默认为BOUNDARY_MIN_VISIBLE_RATIO
        
        返回:
            bool: True=在边界内, False=超出边界
        """
        if min_ratio is None:
            min_ratio = BOUNDARY_MIN_VISIBLE_RATIO
        
        visible_ratio = self.calculate_visible_ratio(x, y, width, height)
        is_valid = visible_ratio >= min_ratio
        
        if not is_valid:
            logger.debug(f"悬浮窗超出边界: 可见比例 {visible_ratio:.2%} < {min_ratio:.2%}")
        
        return is_valid
    
    def ensure_visible(self, x, y, width, height, min_ratio=None):
        """
        确保悬浮窗在边界内，如果超出则调整位置
        
        参数:
            x (int): 悬浮窗左上角X坐标
            y (int): 悬浮窗左上角Y坐标
            width (int): 悬浮窗宽度
            height (int): 悬浮窗高度
            min_ratio (float): 最小可见比例
        
        返回:
            tuple: (new_x, new_y) 调整后的坐标
        """
        if min_ratio is None:
            min_ratio = BOUNDARY_MIN_VISIBLE_RATIO
        
        # 如果已经在边界内，直接返回
        if self.is_within_boundary(x, y, width, height, min_ratio):
            return x, y
        
        # 计算需要保持的最小可见尺寸
        min_visible_width = width * min_ratio
        min_visible_height = height * min_ratio
        
        # 计算合理的坐标范围
        # X坐标范围：[-(width - min_visible_width), screen_width - min_visible_width]
        min_x = -(width - min_visible_width)
        max_x = self.screen_width - min_visible_width
        
        # Y坐标范围：[-(height - min_visible_height), screen_height - min_visible_height]
        min_y = -(height - min_visible_height)
        max_y = self.screen_height - min_visible_height
        
        # 限制坐标在合理范围内
        new_x = max(min_x, min(max_x, x))
        new_y = max(min_y, min(max_y, y))
        
        logger.info(f"位置调整: ({x}, {y}) -> ({new_x}, {new_y})")
        return new_x, new_y
    
    def constrain_size(self, width, height, min_width=None, min_height=None, 
                       max_width=None, max_height=None):
        """
        限制悬浮窗尺寸在合法范围内
        
        参数:
            width (int): 原始宽度
            height (int): 原始高度
            min_width (int): 最小宽度
            min_height (int): 最小高度
            max_width (int): 最大宽度
            max_height (int): 最大高度
        
        返回:
            tuple: (new_width, new_height) 调整后的尺寸
        """
        from ..utils.constants import (
            OVERLAY_MIN_WIDTH, OVERLAY_MIN_HEIGHT,
            OVERLAY_MAX_WIDTH_RATIO, OVERLAY_MAX_HEIGHT_RATIO
        )
        
        if min_width is None:
            min_width = OVERLAY_MIN_WIDTH
        if min_height is None:
            min_height = OVERLAY_MIN_HEIGHT
        if max_width is None:
            max_width = int(self.screen_width * OVERLAY_MAX_WIDTH_RATIO)
        if max_height is None:
            max_height = int(self.screen_height * OVERLAY_MAX_HEIGHT_RATIO)
        
        # 限制尺寸
        new_width = max(min_width, min(max_width, width))
        new_height = max(min_height, min(max_height, height))
        
        if new_width != width or new_height != height:
            logger.info(f"尺寸调整: ({width}, {height}) -> ({new_width}, {new_height})")
        
        return new_width, new_height
