"""
悬浮窗管理模块
职责：管理悬浮窗的创建、显示、隐藏、移除和状态更新
作用：核心模块，负责悬浮窗的完整生命周期管理
通过PyJNIus调用Android WindowManager API实现真正的系统级悬浮窗
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

    通过PyJNIus调用Android WindowManager API创建系统级悬浮窗，
    支持拖动、调整大小、颜色切换、最小化等功能
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
        self._context = None

        # 是否为Android环境
        self._is_android = False

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

        # 检测是否为Android环境
        try:
            from jnius import autoclass
            self._is_android = True
        except ImportError:
            self._is_android = False
            logger.warning("非Android环境")

        logger.info(f"悬浮窗初始化: 屏幕 {screen_width}x{screen_height}, "
                     f"位置 ({self._pos_x}, {self._pos_y}), Android={self._is_android}")

    def is_active(self):
        """检查悬浮窗是否已激活"""
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
        """停止并移除悬浮窗"""
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

        通过PyJNIus调用Android WindowManager API创建系统级悬浮窗：
        1. 获取WindowManager系统服务
        2. 创建LayoutParams配置悬浮窗参数
        3. 创建Android View并设置背景颜色
        4. 调用windowManager.addView()将悬浮窗添加到屏幕
        """
        if not self._is_android:
            logger.warning("非Android环境，跳过悬浮窗创建")
            return

        try:
            from jnius import autoclass

            # 获取Android核心类
            Context = autoclass('android.content.Context')
            WindowManager = autoclass('android.view.WindowManager')
            LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
            PixelFormat = autoclass('android.graphics.PixelFormat')
            Gravity = autoclass('android.view.Gravity')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            View = autoclass('android.view.View')
            Color = autoclass('android.graphics.Color')
            Drawable = autoclass('android.graphics.drawable.ColorDrawable')

            # 获取系统上下文和服务
            self._context = PythonActivity.mActivity
            self._window_manager = self._context.getSystemService(
                Context.WINDOW_SERVICE
            )

            # 创建悬浮窗布局参数（使用固定尺寸而非WRAP_CONTENT）
            self._layout_params = LayoutParams(
                self._width,
                self._height,
                LayoutParams.TYPE_APPLICATION_OVERLAY,
                LayoutParams.FLAG_NOT_FOCUSABLE | LayoutParams.FLAG_NOT_TOUCH_MODAL,
                PixelFormat.TRANSLUCENT
            )

            # 设置初始位置
            self._layout_params.x = self._pos_x
            self._layout_params.y = self._pos_y
            self._layout_params.gravity = Gravity.TOP | Gravity.LEFT

            # 创建Android View作为悬浮窗
            self._overlay_view = View(self._context)

            # 设置背景颜色（半透明灰色）
            self._apply_view_color()

            # 添加悬浮窗到窗口
            self._window_manager.addView(self._overlay_view, self._layout_params)

            logger.info(f"悬浮窗视图创建成功: 位置({self._pos_x},{self._pos_y}), "
                         f"大小({self._width}x{self._height})")

        except ImportError:
            logger.warning("非Android环境，悬浮窗创建已跳过")
        except Exception as e:
            logger.error(f"创建悬浮窗视图失败: {e}")
            raise

    def _apply_view_color(self):
        """应用当前颜色到View"""
        if not self._overlay_view or not self._is_android:
            return

        try:
            from jnius import autoclass
            Color = autoclass('android.graphics.Color')
            ColorDrawable = autoclass('android.graphics.drawable.ColorDrawable')

            # 获取当前颜色RGBA (0-1范围)
            r, g, b, a = COLOR_PRESETS[self._color_index]['rgba']

            # 转换为Android Color格式 (0-255范围)
            color_int = Color.argb(
                int(a * 255),
                int(r * 255),
                int(g * 255),
                int(b * 255)
            )

            # 创建颜色背景
            drawable = ColorDrawable(color_int)
            self._overlay_view.setBackground(drawable)

            logger.debug(f"应用颜色: {COLOR_PRESETS[self._color_index]['name']}")
        except Exception as e:
            logger.error(f"应用颜色失败: {e}")

    def _remove_overlay_view(self):
        """移除悬浮窗视图"""
        if not self._is_android:
            return

        try:
            if self._window_manager and self._overlay_view:
                self._window_manager.removeView(self._overlay_view)
                self._overlay_view = None
                logger.info("悬浮窗视图已移除")
        except Exception as e:
            logger.error(f"移除悬浮窗视图失败: {e}")

    def _update_view_layout(self):
        """更新悬浮窗布局参数到WindowManager"""
        if not self._is_android or not self._window_manager or not self._overlay_view:
            return

        try:
            self._window_manager.updateViewLayout(
                self._overlay_view, self._layout_params
            )
        except Exception as e:
            logger.error(f"更新悬浮窗布局失败: {e}")

    def update_position(self, x, y):
        """
        更新悬浮窗位置

        参数:
            x (int): 新的X坐标
            y (int): 新的Y坐标
        """
        if self._boundary_checker:
            x, y = self._boundary_checker.ensure_visible(
                x, y, self._width, self._height
            )

        self._pos_x = x
        self._pos_y = y

        # 更新Android视图位置
        if self._layout_params:
            self._layout_params.x = x
            self._layout_params.y = y
            self._update_view_layout()

        logger.debug(f"位置更新: ({x}, {y})")

    def update_size(self, width, height):
        """
        更新悬浮窗大小

        参数:
            width (int): 新的宽度
            height (int): 新的高度
        """
        if self._boundary_checker:
            width, height = self._boundary_checker.constrain_size(width, height)

        self._width = width
        self._height = height

        # 更新Android视图大小
        if self._overlay_view and self._is_android:
            try:
                from jnius import autoclass
                LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
                params = self._overlay_view.getLayoutParams()
                params.width = width
                params.height = height
                self._overlay_view.setLayoutParams(params)
                self._update_view_layout()
            except Exception as e:
                logger.error(f"更新视图大小失败: {e}")

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
            self._apply_view_color()
            logger.debug(f"颜色更新: {COLOR_PRESETS[color_index]['name']}")

    def switch_color(self):
        """切换到下一个颜色（循环切换）"""
        next_index = (self._color_index + 1) % len(COLOR_PRESETS)
        self.update_color(next_index)

    def toggle_minimize(self):
        """切换最小化模式"""
        self._is_minimized = not self._is_minimized

        if self._is_minimized:
            # 最小化：缩小View
            self.update_size(30, 30)
            logger.info("最小化模式: 开启")
        else:
            # 恢复：还原View
            self.update_size(OVERLAY_DEFAULT_WIDTH, OVERLAY_DEFAULT_HEIGHT)
            logger.info("最小化模式: 关闭")

    def get_position(self):
        """获取当前悬浮窗位置"""
        return self._pos_x, self._pos_y

    def get_size(self):
        """获取当前悬浮窗大小"""
        return self._width, self._height

    def get_color_rgba(self):
        """获取当前颜色的RGBA值"""
        return COLOR_PRESETS[self._color_index]['rgba']

    def get_color_index(self):
        """获取当前颜色索引"""
        return self._color_index
