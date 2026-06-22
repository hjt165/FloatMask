"""
厂商兼容性处理模块
职责：检测设备厂商，提供差异化的权限引导文案和处理方案
作用：针对华为、小米、OPPO等厂商的特殊限制进行适配
"""

import logging
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.constants import MANUFACTURERS

logger = logging.getLogger(__name__)


def get_manufacturer():
    """
    获取设备厂商名称
    
    返回:
        str: 厂商名称（小写）
    """
    try:
        from jnius import autoclass
        Build = autoclass('android.os.Build')
        manufacturer = Build.MANUFACTURER.lower()
        logger.info(f"检测到设备厂商: {manufacturer}")
        return manufacturer
    except ImportError:
        # 非Android环境
        logger.warning("非Android环境，无法获取厂商信息")
        return "unknown"
    except Exception as e:
        logger.error(f"获取厂商信息失败: {e}")
        return "unknown"


def get_manufacturer_name():
    """
    获取厂商的中文名称
    
    返回:
        str: 中文厂商名称
    """
    manufacturer = get_manufacturer()
    return MANUFACTURERS.get(manufacturer, manufacturer)


def get_permission_guide_text():
    """
    根据厂商获取对应的权限引导文案
    
    返回:
        str: 权限引导说明文字
    """
    manufacturer = get_manufacturer()
    
    guides = {
        'huawei': '请在设置中开启"后台弹出界面"和"显示在其他应用上层"权限',
        'xiaomi': '请在设置中开启"显示在其他应用上层"和"后台弹出界面"权限',
        'oppo': '请在设置中开启"悬浮窗"和"后台运行"权限',
        'vivo': '请在设置中开启"显示悬窗"和"后台弹出界面"权限',
        'samsung': '请在设置中开启"显示在其他应用上层"权限',
        'oneplus': '请在设置中开启"显示在其他应用上层"和"后台运行"权限',
        'realme': '请在设置中开启"悬浮窗"和"后台运行"权限',
        'meizu': '请在设置中开启"显示悬浮窗"权限',
    }
    
    default_guide = '请在设置中开启"显示在其他应用上层"或"悬浮窗"权限'
    return guides.get(manufacturer, default_guide)


def get_permission_settings_path():
    """
    获取对应厂商的权限设置路径提示
    
    返回:
        str: 设置路径提示
    """
    manufacturer = get_manufacturer()
    
    paths = {
        'huawei': '设置 > 应用和服务 > 应用管理 > FloatMask > 权限',
        'xiaomi': '设置 > 应用设置 > 应用管理 > FloatMask > 权限管理',
        'oppo': '设置 > 应用管理 > FloatMask > 悬浮窗管理',
        'vivo': '设置 > 应用与权限 > 应用管理 > FloatMask > 权限管理',
        'samsung': '设置 > 应用 > FloatMask > 显示在其他应用上层',
        'oneplus': '设置 > 应用管理 > FloatMask > 权限管理',
        'realme': '设置 > 应用管理 > FloatMask > 悬浮窗管理',
        'meizu': '设置 > 应用管理 > FloatMask > 权限管理',
    }
    
    default_path = '设置 > 应用管理 > FloatMask > 权限'
    return paths.get(manufacturer, default_path)


def needs_foreground_service_guide():
    """
    判断厂商是否需要额外的前台服务引导
    
    返回:
        bool: True=需要引导, False=不需要
    """
    manufacturer = get_manufacturer()
    # 华为、小米、OPPO、vivo等国产厂商通常需要额外引导
    return manufacturer in ['huawei', 'xiaomi', 'oppo', 'vivo', 'oneplus', 'realme']


def get_foreground_service_guide_text():
    """
    获取前台服务引导文案
    
    返回:
        str: 前台服务引导说明
    """
    manufacturer = get_manufacturer()
    
    guides = {
        'huawei': '华为设备可能会在后台关闭应用，请在"应用启动管理"中将FloatMask设置为"手动管理"并开启所有选项',
        'xiaomi': '小米设备可能会在后台关闭应用，请在"应用管理"中将FloatMask的"省电策略"设置为"无限制"',
        'oppo': 'OPPO设备可能会在后台关闭应用，请在"电池"中将FloatMask设置为"允许后台运行"',
        'vivo': 'vivo设备可能会在后台关闭应用，请在"电池"中将FloatMask设置为"允许后台高耗电"',
    }
    
    default_guide = '为确保悬浮窗持续运行，请将FloatMask添加到后台运行白名单'
    return guides.get(manufacturer, default_guide)
