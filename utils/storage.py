"""
存储管理模块
职责：使用Android SharedPreferences保存和读取应用设置
作用：实现记忆功能，保存悬浮窗位置、大小、颜色等状态
"""

import logging
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.constants import (
    PREFS_NAME,
    PREFS_KEY_POS_X, PREFS_KEY_POS_Y,
    PREFS_KEY_WIDTH, PREFS_KEY_HEIGHT,
    PREFS_KEY_COLOR_INDEX, PREFS_KEY_OPACITY
)

logger = logging.getLogger(__name__)


def _get_shared_preferences():
    """
    获取SharedPreferences实例
    
    返回:
        SharedPreferences: 共享偏好设置对象，失败返回None
    """
    try:
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        context = PythonActivity.mActivity
        shared_prefs = context.getSharedPreferences(PREFS_NAME, 0)
        return shared_prefs
    except ImportError:
        logger.warning("非Android环境，无法访问SharedPreferences")
        return None
    except Exception as e:
        logger.error(f"获取SharedPreferences失败: {e}")
        return None


def save_position(x, y):
    """
    保存悬浮窗位置
    
    参数:
        x (int): X坐标
        y (int): Y坐标
    """
    try:
        shared_prefs = _get_shared_preferences()
        if shared_prefs is None:
            logger.warning("SharedPreferences不可用，跳过保存位置")
            return
        
        editor = shared_prefs.edit()
        editor.putInt(PREFS_KEY_POS_X, int(x))
        editor.putInt(PREFS_KEY_POS_Y, int(y))
        editor.apply()
        logger.info(f"已保存位置: ({x}, {y})")
    except Exception as e:
        logger.error(f"保存位置失败: {e}")


def load_position(default_x=0, default_y=0):
    """
    读取保存的悬浮窗位置
    
    参数:
        default_x (int): 默认X坐标
        default_y (int): 默认Y坐标
    
    返回:
        tuple: (x, y) 位置坐标
    """
    try:
        shared_prefs = _get_shared_preferences()
        if shared_prefs is None:
            return default_x, default_y
        
        x = shared_prefs.getInt(PREFS_KEY_POS_X, default_x)
        y = shared_prefs.getInt(PREFS_KEY_POS_Y, default_y)
        logger.info(f"已读取位置: ({x}, {y})")
        return x, y
    except Exception as e:
        logger.error(f"读取位置失败: {e}")
        return default_x, default_y


def save_size(width, height):
    """
    保存悬浮窗大小
    
    参数:
        width (int): 宽度
        height (int): 高度
    """
    try:
        shared_prefs = _get_shared_preferences()
        if shared_prefs is None:
            logger.warning("SharedPreferences不可用，跳过保存大小")
            return
        
        editor = shared_prefs.edit()
        editor.putInt(PREFS_KEY_WIDTH, int(width))
        editor.putInt(PREFS_KEY_HEIGHT, int(height))
        editor.apply()
        logger.info(f"已保存大小: ({width}, {height})")
    except Exception as e:
        logger.error(f"保存大小失败: {e}")


def load_size(default_width=200, default_height=120):
    """
    读取保存的悬浮窗大小
    
    参数:
        default_width (int): 默认宽度
        default_height (int): 默认高度
    
    返回:
        tuple: (width, height) 尺寸
    """
    try:
        shared_prefs = _get_shared_preferences()
        if shared_prefs is None:
            return default_width, default_height
        
        width = shared_prefs.getInt(PREFS_KEY_WIDTH, default_width)
        height = shared_prefs.getInt(PREFS_KEY_HEIGHT, default_height)
        logger.info(f"已读取大小: ({width}, {height})")
        return width, height
    except Exception as e:
        logger.error(f"读取大小失败: {e}")
        return default_width, default_height


def save_color_index(color_index):
    """
    保存颜色索引
    
    参数:
        color_index (int): 颜色索引
    """
    try:
        shared_prefs = _get_shared_preferences()
        if shared_prefs is None:
            return
        
        editor = shared_prefs.edit()
        editor.putInt(PREFS_KEY_COLOR_INDEX, color_index)
        editor.apply()
        logger.info(f"已保存颜色索引: {color_index}")
    except Exception as e:
        logger.error(f"保存颜色索引失败: {e}")


def load_color_index(default_index=0):
    """
    读取保存的颜色索引
    
    参数:
        default_index (int): 默认颜色索引
    
    返回:
        int: 颜色索引
    """
    try:
        shared_prefs = _get_shared_preferences()
        if shared_prefs is None:
            return default_index
        
        index = shared_prefs.getInt(PREFS_KEY_COLOR_INDEX, default_index)
        logger.info(f"已读取颜色索引: {index}")
        return index
    except Exception as e:
        logger.error(f"读取颜色索引失败: {e}")
        return default_index


def save_opacity(opacity):
    """
    保存透明度
    
    参数:
        opacity (float): 透明度 (0.0-1.0)
    """
    try:
        shared_prefs = _get_shared_preferences()
        if shared_prefs is None:
            return
        
        editor = shared_prefs.edit()
        editor.putFloat(PREFS_KEY_OPACITY, float(opacity))
        editor.apply()
        logger.info(f"已保存透明度: {opacity}")
    except Exception as e:
        logger.error(f"保存透明度失败: {e}")


def load_opacity(default_opacity=0.5):
    """
    读取保存的透明度
    
    参数:
        default_opacity (float): 默认透明度
    
    返回:
        float: 透明度
    """
    try:
        shared_prefs = _get_shared_preferences()
        if shared_prefs is None:
            return default_opacity
        
        opacity = shared_prefs.getFloat(PREFS_KEY_OPACITY, default_opacity)
        logger.info(f"已读取透明度: {opacity}")
        return opacity
    except Exception as e:
        logger.error(f"读取透明度失败: {e}")
        return default_opacity


def load_all():
    """
    读取所有保存的状态
    
    返回:
        dict: 包含所有状态的字典
    """
    return {
        'pos_x': load_position()[0],
        'pos_y': load_position()[1],
        'width': load_size()[0],
        'height': load_size()[1],
        'color_index': load_color_index(),
        'opacity': load_opacity(),
    }


def save_all(pos_x, pos_y, width, height, color_index, opacity):
    """
    保存所有状态
    
    参数:
        pos_x (int): X坐标
        pos_y (int): Y坐标
        width (int): 宽度
        height (int): 高度
        color_index (int): 颜色索引
        opacity (float): 透明度
    """
    save_position(pos_x, pos_y)
    save_size(width, height)
    save_color_index(color_index)
    save_opacity(opacity)
    logger.info("已保存所有状态")
