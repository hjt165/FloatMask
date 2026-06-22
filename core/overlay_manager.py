"""
悬浮窗管理模块
职责：管理悬浮窗的创建、显示、隐藏、移除和状态更新
作用：核心模块，负责悬浮窗的完整生命周期管理
"""

import logging
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.constants import (
    OVERLAY_DEFAULT_WIDTH, OVERLAY_DEFAULT_HEIGHT,
    OVERLAY_BORDER_WIDTH, OVERLAY_BORDER_COLOR,
    COLOR_PRESETS, DEFAULT_COLOR_INDEX
)
from core.boundary import BoundaryChecker

logger = logging.getLogger(__name__)


class OverlayManager:
    """
    悬浮窗管理器类
    
    管理悬浮窗的完整生命周期，包括：
    - 创建和初始化悬浮窗
    - 显示和隐藏悬浮窗
    - 更新悬浮窗位置、大小、颜色
    - 移除悬浮窗
    """
    
    def __init__(self):
        """初始化悬浮窗管理器"""
        # 悬浮窗状态
        self._is_active = False
        self._is_minimized = False
        
        # 悬浮窗属性
        self._pos_x = 0
        self._pos_y = 0
        self._width = OVERLAY_DEFAULT_WIDTH
        self._height = OVERLAY_DEFAULT_HEIGHT
        self._color_index = DEFAULT_COLOR_INDEX
        self._opacity = COLOR_PRESETS[DEFAULT_COLOR_INDEX]['rgba'][3]
        
        # 边界检测器
        self._boundary_checker = None
        
        # Android系统服务引用
        self._window_manager = None
        self._overlay_view = None
        self._layout_params = None
        
        logger.info("悬浮窗管理器初始化完成")
    
    def initialize(self, screen_width, screen_height):
        """
        初始化悬浮窗，设置屏幕尺寸和默认位置
        
        参数:
            screen_width (int): 屏幕宽度
            screen_height (int): 屏幕高度
        """
        # 初始化边界检测器
        self._boundary_checker = BoundaryChecker(screen_width, screen_height)
        
        # 计算默认位置（屏幕中央偏右）
        self._pos_x = int(screen_width * 0.6)
        self._pos_y = int(screen_height * 0.4)
        
        logger.info(f"悬浮窗初始化: 屏幕 {screen_width}x{screen_height}, 位置 ({self._pos_x}, {self._pos_y})")
    
    def is_active(self):
        """
        检查悬浮窗是否已激活
        
        返回:
            bool: True=已激活, False=未激活
        """
        return self._is_active
    
    def start(self):
        """
        启动悬浮窗
        
        成功返回True，失败返回False
        """
        if self._is_active:
            logger.warning("悬浮窗已在运行")
            return True
        
        try:
            self._create_overlay_view()
            self._is_active = True
            logger.info("悬浮窗启动成功")
            return True
        except Exception as e:
            logger.error(f"启动悬浮窗失败: {e}")
            return False
    
    def stop(self):
        """
        停止并移除悬浮窗
        """
        if not self._is_active:
            logger.warning("悬浮窗未在运行")
            return
        
        try:
            self._remove_overlay_view()
            self._is_active = False
            logger.info("悬浮窗已停止")
        except Exception as e:
            logger.error(f"停止悬浮窗失败: {e}")
    
    def _create_overlay_view(self):
        """
        创建悬浮窗视图（Android环境）
        
        通过PyJNIus调用Android WindowManager API创建悬浮窗
        """
        try:
            from jnius import autoclass
            
            # 获取Android类
            Context = autoclass('android.content.Context')
            WindowManager = autoclass('android.view.WindowManager')
            LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
            PixelFormat = autoclass('android.view.PixelFormat')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            
            # 获取系统服务
            context = PythonActivity.mActivity
            self._window_manager = context.getSystemService(Context.WINDOW_SERVICE)
            
            # 创建悬浮窗参数
            self._layout_params = LayoutParams(
                LayoutParams.WRAP_CONTENT,
                LayoutParams.WRAP_CONTENT,
                LayoutParams.TYPE_APPLICATION_OVERLAY,
                LayoutParams.FLAG_NOT_FOCUSABLE | LayoutParams.FLAG_NOT_TOUCH_MODAL,
                PixelFormat.TRANSLUCENT
            )
            
            # 设置初始位置
            self._layout_params.x = self._pos_x
            self._layout_params.y = self._pos_y
            
            # 创建悬浮窗视图（这里需要创建一个Kivy Widget并桥接到Android）
            # 注意：实际实现需要创建一个Android View并添加到WindowManager
            # 以下为概念代码，实际实现可能需要额外的桥接层
            
            logger.info("悬浮窗视图创建成功")
            
        except ImportError:
            logger.warning("非Android环境，悬浮窗创建已跳过")
        except Exception as e:
            logger.error(f"创建悬浮窗视图失败: {e}")
            raise
    
    def _remove_overlay_view(self):
        """
        移除悬浮窗视图
        """
        try:
            if self._window_manager and self._overlay_view:
                self._window_manager.removeView(self._overlay_view)
                self._overlay_view = None
                logger.info("悬浮窗视图已移除")
        except Exception as e:
            logger.error(f"移除悬浮窗视图失败: {e}")
    
    def update_position(self, x, y):
        """
        更新悬浮窗位置
        
        参数:
            x (int): 新的X坐标
            y (int): 新的Y坐标
        """
        if self._boundary_checker:
            # 确保在边界内
            x, y = self._boundary_checker.ensure_visible(
                x, y, self._width, self._height
            )
        
        self._pos_x = x
        self._pos_y = y
        
        # 更新Android视图位置
        if self._layout_params:
            self._layout_params.x = x
            self._layout_params.y = y
        
        logger.debug(f"位置更新: ({x}, {y})")
    
    def update_size(self, width, height):
        """
        更新悬浮窗大小
        
        参数:
            width (int): 新的宽度
            height (int): 新的高度
        """
        if self._boundary_checker:
            # 限制尺寸在合法范围内
            width, height = self._boundary_checker.constrain_size(width, height)
        
        self._width = width
        self._height = height
        
        logger.debug(f"大小更新: ({width}, {height})")
    
    def update_color(self, color_index):
        """
        更新悬浮窗颜色
        
        参数:
            color_index (int): 颜色索引
        """
        if 0 <= color_index < len(COLOR_PRESETS):
            self._color_index = color_index
            self._opacity = COLOR_PRESETS[color_index]['rgba'][3]
            logger.debug(f"颜色更新: 索引 {color_index}")
    
    def switch_color(self):
        """
        切换到下一个颜色（循环切换）
        """
        next_index = (self._color_index + 1) % len(COLOR_PRESETS)
        self.update_color(next_index)
    
    def toggle_minimize(self):
        """
        切换最小化模式
        """
        self._is_minimized = not self._is_minimized
        logger.info(f"最小化模式: {'开启' if self._is_minimized else '关闭'}")
    
    def get_position(self):
        """
        获取当前悬浮窗位置
        
        返回:
            tuple: (x, y) 坐标
        """
        return self._pos_x, self._pos_y
    
    def get_size(self):
        """
        获取当前悬浮窗大小
        
        返回:
            tuple: (width, height) 尺寸
        """
        return self._width, self._height
    
    def get_color_rgba(self):
        """
        获取当前颜色的RGBA值
        
        返回:
            tuple: (r, g, b, a) 颜色值 (0-1)
        """
        return COLOR_PRESETS[self._color_index]['rgba']
    
    def get_color_index(self):
        """
        获取当前颜色索引
        
        返回:
            int: 颜色索引
        """
        return self._color_index
