"""
权限管理模块
职责：检测和申请Android悬浮窗权限，处理权限相关逻辑
作用：确保应用能够正常显示悬浮窗，提供权限状态查询和引导功能
"""

import logging

# 配置日志
logger = logging.getLogger(__name__)


def check_overlay_permission():
    """
    检测悬浮窗权限是否已授予
    
    返回:
        bool: True=已授权, False=未授权
    """
    try:
        # 尝试导入Android模块（仅在Android环境可用）
        from android_permissions import check_permission, Permission
        return check_permission(Permission.SYSTEM_ALERT_WINDOW)
    except ImportError:
        # 非Android环境，返回True便于桌面调试
        logger.warning("非Android环境，权限检测已跳过")
        return True
    except Exception as e:
        logger.error(f"权限检测失败: {e}")
        return False


def request_overlay_permission():
    """
    请求悬浮窗权限
    
    返回:
        bool: True=请求成功, False=请求失败
    """
    try:
        from android_permissions import request_permissions, Permission
        request_permissions([Permission.SYSTEM_ALERT_WINDOW])
        logger.info("已请求悬浮窗权限")
        return True
    except ImportError:
        logger.warning("非Android环境，权限请求已跳过")
        return True
    except Exception as e:
        logger.error(f"权限请求失败: {e}")
        return False


def open_overlay_settings():
    """
    打开系统悬浮窗权限设置页面
    
    用于用户手动开启权限时调用
    """
    try:
        from android_permissions import open_settings
        open_settings('SYSTEM_ALERT_WINDOW')
        logger.info("已跳转到悬浮窗权限设置页面")
    except ImportError:
        logger.warning("非Android环境，无法打开系统设置")
    except Exception as e:
        logger.error(f"打开设置页面失败: {e}")


def get_permission_status_text():
    """
    获取权限状态的中文描述文本
    
    返回:
        str: 权限状态描述
    """
    if check_overlay_permission():
        return "已授权"
    else:
        return "未授权"


def is_permission_guide_needed():
    """
    判断是否需要显示权限引导
    
    返回:
        bool: True=需要引导, False=不需要
    """
    return not check_overlay_permission()
