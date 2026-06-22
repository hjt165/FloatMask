[app]

<<<<<<< HEAD
# App基本信息
=======
# 应用基本信息
>>>>>>> 29e54356d094ee786c5a700356f6211bd74ff6bc
title = FloatMask
package.name = floatmask
package.domain = org.floatmask

<<<<<<< HEAD
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
=======
# 源代码配置
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,jar,ttc,ttf

# 依赖配置
requirements = python3,kivy,pillow,pyjnius

# 界面配置
fullscreen = 0
orientation = portrait

# Android权限配置
android.permissions = SYSTEM_ALERT_WINDOW,FOREGROUND_SERVICE,WAKE_LOCK

# Android API级别
android.api = 33
android.minapi = 24

# NDK配置（由p4a自动选择推荐版本）
# android.ndk = 27c

# CPU架构支持（添加x86_64支持模拟器测试）
android.archs = arm64-v8a,x86_64

# Assets目录（包含libs/overlay-touch-handler.jar等）
android.asset_dir = assets

# 版本配置
version = 1.0.0
version.code = 1

# 构建配置
android.debuggable = 0
android.release_artifact = apk
android.accept_sdk_license = True

# 日志配置
log_level = 2

# P4Abootstrap配置
p4a.bootstrap = sdl2

# 签名配置（调试用debug签名即可）
# android.release_artifact = apk
# android.signing_key = /path/to/your.keystore
# android.signing_key_password = your_password

# 禁用presplash以加速构建
presplash.filename = 

[buildozer]
warn_on_root = 0
>>>>>>> 29e54356d094ee786c5a700356f6211bd74ff6bc
