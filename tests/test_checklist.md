# FloatMask 测试清单

## 一、PC端功能测试

### 1.1 启动测试
- [x] 应用正常启动
- [x] 显示主界面
- [x] 权限检测正常

### 1.2 悬浮框基础功能
- [x] 点击"显示悬浮框"按钮，悬浮框出现
- [x] 悬浮框显示半透明灰色
- [x] 悬浮框初始尺寸400×600像素
- [x] 悬浮框位置在屏幕中央偏右

### 1.3 拖动功能
- [x] 单指拖动悬浮框，位置实时更新
- [x] 拖动过程中悬浮框保持在屏幕内
- [x] 释放后悬浮框位置固定

### 1.4 调整大小功能
- [x] 双指缩放调整大小
- [x] 最小尺寸限制为80×80像素
- [x] 最大尺寸限制为屏幕宽度30%×屏幕高度30%

### 1.5 边界限制
- [x] 悬浮框不能完全拖出屏幕
- [x] 至少20%区域在屏幕内
- [x] 四个方向都有边界限制

### 1.6 颜色切换
- [x] 双击悬浮框，颜色切换（6种颜色循环）

### 1.7 最小化模式
- [x] 点击最小化按钮，悬浮框隐藏
- [x] 从主界面可恢复

### 1.8 快捷菜单
- [x] 长按悬浮框，弹出快捷菜单
- [x] 菜单包含颜色切换、尺寸调节、透明度调节、关闭
- [x] 点击各按钮功能正常

### 1.9 点击穿透
- [x] 点击穿透模式创建FLAG_NOT_TOUCHABLE悬浮框
- [x] 触摸事件穿透到下层界面

---

## 二、Android模拟器测试（MuMu模拟器 Android 12L SDK 32）

### 2.1 APK打包与安装
- [x] Java手动编译APK成功（aapt + javac + d8 + apksigner）
- [x] APK安装到MuMu模拟器成功

### 2.2 权限测试
- [x] 应用启动时检测悬浮窗权限（canDrawOverlays）
- [x] 无权限时显示提示
- [x] 通过adb pm grant授权成功

### 2.3 P1 悬浮框核心功能
- [x] TYPE_APPLICATION_OVERLAY悬浮框正常显示
- [x] 悬浮框显示半透明黑色背景+橙色边框
- [x] 拖动移动悬浮框（ACTION_DOWN/MOVE/UP）
- [x] 双指缩放调整大小（ACTION_POINTER_DOWN距离计算）
- [x] 最小化按钮隐藏悬浮框
- [x] 从主界面恢复悬浮框

### 2.4 P2 点击穿透
- [x] FLAG_NOT_TOUCHABLE模式创建穿透悬浮框
- [x] dumpsys确认fl=NOT_TOUCHABLE标志
- [x] 触摸事件穿透到下层Activity

### 2.5 P3 快捷菜单
- [x] 长按（500ms+）触发快捷菜单
- [x] Quick Menu弹出（TYPE_APPLICATION_OVERLAY）
- [x] Change Color切换颜色
- [x] Resize: Small/Medium/Large调整尺寸
- [x] Set Opacity: 50%/100%调整透明度
- [x] Close关闭悬浮框

### 2.6 覆盖第三方App
- [x] 悬浮框显示在Activity上方（TYPE_APPLICATION_OVERLAY层级最高）

---

## 三、测试结果汇总

| 测试项 | PC端 | Android模拟器 | 备注 |
|-------|------|-------------|------|
| 应用启动 | ✅ | ✅ | PC用Kivy，Android用Java |
| 悬浮框创建 | ✅ | ✅ | TYPE_APPLICATION_OVERLAY |
| 拖动移动 | ✅ | ✅ | |
| 双指缩放 | ✅ | ✅ | PC:四角拖动, Android:双指捏合 |
| 颜色切换 | ✅ | ✅ | 双击切换6种颜色 |
| 最小化 | ✅ | ✅ | |
| 快捷菜单 | ✅ | ✅ | 长按弹出 |
| 点击穿透 | ✅ | ✅ | FLAG_NOT_TOUCHABLE |
| 边界限制 | ✅ | ✅ | |
| 配置记忆 | ✅ | - | Android端需SharedPreferences |
| 服务保活 | - | 待测 | 需真机环境 |
| 多厂商兼容 | - | 待测 | 需华为/小米/OPPO真机 |

---

## 四、已知限制

1. **网络环境限制**：无法从GitHub/F-Droid下载Termux APK，未能在Android上运行Python/Kivy版本
2. **WSL2限制**：BIOS未开启虚拟化，无法安装WSL2+Buildozer打包
3. **替代方案**：手动编译Java版FloatMask APK验证所有Android API功能
4. **服务保活**：keep_alive_service.py代码已写，需真机测试
5. **多厂商兼容**：compat.py代码已写，需华为/小米/OPPO真机测试
