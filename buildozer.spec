[app]

# 应用基本信息
title = FloatMask
package.name = floatmask
package.domain = org.floatmask

# 源代码配置
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,jar

# 依赖配置
requirements = python3,kivy==2.3.0,pillow,pyjnius

# 界面配置
fullscreen = 0
orientation = portrait

# Android权限配置
android.permissions = SYSTEM_ALERT_WINDOW,FOREGROUND_SERVICE,WAKE_LOCK

# Android API级别
android.api = 33
android.minapi = 24

# NDK配置
android.ndk = 25b

# CPU架构支持（只打包arm64减小体积）
android.archs = arm64-v8a

# 版本配置
version = 1.0.0
version.code = 1

# 构建配置
android.debuggable = 0
android.release_artifact = apk

# 日志配置
log_level = 2

# P4Abootstrap配置
p4a.bootstrap = python3

# 签名配置（调试用debug签名即可）
# android.release_artifact = apk
# android.signing_key = /path/to/your.keystore
# android.signing_key_password = your_password

# 禁用presplash以加速构建
presplash.filename = 

[buildozer]
warn_on_root = 0
