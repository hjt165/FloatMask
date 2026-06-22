"""
常量定义模块
职责：定义应用中所有全局常量、颜色配置、尺寸配置、默认值
作用：避免因功能增多导致变量声明冲突，统一管理所有配置
"""

# ==================== 应用信息 ====================
APP_NAME = "FloatMask"
APP_VERSION = "0.1.0"
APP_DESCRIPTION = "智能字幕遮挡工具"

# ==================== 悬浮窗默认尺寸 ====================
# 初始尺寸（像素）
OVERLAY_DEFAULT_WIDTH = 200
OVERLAY_DEFAULT_HEIGHT = 120

# 最小尺寸限制
OVERLAY_MIN_WIDTH = 80
OVERLAY_MIN_HEIGHT = 80

# 最大尺寸比例（屏幕的30%）
OVERLAY_MAX_WIDTH_RATIO = 0.3
OVERLAY_MAX_HEIGHT_RATIO = 0.3

# 最小化模式尺寸
OVERLAY_MINIMIZED_SIZE = 30

# ==================== 边界限制 ====================
# 最小可见比例（至少20%在屏幕内）
BOUNDARY_MIN_VISIBLE_RATIO = 0.2

# ==================== 颜色配置 ====================
# RGB颜色元组 (R, G, B) 范围 0-255
COLORS = {
    'gray': (128, 128, 128),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
}

# RGBA颜色配置 (R, G, B, A) 范围 0-1
COLOR_PRESETS = [
    {'name': '半透明灰色', 'rgba': (0.5, 0.5, 0.5, 0.5)},   # 默认
    {'name': '半透明黑色', 'rgba': (0, 0, 0, 0.7)},
    {'name': '纯黑色', 'rgba': (0, 0, 0, 1.0)},
]

# 默认颜色索引
DEFAULT_COLOR_INDEX = 0

# ==================== 外观配置 ====================
# 边框配置
OVERLAY_BORDER_WIDTH = 2
OVERLAY_BORDER_COLOR = (0, 0, 0)  # 黑色边框

# 默认透明度
DEFAULT_OPACITY = 0.5

# ==================== UI主题颜色 ====================
# 应用主题色（蓝色）
THEME_PRIMARY_COLOR = '#2196F3'
# 背景色（白色）
THEME_BACKGROUND_COLOR = '#FFFFFF'
# 文字颜色
THEME_TEXT_COLOR = '#333333'
# 辅助文字颜色
THEME_SECONDARY_TEXT_COLOR = '#757575'

# ==================== 字体字号 ====================
FONT_SIZE_TITLE = 24  # sp
FONT_SIZE_BODY = 16   # sp
FONT_SIZE_CAPTION = 14  # sp
FONT_SIZE_BUTTON = 18  # sp

# ==================== 页面名称 ====================
PAGE_SPLASH = 'splash'
PAGE_MAIN = 'main'
PAGE_PERMISSION = 'permission'
PAGE_SETTINGS = 'settings'

# ==================== SharedPreferences键名 ====================
# 存储键名常量
PREFS_NAME = 'FloatMaskPrefs'
PREFS_KEY_POS_X = 'position_x'
PREFS_KEY_POS_Y = 'position_y'
PREFS_KEY_WIDTH = 'width'
PREFS_KEY_HEIGHT = 'height'
PREFS_KEY_COLOR_INDEX = 'color_index'
PREFS_KEY_OPACITY = 'opacity'

# ==================== 厂商列表 ====================
MANUFACTURERS = {
    'huawei': '华为',
    'xiaomi': '小米',
    'oppo': 'OPPO',
    'vivo': 'vivo',
    'samsung': '三星',
    'oneplus': '一加',
    'realme': 'realme',
    'meizu': '魅族',
}

# ==================== 权限相关 ====================
# 悬浮窗权限
PERMISSION_OVERLAY = 'SYSTEM_ALERT_WINDOW'
# 前台服务权限
PERMISSION_FOREGROUND_SERVICE = 'FOREGROUND_SERVICE'
