[app]

# App基本信息
title = FloatMask
package.name = floatmask
package.domain = org.floatmask

# 源代码配置
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,jar,ttc,ttf
source.include_patterns = assets/*,ui/*

# 依赖配置
requirements = python3,kivy,pillow,pyjnius

# 界面配置
fullscreen = 0
orientation = portrait

# 版本配置
version = 1.0.0
version.code = 1

# Python版本
python.branch = python3

# Android权限配置
android.permissions = SYSTEM_ALERT_WINDOW,FOREGROUND_SERVICE,WAKE_LOCK

# Android API级别
android.api = 33
android.minapi = 24

# CPU架构支持（添加x86_64支持模拟器测试）
android.archs = arm64-v8a,x86_64

# Assets目录
android.asset_dir = assets

# 构建配置
android.debuggable = 0
android.release_artifact = apk
android.debug_artifact = apk
android.accept_sdk_license = True

# Android混淆配置
android.enable_proguard = False

# 后台服务配置
services = floatmask_service:./services/service_main.py

# 图标配置
# icon.filename = %(source.dir)s/assets/icons/app_icon.png

# 启动画面配置
# splash.filename = %(source.dir)s/assets/images/splash.png
# splash.orientation = portrait

# P4Abootstrap配置
p4a.bootstrap = sdl2

# 禁用presplash以加速构建
presplash.filename =

# 日志配置
log_level = 2

# 图片压缩配置
android.add_resources = True

[buildozer]
log_level = 2
warn_on_root = 1