"""
触摸处理模块
职责：处理悬浮窗的所有触摸交互事件
作用：实现拖动移动、双击切换颜色、长按菜单等交互功能
"""

import logging
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.constants import OVERLAY_MINIMIZED_SIZE

logger = logging.getLogger(__name__)


class TouchHandler:
    """
    触摸处理器类
    
    处理悬浮窗的各种触摸交互：
    - 单指拖动：移动悬浮窗位置
    - 双击：切换颜色
    - 长按：弹出快捷菜单
    """
    
    def __init__(self, overlay_manager):
        """
        初始化触摸处理器
        
        参数:
            overlay_manager (OverlayManager): 悬浮窗管理器实例
        """
        self._overlay_manager = overlay_manager
        
        # 触摸状态
        self._touch_start_time = 0
        self._touch_start_pos = (0, 0)
        self._last_touch_time = 0
        self._touch_count = 0
        
        # 配置参数
        self._long_press_duration = 0.5  # 长按时间（秒）
        self._double_click_interval = 0.3  # 双击间隔（秒）
        self._drag_threshold = 10  # 拖动阈值（像素）
        
        # 回调函数
        self._on_double_click = None
        self._on_long_press = None
        
        logger.info("触摸处理器初始化完成")
    
    def set_double_click_callback(self, callback):
        """
        设置双击回调函数
        
        参数:
            callback (function): 双击时调用的函数
        """
        self._on_double_click = callback
    
    def set_long_press_callback(self, callback):
        """
        设置长按回调函数
        
        参数:
            callback (function): 长按时调用的函数
        """
        self._on_long_press = callback
    
    def on_touch_down(self, x, y):
        """
        触摸按下事件处理
        
        参数:
            x (int): 触摸点X坐标
            y (int): 触摸点Y坐标
        """
        current_time = time.time()
        
        # 记录触摸开始时间和位置
        self._touch_start_time = current_time
        self._touch_start_pos = (x, y)
        
        # 检测双击
        if current_time - self._last_touch_time < self._double_click_interval:
            self._touch_count += 1
            if self._touch_count >= 2:
                # 双击检测到
                logger.debug("检测到双击")
                self._handle_double_click()
                self._touch_count = 0
                return
        else:
            self._touch_count = 1
        
        self._last_touch_time = current_time
        logger.info(f"触摸按下: ({x}, {y})")
    
    def on_touch_move(self, x, y):
        """
        触摸移动事件处理（拖动）
        
        参数:
            x (int): 当前触摸点X坐标
            y (int): 当前触摸点Y坐标
        """
        if not self._overlay_manager.is_active():
            return
        
        # 如果是最小化模式，不允许拖动
        if self._overlay_manager._is_minimized:
            return
        
        # 计算移动距离
        start_x, start_y = self._touch_start_pos
        dx = x - start_x
        dy = y - start_y
        
        # 如果移动距离超过阈值，视为拖动
        if abs(dx) > self._drag_threshold or abs(dy) > self._drag_threshold:
            # 获取当前悬浮窗位置
            current_x, current_y = self._overlay_manager.get_position()
            
            # 计算新位置
            new_x = current_x + dx
            new_y = current_y + dy
            
            # 更新位置
            self._overlay_manager.update_position(new_x, new_y)
            
            # 更新触摸起始位置
            self._touch_start_pos = (x, y)

            logger.info(f"拖动: ({dx}, {dy}), 新位置: ({new_x}, {new_y})")
    
    def on_touch_up(self, x, y):
        """
        触摸抬起事件处理
        
        参数:
            x (int): 触摸点X坐标
            y (int): 触摸点Y坐标
        """
        current_time = time.time()
        press_duration = current_time - self._touch_start_time
        
        # 检测长按
        if press_duration >= self._long_press_duration:
            # 计算移动距离
            start_x, start_y = self._touch_start_pos
            dx = abs(x - start_x)
            dy = abs(y - start_y)
            
            # 如果没有明显移动，视为长按
            if dx < self._drag_threshold and dy < self._drag_threshold:
                logger.debug("检测到长按")
                self._handle_long_press()
        
        logger.info(f"触摸抬起: ({x}, {y})")
    
    def _handle_double_click(self):
        """处理双击事件"""
        if self._on_double_click:
            self._on_double_click()
        else:
            # 默认行为：切换颜色
            self._overlay_manager.switch_color()
            logger.info("双击切换颜色")
    
    def _handle_long_press(self):
        """处理长按事件"""
        if self._on_long_press:
            self._on_long_press()
        else:
            # 默认行为：打印日志（实际应用中应弹出菜单）
            logger.info("长按触发（菜单功能待实现）")
    
    def is_point_inside(self, touch_x, touch_y, overlay_x, overlay_y, 
                        overlay_width, overlay_height):
        """
        检测触摸点是否在悬浮窗区域内
        
        参数:
            touch_x (int): 触摸点X坐标
            touch_y (int): 触摸点Y坐标
            overlay_x (int): 悬浮窗X坐标
            overlay_y (int): 悬浮窗Y坐标
            overlay_width (int): 悬浮窗宽度
            overlay_height (int): 悬浮窗高度
        
        返回:
            bool: True=在区域内, False=不在区域内
        """
        return (overlay_x <= touch_x <= overlay_x + overlay_width and
                overlay_y <= touch_y <= overlay_y + overlay_height)
    
    def get_resize_edge(self, touch_x, touch_y, overlay_x, overlay_y,
                        overlay_width, overlay_height, edge_size=20):
        """
        检测触摸点是否在悬浮窗边缘（用于调整大小）
        
        参数:
            touch_x (int): 触摸点X坐标
            touch_y (int): 触摸点Y坐标
            overlay_x (int): 悬浮窗X坐标
            overlay_y (int): 悬浮窗Y坐标
            overlay_width (int): 悬浮窗宽度
            overlay_height (int): 悬浮窗高度
            edge_size (int): 边缘检测大小（像素）
        
        返回:
            str: 边缘位置 ('left', 'right', 'top', 'bottom', 'top_left', 
                 'top_right', 'bottom_left', 'bottom_right', None)
        """
        # 检测是否在悬浮窗区域内
        if not self.is_point_inside(touch_x, touch_y, overlay_x, overlay_y,
                                    overlay_width, overlay_height):
            return None
        
        # 计算各边缘距离
        dist_left = touch_x - overlay_x
        dist_right = (overlay_x + overlay_width) - touch_x
        dist_top = touch_y - overlay_y
        dist_bottom = (overlay_y + overlay_height) - touch_y
        
        # 检测四角
        if dist_left < edge_size and dist_top < edge_size:
            return 'top_left'
        if dist_right < edge_size and dist_top < edge_size:
            return 'top_right'
        if dist_left < edge_size and dist_bottom < edge_size:
            return 'bottom_left'
        if dist_right < edge_size and dist_bottom < edge_size:
            return 'bottom_right'
        
        # 检测四边
        if dist_left < edge_size:
            return 'left'
        if dist_right < edge_size:
            return 'right'
        if dist_top < edge_size:
            return 'top'
        if dist_bottom < edge_size:
            return 'bottom'
        
        return None
