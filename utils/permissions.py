"""
权限管理模块
职责：检测和申请Android悬浮窗权限，处理权限相关逻辑
作用：确保应用能够正常显示悬浮窗，提供权限状态查询和引导功能
使用PyJNIus直接调用Android Settings API检测权限
"""

import logging

# 配置日志
logger = logging.getLogger(__name__)


def check_overlay_permission():
    """
    检测悬浮窗权限是否已授予

    通过PyJNIus调用 android.provider.Settings.canDrawOverlays() 检测

    返回:
        bool: True=已授权, False=未授权
    """
    try:
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Settings = autoclass('android.provider.Settings')
        context = PythonActivity.mActivity

        # Android 6.0+ 使用 canDrawOverlays 检测悬浮窗权限
        result = Settings.canDrawOverlays(context)
        logger.info(f"悬浮窗权限状态: {result}")
        return result
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

    SYSTEM_ALERT_WINDOW是特殊权限，不能用普通运行时权限请求，
    必须通过 Settings.ACTION_MANAGE_OVERLAY_PERMISSION 跳转设置页

    返回:
        bool: True=请求成功, False=请求失败
    """
    try:
        open_overlay_settings()
        return True
    except Exception as e:
        logger.error(f"权限请求失败: {e}")
        return False


def open_overlay_settings():
    """
    打开系统悬浮窗权限设置页面

    通过Intent跳转到 android.settings.action.MANAGE_OVERLAY_PERMISSION
    """
    try:
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        Uri = autoclass('android.net.Uri')
        Settings = autoclass('android.provider.Settings')

        context = PythonActivity.mActivity

        # 构建跳转Intent
        package_name = context.getPackageName()
        uri = Uri.parse(f"package:{package_name}")

        intent = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, uri)
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)

        # 启动设置页面
        context.startActivity(intent)
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
