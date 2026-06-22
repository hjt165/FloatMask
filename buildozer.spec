[app]

# App基本信息
title = FloatMask
package.name = floatmask
package.domain = org.floatmask

source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.include_patterns = assets/*,ui/*

version = 0.1.0

# Python版本
python.branch = python3

# 依赖包
requirements = python3,kivy,pyjnius,android

# Android权限配置
android.permissions = SYSTEM_ALERT_WINDOW,FOREGROUND_SERVICE

# Android API级别
android.api = 34
android.minapi = 24
android.ndk = 25

# Android打包配置
android.release_artifact = apk
android.debug_artifact = apk

# Android混淆配置
android.enable_proguard = False

# Android签名配置
# android.release = True
# android.debuggable = False

# Android工具链
android.allow_backup = True

# 后台服务配置
services = floatmask_service:./services/service_main.py

# 图标配置
# icon.filename = %(source.dir)s/assets/icons/app_icon.png

# 启动画面配置
# splash.filename = %(source.dir)s/assets/images/splash.png
# splash.orientation = portrait

# 项目配置
fullscreen = 0
orientation = portrait

# 日志配置
log_level = 2

# 图片压缩配置
android.add_resources = True

[buildozer]
log_level = 2
warn_on_root = 1
