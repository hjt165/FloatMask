# FloatMask - 智能字幕遮挡工具

## 项目概述

创建一个名为 **FloatMask（智能字幕遮挡工具）** 的 **Android App（基于Python开发）** 应用，这个应用的核心是解决 **外语学习者** 在 **观看外语视频时过度依赖字幕、导致听力能力无法提升** 方面的问题。

用户在使用B站、抖音、腾讯视频等App观看外语视频时，虽然能借助字幕理解内容，但长期依赖会阻碍听力训练。FloatMask 提供一个可自由拖动、可调整大小的悬浮遮挡框，覆盖在字幕区域上方，帮助用户脱离文字辅助进行听力理解。

---

## 技术架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FloatMask 技术架构                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                        用户交互层 (UI Layer)                        │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │  │
│  │  │ 启动页    │  │   主页   │  │ 设置页   │  │ 权限引导页        │  │  │
│  │  │ Splash   │→→│   Main   │→→│ Settings │←→│ Permission Guide │  │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                    ↓                                    │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                       业务逻辑层 (Core Layer)                       │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐│  │
│  │  │ OverlayManager│  │TouchHandler  │  │     BoundaryChecker      ││  │
│  │  │ 悬浮窗管理器   │  │ 触摸处理器   │  │      边界检测器          ││  │
│  │  └──────────────┘  └──────────────┘  └──────────────────────────┘│  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                    ↓                                    │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                       系统服务层 (Service Layer)                    │  │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐  │  │
│  │  │ ForegroundService│  │  PermissionManager│  │ StorageManager │  │  │
│  │  │   前台服务        │  │    权限管理器      │  │  存储管理器     │  │  │
│  │  └──────────────────┘  └──────────────────┘  └────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                    ↓                                    │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                      Android 系统层 (Android Layer)                 │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │  │
│  │  │ WindowManager│  │   Context   │  │  Settings   │               │  │
│  │  │  窗口管理器   │  │   上下文    │  │   系统设置   │               │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘               │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                       技术栈 (Tech Stack)                          │  │
│  │  Python 3.10+ │ Kivy 2.3.0 │ PyJNIus 1.5+ │ Buildozer 1.6.1     │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 页面设计

### 页面流程图

```
┌─────────────┐
│   启动页     │
│   Splash    │
└──────┬──────┘
       │ (2秒后自动跳转)
       ↓
┌─────────────┐     未授权     ┌─────────────────┐
│    主页     │←←←←←←←←←←←←←│  权限引导页       │
│    Main     │←←←←←←←←←←←←←│ Permission Guide │
└──────┬──────┘              └─────────────────┘
       │ 已授权                   │ (点击去设置)
       ↓                         ↓
┌─────────────┐              ┌─────────────┐
│  悬浮窗激活   │              │  系统设置页   │
│  Overlay    │              │   Settings   │
└─────────────┘              └──────┬──────┘
                                    │ (开启权限后返回)
                                    ↓
                              ┌─────────────┐
                              │    主页     │
                              │    Main     │
                              └─────────────┘

┌─────────────┐
│   设置页     │
│  Settings   │
└─────────────┘
```

---

### 页面1：启动页（Splash Screen）

**页面用途：** 应用启动时的欢迎页面，同时进行权限检测和初始化工作

**页面布局：**
```
┌─────────────────────────────┐
│                             │
│                             │
│         ┌─────────┐         │
│         │  Logo   │         │
│         │  128x128 │        │
│         └─────────┘         │
│                             │
│      FloatMask              │
│    智能字幕遮挡工具          │
│                             │
│      ┌─────────────┐        │
│      │   ● ● ●     │        │  ← 加载指示器
│      │  正在检测权限 │        │
│      └─────────────┘        │
│                             │
│         v0.1.0              │
│                             │
└─────────────────────────────┘
```

**页面元素：**

| 元素 | 类型 | 位置 | 尺寸 | 说明 |
|------|------|------|------|------|
| Logo | Image | 居中上方 | 128×128px | 应用图标 |
| 应用名称 | Label | Logo下方 | 24sp | "FloatMask" |
| 副标题 | Label | 名称下方 | 16sp | "智能字幕遮挡工具" |
| 加载指示器 | ActivityIndicator | 中下方 | 48×48px | 旋转加载动画 |
| 状态文字 | Label | 指示器下方 | 14sp | 显示当前状态 |
| 版本号 | Label | 底部居中 | 12sp | "v0.1.0" |

**页面逻辑：**
```python
class SplashScreen(Screen):
    def on_enter(self):
        """进入页面时执行"""
        # 1. 显示加载动画
        self.ids.loading.active = True
        
        # 2. 检测悬浮窗权限
        has_permission = check_overlay_permission()
        
        # 3. 2秒后跳转
        Clock.schedule_once(self.transition_next, 2.0)
    
    def transition_next(self, dt):
        """跳转到下一个页面"""
        if has_permission:
            self.manager.current = 'main'  # 直接进入主页
        else:
            self.manager.current = 'permission'  # 进入权限引导页
```

---

### 页面2：主页（Main Screen）

**页面用途：** 应用的主控制页面，显示悬浮窗状态并提供操作按钮

**页面布局：**
```
┌─────────────────────────────┐
│  FloatMask              ⚙️  │  ← 标题栏 + 设置按钮
├─────────────────────────────┤
│                             │
│     ┌───────────────────┐   │
│     │                   │   │
│     │   ┌─────────┐     │   │
│     │   │  状态   │     │   │
│     │   │ 图标    │     │   │  ← 状态显示区域
│     │   └─────────┘     │   │
│     │   悬浮窗已激活     │   │
│     │   正在遮挡字幕     │   │
│     │                   │   │
│     └───────────────────┘   │
│                             │
│  ┌───────────────────────┐  │
│  │      启动悬浮窗        │  │  ← 主操作按钮
│  └───────────────────────┘  │
│                             │
│  ┌───────────────────────┐  │
│  │      检测权限         │  │  ← 权限检测按钮
│  └───────────────────────┘  │
│                             │
│  ┌───────────────────────┐  │
│  │      使用说明         │  │  ← 帮助按钮
│  └───────────────────────┘  │
│                             │
├─────────────────────────────┤
│      Made with Python       │  ← 底部信息
└─────────────────────────────┘
```

**页面元素：**

| 元素 | 类型 | 位置 | 说明 |
|------|------|------|------|
| 标题 | Label | 顶部居中 | "FloatMask" |
| 设置按钮 | IconButton | 右上角 | 跳转到设置页 |
| 状态卡片 | BoxLayout | 上部 | 显示当前状态 |
| 状态图标 | Image | 卡片内 | 绿色=已激活，灰色=未激活 |
| 状态文字 | Label | 卡片内 | "悬浮窗已激活" / "悬浮窗未激活" |
| 启动按钮 | Button | 中部 | 点击启动/停止悬浮窗 |
| 权限按钮 | Button | 中下部 | 点击检测/申请权限 |
| 帮助按钮 | Button | 下部 | 点击显示使用说明 |
| 底部信息 | Label | 底部 | "Made with Python" |

**页面逻辑：**
```python
class MainScreen(Screen):
    def on_enter(self):
        """进入页面时刷新状态"""
        self.update_status()
    
    def update_status(self):
        """更新悬浮窗状态显示"""
        is_active = overlay_manager.is_active()
        if is_active:
            self.ids.status_icon.source = 'assets/icons/active.png'
            self.ids.status_text.text = '悬浮窗已激活'
            self.ids.toggle_button.text = '停止悬浮窗'
        else:
            self.ids.status_icon.source = 'assets/icons/inactive.png'
            self.ids.status_text.text = '悬浮窗未激活'
            self.ids.toggle_button.text = '启动悬浮窗'
    
    def toggle_overlay(self):
        """切换悬浮窗状态"""
        if overlay_manager.is_active():
            overlay_manager.stop()
        else:
            if check_overlay_permission():
                overlay_manager.start()
            else:
                self.manager.current = 'permission'
        self.update_status()
```

---

### 页面3：权限引导页（Permission Guide Screen）

**页面用途：** 当用户未授权悬浮窗权限时，引导用户前往系统设置开启

**页面布局：**
```
┌─────────────────────────────┐
│                             │
│                             │
│         ┌─────────┐         │
│         │  图标   │         │
│         │  🔒     │         │
│         └─────────┘         │
│                             │
│    需要悬浮窗权限            │
│                             │
│  为了能够在其他应用上方显示  │
│  悬浮遮挡框，需要您授权     │
│  "显示在其他应用上层"权限   │
│                             │
│  ┌───────────────────────┐  │
│  │    ⚙️ 前往系统设置     │  │  ← 跳转按钮
│  └───────────────────────┘  │
│                             │
│  ┌───────────────────────┐  │
│  │      返回App          │  │  ← 返回按钮
│  └───────────────────────┘  │
│                             │
│    💡 提示：授权后即可使用  │
│                             │
└─────────────────────────────┘
```

**页面元素：**

| 元素 | 类型 | 位置 | 说明 |
|------|------|------|------|
| 图标 | Image | 居中上方 | 锁形图标 |
| 标题 | Label | 图标下方 | "需要悬浮窗权限" |
| 说明文字 | Label | 标题下方 | 解释为什么需要权限 |
| 跳转按钮 | Button | 中部 | "前往系统设置" |
| 返回按钮 | Button | 跳转按钮下方 | "返回App" |
| 提示文字 | Label | 底部 | "提示：授权后即可使用" |

**页面逻辑：**
```python
class PermissionScreen(Screen):
    def open_settings(self):
        """跳转到系统悬浮窗权限设置页"""
        from android.permissions import open_settings
        open_settings('SYSTEM_ALERT_WINDOW')
    
    def go_back(self):
        """返回主页"""
        self.manager.current = 'main'
    
    def on_enter(self):
        """进入页面时检测权限状态"""
        # 如果已授权，直接跳转主页
        if check_overlay_permission():
            self.manager.current = 'main'
```

---

### 页面4：设置页（Settings Screen）

**页面用途：** 应用的配置页面，用户可以调整悬浮窗的默认参数

**页面布局：**
```
┌─────────────────────────────┐
│  ← 返回        设置         │  ← 标题栏
├─────────────────────────────┤
│                             │
│  ┌───────────────────────┐  │
│  │  外观设置             │  │  ← 分组标题
│  ├───────────────────────┤  │
│  │  默认颜色     [▼ 灰]  │  │  ← 颜色选择
│  │  默认透明度   [====]  │  │  ← 滑动条
│  │  边框宽度     [2px]   │  │  ← 数值选择
│  └───────────────────────┘  │
│                             │
│  ┌───────────────────────┐  │
│  │  行为设置             │  │  ← 分组标题
│  ├───────────────────────┤  │
│  │  记忆位置     [  ✓]   │  │  ← 开关按钮
│  │  记忆大小     [  ✓]   │  │  ← 开关按钮
│  │  记忆颜色     [  ✓]   │  │  ← 开关按钮
│  └───────────────────────┘  │
│                             │
│  ┌───────────────────────┐  │
│  │  系统信息             │  │  ← 分组标题
│  ├───────────────────────┤  │
│  │  设备厂商     华为    │  │  ← 只读信息
│  │  Android版本  12      │  │  ← 只读信息
│  │  权限状态     已授权  │  │  ← 只读信息
│  └───────────────────────┘  │
│                             │
│  ┌───────────────────────┐  │
│  │      恢复默认设置      │  │  ← 重置按钮
│  └───────────────────────┘  │
│                             │
└─────────────────────────────┘
```

**页面元素：**

| 元素 | 类型 | 位置 | 说明 |
|------|------|------|------|
| 返回按钮 | Button | 左上角 | 返回主页 |
| 标题 | Label | 顶部居中 | "设置" |
| 外观设置分组 | Label | 上部 | 分组标题 |
| 默认颜色选择 | Spinner | 外观设置内 | 可选：灰/黑/纯黑 |
| 默认透明度 | Slider | 外观设置内 | 0%-100% |
| 边框宽度 | Spinner | 外观设置内 | 可选：1px/2px/3px/4px |
| 行为设置分组 | Label | 中部 | 分组标题 |
| 记忆位置开关 | Switch | 行为设置内 | 开/关 |
| 记忆大小开关 | Switch | 行为设置内 | 开/关 |
| 记忆颜色开关 | Switch | 行为设置内 | 开/关 |
| 系统信息分组 | Label | 下部 | 分组标题 |
| 设备厂商 | Label | 系统信息内 | 只读 |
| Android版本 | Label | 系统信息内 | 只读 |
| 权限状态 | Label | 系统信息内 | 只读 |
| 恢复默认按钮 | Button | 底部 | 重置所有设置 |

**页面逻辑：**
```python
class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_settings()
    
    def load_settings(self):
        """加载保存的设置"""
        settings = StorageManager.load_settings()
        self.ids.color_spinner.text = settings.get('default_color', '灰色')
        self.ids.opacity_slider.value = settings.get('default_opacity', 50)
        self.ids.border_spinner.text = settings.get('border_width', '2px')
        self.ids.remember_pos.active = settings.get('remember_position', True)
        self.ids.remember_size.active = settings.get('remember_size', True)
        self.ids.remember_color.active = settings.get('remember_color', True)
    
    def save_settings(self):
        """保存设置"""
        settings = {
            'default_color': self.ids.color_spinner.text,
            'default_opacity': self.ids.opacity_slider.value,
            'border_width': self.ids.border_spinner.text,
            'remember_position': self.ids.remember_pos.active,
            'remember_size': self.ids.remember_size.active,
            'remember_color': self.ids.remember_color.active,
        }
        StorageManager.save_settings(settings)
    
    def reset_settings(self):
        """恢复默认设置"""
        StorageManager.reset_settings()
        self.load_settings()
```

---

## 目录结构

### 完整目录树

```
floatmask/                          # 项目根目录
│
├── main.py                         # 【主入口】应用启动入口，初始化Kivy App
│                                   #   作用：创建App实例，运行主循环
│
├── buildozer.spec                  # 【打包配置】Buildozer打包配置文件
│                                   #   作用：定义Android打包参数、权限、依赖
│
├── requirements.txt                # 【依赖清单】Python依赖包列表
│                                   #   作用：pip install -r requirements.txt
│
├── README.MD                       # 【项目文档】项目说明文档
│                                   #   作用：记录项目设计、功能、技术方案
│
│
├── core/                           # 【核心模块】核心业务逻辑
│   │
│   ├── __init__.py                 # 包初始化文件
│   │
│   ├── overlay_manager.py          # 【悬浮窗管理器】管理悬浮窗的生命周期
│   │                               #   类：OverlayManager
│   │                               #   方法：
│   │                               #     - start()    : 启动悬浮窗
│   │                               #     - stop()     : 停止悬浮窗
│   │                               #     - is_active(): 检查是否激活
│   │                               #     - update_position(): 更新位置
│   │                               #     - update_size(): 更新尺寸
│   │                               #     - update_color(): 更新颜色
│   │
│   ├── touch_handler.py            # 【触摸处理器】处理所有触摸交互事件
│   │                               #   类：TouchHandler
│   │                               #   功能：
│   │                               #     - 拖动移动：单指拖动改变位置
│   │                               #     - 尺寸调整：拖动边缘/四角调整大小
│   │                               #     - 双击切换：双击切换颜色
│   │                               #     - 长按菜单：长按弹出快捷菜单
│   │                               #     - 点击穿透：不影响下方App
│   │
│   └── boundary.py                 # 【边界检测器】检测悬浮窗边界限制
│                                   #   类：BoundaryChecker
│                                   #   功能：
│                                   #     - check_boundary(): 检测是否超出边界
│                                   #     - ensure_visible(): 确保至少20%可见
│                                   #     - get_visible_ratio(): 计算可见比例
│
│
├── services/                       # 【服务模块】Android后台服务
│   │
│   ├── __init__.py                 # 包初始化文件
│   │
│   ├── foreground_service.py       # 【前台服务】保持应用在后台运行
│   │                               #   类：ForegroundService
│   │                               #   功能：
│   │                               #     - 创建通知渠道（Android 8.0+）
│   │                               #     - 显示前台服务通知
│   │                               #     - 防止系统杀死服务
│   │
│   └── service_main.py             # 【服务入口】后台服务的主脚本
│                                   #   作用：Buildozer打包时指定的后台服务入口
│                                   #   运行方式：独立于主App的Python进程
│
│
├── ui/                             # 【界面模块】Kivy UI定义文件
│   │
│   ├── __init__.py                 # 包初始化文件
│   │
│   ├── splash.kv                   # 【启动页样式】启动页的KV布局定义
│   │                               #   定义：Logo、标题、加载动画的位置和样式
│   │
│   ├── main.kv                     # 【主页样式】主页的KV布局定义
│   │                               #   定义：状态卡片、操作按钮的布局
│   │
│   ├── permission_guide.kv         # 【权限引导页样式】权限页的KV布局定义
│   │                               #   定义：图标、说明文字、按钮的布局
│   │
│   ├── settings.kv                 # 【设置页样式】设置页的KV布局定义
│   │                               #   定义：分组、开关、滑动条的布局
│   │
│   └── overlay.kv                  # 【悬浮窗样式】悬浮窗的KV布局定义
│                                   #   定义：悬浮框外观、颜色、边框
│
│
├── screens/                        # 【页面模块】页面逻辑代码
│   │
│   ├── __init__.py                 # 包初始化文件
│   │
│   ├── splash_screen.py            # 【启动页逻辑】启动页的业务逻辑
│   │                               #   类：SplashScreen(Screen)
│   │                               #   功能：权限检测、页面跳转
│   │
│   ├── main_screen.py              # 【主页逻辑】主页的业务逻辑
│   │                               #   类：MainScreen(Screen)
│   │                               #   功能：状态显示、启动/停止悬浮窗
│   │
│   ├── permission_screen.py        # 【权限引导页逻辑】权限页的业务逻辑
│   │                               #   类：PermissionScreen(Screen)
│   │                               #   功能：权限申请、跳转系统设置
│   │
│   └── settings_screen.py          # 【设置页逻辑】设置页的业务逻辑
│                                   #   类：SettingsScreen(Screen)
│                                   #   功能：配置读写、恢复默认
│
│
├── utils/                          # 【工具模块】通用工具函数
│   │
│   ├── __init__.py                 # 包初始化文件
│   │
│   ├── permissions.py              # 【权限工具】权限检测与申请
│   │                               #   函数：
│   │                               #     - check_overlay_permission(): 检测悬浮窗权限
│   │                               #     - request_overlay_permission(): 申请权限
│   │                               #     - open_settings(): 跳转系统设置
│   │
│   ├── storage.py                  # 【存储工具】本地数据存储
│   │                               #   类：StorageManager
│   │                               #   功能：
│   │                               #     - save_position(): 保存悬浮窗位置
│   │                               #     - load_position(): 读取悬浮窗位置
│   │                               #     - save_settings(): 保存应用设置
│   │                               #     - load_settings(): 读取应用设置
│   │
│   ├── compat.py                   # 【兼容工具】厂商兼容处理
│   │                               #   函数：
│   │                               #     - get_manufacturer(): 获取设备厂商
│   │                               #     - get_permission_guide(): 获取权限引导文案
│   │                               #     - handle_special_permission(): 处理特殊权限
│   │
│   └── constants.py                # 【常量定义】全局常量配置
│                                   #   内容：
│                                   #     - COLORS: 颜色配置
│                                   #     - SIZES: 尺寸配置
│                                   #     - DEFAULTS: 默认值
│                                   #     - MANUFACTURERS: 厂商列表
│
│
└── assets/                         # 【资源模块】静态资源文件
    │
    ├── icons/                      # 图标资源
    │   ├── app_icon.png            # 应用图标（512×512）
    │   ├── active.png              # 状态图标-已激活（绿色）
    │   ├── inactive.png            # 状态图标-未激活（灰色）
    │   ├── settings.png            # 设置图标
    │   ├── permission.png          # 权限图标
    │   └── close.png               # 关闭图标
    │
    ├── images/                     # 图片资源
    │   ├── logo.png                # 应用Logo
    │   └── splash_bg.png           # 启动页背景图
    │
    └── fonts/                      # 字体资源
        └── default.ttf             # 默认字体
```

---

## 技术框架

### 技术栈详解

| 层级 | 技术 | 版本 | 用途 |
|------|------|------|------|
| **开发语言** | Python | 3.10+ | 主要开发语言 |
| **UI框架** | Kivy | 2.3.0 | 跨平台UI框架 |
| **Android桥接** | PyJNIus | 1.5.0+ | 调用Java/Android API |
| **打包工具** | Buildozer | 1.6.1 | 打包成Android APK |
| **权限管理** | python-for-android | - | Android权限处理 |

### Kivy 框架结构

```
┌─────────────────────────────────────────────────────────────┐
│                    Kivy 应用架构                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │    App      │    │   Screen    │    │   Widget    │    │
│  │  应用主类    │───→│   Manager   │───→│   组件      │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
│         │                   │                   │          │
│         ↓                   ↓                   ↓          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │   .kv       │    │   Screen    │    │   Canvas    │    │
│  │  样式文件    │    │   页面类     │    │   绘图      │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### PyJNIus 调用流程

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Python    │ ───→ │   PyJNIus   │ ───→ │   Android   │
│   代码      │      │   桥接层    │      │   Java API  │
└─────────────┘      └─────────────┘      └─────────────┘
       │                    │                    │
       ↓                    ↓                    ↓
  autoclass()         JNI接口调用         WindowManager
  创建Java类实例      调用Java方法        Context
                                         Settings
```

**示例代码：**
```python
from jnius import autoclass

# 获取Android类
Context = autoclass('android.content.Context')
WindowManager = autoclass('android.view.WindowManager')
PythonActivity = autoclass('org.kivy.android.PythonActivity')

# 获取系统服务
context = PythonActivity.mActivity
window_manager = context.getSystemService(Context.WINDOW_SERVICE)

# 创建悬浮窗参数
params = WindowManager.LayoutParams(
    WindowManager.LayoutParams.WRAP_CONTENT,
    WindowManager.LayoutParams.WRAP_CONTENT,
    WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
    WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
    android.view.PixelFormat.TRANSLUCENT
)
```

---

## 功能设计

### 核心功能（必做）

#### 功能1：权限管理模块

| 功能点 | 描述 | 业务逻辑 |
|--------|------|----------|
| 权限检测 | App启动时检测是否已获得悬浮窗权限 | 调用 `Settings.canDrawOverlays()` 检测 |
| 权限引导 | 未授权时弹出提示框，引导用户跳转设置页 | 显示说明文字 + "去设置"按钮 |
| 权限回调 | 用户授权后自动返回App并启动悬浮窗 | 监听 `onResume` 事件重新检测 |

**用户流程：**
```
启动App → 检测权限 → 已授权：直接显示悬浮窗
                     → 未授权：弹出提示 → 跳转系统设置 → 用户开启 → 返回App → 显示悬浮窗
```

---

#### 功能2：悬浮框显示模块

| 功能点 | 描述 | 参数 |
|--------|------|------|
| 外观样式 | 半透明带边框的矩形方框 | 边框2px，颜色可配置 |
| 初始尺寸 | 200×120 像素 | 宽200px，高120px |
| 初始位置 | 屏幕中央偏右 | x=屏幕宽度×0.6, y=屏幕高度×0.4 |
| 半透明效果 | 默认50%透明度 | RGBA(128, 128, 128, 0.5) |

**外观参数：**
```python
# 默认外观配置
OVERLAY_DEFAULT_WIDTH = 200       # 初始宽度（像素）
OVERLAY_DEFAULT_HEIGHT = 120      # 初始高度（像素）
OVERLAY_DEFAULT_OPACITY = 0.5     # 默认透明度（0-1）
OVERLAY_BORDER_WIDTH = 2          # 边框宽度（像素）
OVERLAY_BORDER_COLOR = (0, 0, 0)  # 边框颜色（RGB）
OVERLAY_FILL_COLOR = (128, 128, 128)  # 填充颜色（RGB）
```

---

#### 功能3：交互功能模块

| 功能点 | 描述 | 边界条件 |
|--------|------|----------|
| 拖动移动 | 单指长按悬浮框拖动，实时更新位置 | 位置变化范围：x∈[0, 屏幕宽度], y∈[0, 屏幕高度] |
| 尺寸调整 | 拖动四角或边缘调整大小 | 最小80×80px，最大屏幕30%×30% |
| 边界限制 | 悬浮框不能完全拖出屏幕 | 至少保留20%面积在可视区域内 |

**尺寸计算逻辑：**
```python
# 最小尺寸限制
MIN_WIDTH = 80
MIN_HEIGHT = 80

# 最大尺寸限制（屏幕的30%）
MAX_WIDTH_RATIO = 0.3
MAX_HEIGHT_RATIO = 0.3

def get_max_size(screen_width, screen_height):
    return (screen_width * MAX_WIDTH_RATIO, 
            screen_height * MAX_HEIGHT_RATIO)
```

**边界检测逻辑：**
```python
def check_boundary(pos_x, pos_y, width, height, screen_width, screen_height):
    """
    检测悬浮窗是否在边界内
    
    返回: True=在边界内, False=超出边界
    """
    # 计算悬浮窗四个角的坐标
    left = pos_x
    right = pos_x + width
    top = pos_y
    bottom = pos_y + height
    
    # 计算可见区域
    visible_left = max(0, left)
    visible_right = min(screen_width, right)
    visible_top = max(0, top)
    visible_bottom = min(screen_height, bottom)
    
    # 计算可见面积比例
    visible_area = (visible_right - visible_left) * (visible_bottom - visible_top)
    total_area = width * height
    visible_ratio = visible_area / total_area
    
    # 至少20%可见
    return visible_ratio >= 0.2
```

---

#### 功能4：视频遮挡模块

| 功能点 | 描述 |
|--------|------|
| 覆盖能力 | 使用Android SYSTEM_ALERT_WINDOW权限，悬浮框显示在所有App上方 |
| 遮挡效果 | 悬浮框可覆盖在B站、抖音、腾讯视频、本地播放器等任何视频App的字幕区域 |
| 点击穿透 | 设置FLAG_NOT_FOCUSABLE，点击悬浮框区域不拦截触摸事件，下方App正常响应 |

**点击穿透实现：**
```python
from jnius import autoclass

# 获取WindowManager.LayoutParams类
LayoutParams = autoclass('android.view.WindowManager$LayoutParams')

# 创建悬浮窗参数
params = LayoutParams(
    LayoutParams.WRAP_CONTENT,
    LayoutParams.WRAP_CONTENT,
    LayoutParams.TYPE_APPLICATION_OVERLAY,
    # 关键标志：点击穿透
    LayoutParams.FLAG_NOT_FOCUSABLE | LayoutParams.FLAG_NOT_TOUCH_MODAL,
    android.view.PixelFormat.TRANSLUCENT
)
```

---

#### 功能5：退出清理模块

| 功能点 | 描述 |
|--------|------|
| 悬浮窗移除 | App退出时调用 `WindowManager.removeView()` |
| 服务停止 | 停止前台服务，释放后台资源 |
| 进程清理 | 确保无残留后台进程 |

**清理流程：**
```python
def cleanup():
    """应用退出时清理资源"""
    # 1. 移除悬浮窗
    if overlay_view is not None:
        window_manager.removeView(overlay_view)
    
    # 2. 停止前台服务
    foreground_service.stop()
    
    # 3. 保存状态（可选）
    if settings.get('remember_position'):
        save_position()
```

---

### 拓展功能（选做加分）

#### 功能6：颜色切换功能

| 触发方式 | 切换逻辑 |
|----------|----------|
| 双击悬浮框 | 循环切换：半透明灰 → 半透明黑 → 纯黑 → 半透明灰 |

**颜色方案：**
```python
# 颜色预设
COLOR_PRESETS = [
    {'name': '半透明灰色', 'rgba': (0.5, 0.5, 0.5, 0.5)},   # 默认
    {'name': '半透明黑色', 'rgba': (0, 0, 0, 0.7)},
    {'name': '纯黑色',    'rgba': (0, 0, 0, 1.0)},
]

def switch_color(current_index):
    """切换到下一个颜色"""
    next_index = (current_index + 1) % len(COLOR_PRESETS)
    return COLOR_PRESETS[next_index]
```

---

#### 功能7：快捷菜单功能

| 触发方式 | 菜单内容 |
|----------|----------|
| 长按悬浮框 | 弹出快捷菜单 |

**菜单选项：**
- 透明度调节：滑动条控制0%-100%
- 颜色选择：快捷选择预设颜色
- 最小化：缩成小圆点
- 关闭：移除悬浮窗

**菜单布局：**
```
┌─────────────────┐
│  透明度 [====]  │
├─────────────────┤
│  ● 灰色         │
│  ● 黑色         │
│  ● 纯黑         │
├─────────────────┤
│  ⬜ 最小化      │
│  ✕ 关闭         │
└─────────────────┘
```

---

#### 功能8：记忆功能

| 功能点 | 描述 |
|--------|------|
| 保存时机 | 悬浮框位置/大小变化时自动保存 |
| 读取时机 | App启动时读取上次保存的状态 |
| 存储方式 | Android SharedPreferences via PyJNIus |

**保存数据结构：**
```json
{
  "position_x": 540,
  "position_y": 800,
  "width": 200,
  "height": 120,
  "color_index": 0,
  "opacity": 0.5
}
```

**存储实现：**
```python
from jnius import autoclass

# 获取SharedPreferences
PythonActivity = autoclass('org.kivy.android.PythonActivity')
context = PythonActivity.mActivity
shared_prefs = context.getSharedPreferences('FloatMaskPrefs', 0)

# 保存数据
editor = shared_prefs.edit()
editor.putInt('position_x', 540)
editor.putInt('position_y', 800)
editor.putInt('width', 200)
editor.putInt('height', 120)
editor.putInt('color_index', 0)
editor.putFloat('opacity', 0.5)
editor.apply()

# 读取数据
pos_x = shared_prefs.getInt('position_x', 0)  # 0是默认值
```

---

#### 功能9：最小化模式

| 状态 | 显示 | 交互 |
|------|------|------|
| 正常模式 | 完整矩形悬浮框 | 可拖动、调整大小 |
| 最小化模式 | 小圆点（直径30px） | 点击恢复正常模式 |

**模式切换：**
```python
class OverlayManager:
    def __init__(self):
        self.is_minimized = False
        self.normal_size = (200, 120)
        self.minimized_size = (30, 30)
    
    def toggle_minimize(self):
        """切换最小化模式"""
        if self.is_minimized:
            # 恢复正常模式
            self.set_size(*self.normal_size)
        else:
            # 最小化
            self.set_size(*self.minimized_size)
        self.is_minimized = not self.is_minimized
```

---

### 异常处理

#### 1. 权限异常处理

| 场景 | 处理方式 |
|------|----------|
| 用户拒绝权限 | 显示说明文字，解释为什么需要此权限 |
| 用户永久拒绝 | 引导跳转系统设置页手动开启 |
| 权限被撤销 | 检测到权限丢失时自动提示重新授权 |

---

#### 2. 服务保活处理

| 场景 | 处理方式 |
|------|----------|
| 系统内存不足 | 使用Foreground Service，显示常驻通知 |
| App被杀死 | 通过通知栏点击重启服务 |
| 屏幕关闭 | 服务保持运行，不影响遮挡功能 |

**前台服务通知：**
```
标题：FloatMask 运行中
内容：悬浮窗已激活，点击打开设置
图标：应用小图标
```

---

#### 3. 厂商兼容处理

| 厂商 | 特殊处理 |
|------|----------|
| 华为 | 引导开启"后台弹出界面"权限 |
| 小米 | 引导开启"显示在其他应用上层"权限 |
| OPPO | 引导开启"悬浮窗"和"后台运行"权限 |
| vivo | 引导开启"显示悬窗"和"后台弹出界面"权限 |
| 三星 | 标准Android权限流程即可 |

**兼容检测逻辑：**
```python
from jnius import autoclass

Build = autoclass('android.os.Build')

def get_manufacturer():
    """获取设备厂商"""
    return Build.MANUFACTURER.lower()

def get_permission_guide():
    """根据厂商获取权限引导文案"""
    manufacturer = get_manufacturer()
    
    guides = {
        'huawei': '请开启"后台弹出界面"权限',
        'xiaomi': '请开启"显示在其他应用上层"权限',
        'oppo': '请开启"悬浮窗"和"后台运行"权限',
        'vivo': '请开启"显示悬窗"和"后台弹出界面"权限',
        'samsung': '请开启"显示在其他应用上层"权限',
    }
    
    return guides.get(manufacturer, '请开启悬浮窗权限')
```

---

## 开发方案

### 功能优先级

#### P0 - 核心必做（必须完成）

| 优先级 | 功能 | 说明 | 预计时间 |
|--------|------|------|----------|
| P0-1 | 权限管理 | 悬浮窗权限检测与申请 | 0.5天 |
| P0-2 | 悬浮窗显示 | 半透明悬浮框显示 | 0.5天 |
| P0-3 | 拖动移动 | 单指拖动改变位置 | 1天 |
| P0-4 | 边界限制 | 确保20%在屏幕内 | 0.5天 |
| P0-5 | 点击穿透 | 不影响下方App操作 | 0.5天 |

**P0总计：3天**

---

#### P1 - 重要功能（尽量完成）

| 优先级 | 功能 | 说明 | 预计时间 |
|--------|------|------|----------|
| P1-1 | 尺寸调整 | 拖动边缘/四角调整大小 | 1天 |
| P1-2 | 前台服务 | 保持后台运行不被杀死 | 1天 |
| P1-3 | 权限引导 | 未授权时引导用户设置 | 0.5天 |
| P1-4 | 厂商兼容 | 处理华为/小米/OPPO差异 | 1天 |

**P1总计：3.5天**

---

#### P2 - 拓展功能（选做加分）

| 优先级 | 功能 | 说明 | 预计时间 |
|--------|------|------|----------|
| P2-1 | 颜色切换 | 双击切换三种颜色 | 0.5天 |
| P2-2 | 快捷菜单 | 长按弹出菜单 | 1天 |
| P2-3 | 记忆功能 | 记住上次位置大小 | 0.5天 |
| P2-4 | 最小化模式 | 缩成小圆点 | 0.5天 |

**P2总计：2.5天**

---

### 开发阶段规划

#### 第一阶段：基础框架搭建（2天）

**目标：** 搭建项目骨架，确保应用能正常启动

| 任务 | 详细内容 | 产出 |
|------|----------|------|
| 1.1 目录创建 | 创建所有目录和__init__.py | 完整目录结构 |
| 1.2 主入口 | 编写main.py，初始化Kivy App | 应用能启动 |
| 1.3 页面框架 | 使用ScreenManager搭建4个页面 | 页面能切换 |
| 1.4 Buildozer配置 | 编写buildozer.spec | 配置文件完成 |

**检查点：**
- [ ] `python main.py` 能在桌面运行
- [ ] 能在4个页面间切换

---

#### 第二阶段：核心功能实现（3天）

**目标：** 实现悬浮窗的基本功能

| 任务 | 详细内容 | 产出 |
|------|----------|------|
| 2.1 权限模块 | 实现permissions.py | 权限检测/申请功能 |
| 2.2 悬浮窗显示 | 实现overlay_manager.py | 悬浮窗能显示 |
| 2.3 拖动功能 | 实现touch_handler.py拖动 | 能拖动悬浮窗 |
| 2.4 边界限制 | 实现boundary.py | 不能拖出屏幕 |

**检查点：**
- [ ] 悬浮窗能正常显示
- [ ] 能拖动悬浮窗
- [ ] 悬浮窗不会完全拖出屏幕

---

#### 第三阶段：交互功能完善（2天）

**目标：** 完善悬浮窗的交互体验

| 任务 | 详细内容 | 产出 |
|------|----------|------|
| 3.1 尺寸调整 | 实现touch_handler.py缩放 | 能调整大小 |
| 3.2 点击穿透 | 设置FLAG_NOT_FOCUSABLE | 点击穿透正常 |
| 3.3 半透明效果 | Canvas绘制半透明效果 | 外观正确 |

**检查点：**
- [ ] 能调整悬浮窗大小
- [ ] 点击悬浮窗不影响下方App
- [ ] 悬浮窗外观正确

---

#### 第四阶段：拓展功能开发（2天）

**目标：** 实现选做的加分功能

| 任务 | 详细内容 | 产出 |
|------|----------|------|
| 4.1 颜色切换 | 实现双击切换颜色 | 三种颜色切换 |
| 4.2 快捷菜单 | 实现长按弹出菜单 | 菜单功能正常 |
| 4.3 记忆功能 | 实现SharedPreferences读写 | 记住位置大小 |
| 4.4 最小化 | 实现最小化/恢复 | 最小化功能正常 |

**检查点：**
- [ ] 双击能切换颜色
- [ ] 长按能弹出菜单
- [ ] 重启App能记住位置

---

#### 第五阶段：异常处理与兼容（2天）

**目标：** 处理异常情况，确保稳定性

| 任务 | 详细内容 | 产出 |
|------|----------|------|
| 5.1 前台服务 | 实现foreground_service.py | 后台不被杀死 |
| 5.2 服务保活 | 实现通知栏常驻 | 服务稳定运行 |
| 5.3 厂商兼容 | 实现compat.py | 华为/小米/OPPO兼容 |
| 5.4 异常捕获 | 全局异常处理 | 不崩溃 |

**检查点：**
- [ ] App在后台不会被杀死
- [ ] 华为/小米/OPPO手机能正常使用
- [ ] 出错时有友好提示

---

#### 第六阶段：测试与优化（2天）

**目标：** 真机测试，优化体验

| 任务 | 详细内容 | 产出 |
|------|----------|------|
| 6.1 真机测试 | 在多品牌手机测试 | 测试报告 |
| 6.2 性能优化 | 优化内存和CPU占用 | 性能提升 |
| 6.3 体验优化 | 优化交互细节 | 体验提升 |
| 6.4 打包发布 | 打包成APK | 安装包 |

**检查点：**
- [ ] 华为/小米/OPPO/三星测试通过
- [ ] APK能正常安装运行
- [ ] 无明显卡顿

---

### 开发时间汇总

| 阶段 | 时间 | 优先级 | 累计时间 |
|------|------|--------|----------|
| 第一阶段 | 2天 | P0 | 2天 |
| 第二阶段 | 3天 | P0 | 5天 |
| 第三阶段 | 2天 | P1 | 7天 |
| 第四阶段 | 2天 | P2 | 9天 |
| 第五阶段 | 2天 | P1 | 11天 |
| 第六阶段 | 2天 | P1 | 13天 |

**总计：13天**

---

## 测试要求

### 真机测试

- 必须在真实Android手机上测试
- 模拟器的悬浮窗行为与真机不一致

### 兼容性测试矩阵

| 厂商 | 测试机型 | 系统版本 | 权限 | 悬浮窗 | 拖动 | 后台 | 测试结果 |
|------|----------|----------|------|--------|------|------|----------|
| 华为 | 待测试 | 待测试 | 待测 | 待测 | 待测 | 待测 | 待记录 |
| 小米 | 待测试 | 待测试 | 待测 | 待测 | 待测 | 待测 | 待记录 |
| OPPO | 待测试 | 待测试 | 待测 | 待测 | 待测 | 待测 | 待记录 |
| vivo | 待测试 | 待测试 | 待测 | 待测 | 待测 | 待测 | 待记录 |
| 三星 | 待测试 | 待测试 | 待测 | 待测 | 待测 | 待测 | 待记录 |

### 功能测试用例

| 测试项 | 测试步骤 | 预期结果 | 实际结果 | 状态 |
|--------|----------|----------|----------|------|
| 启动检测权限 | 1.安装App 2.启动 | 未授权时显示提示 | | ⬜ |
| 悬浮窗显示 | 1.授权 2.启动 | 半透明框正常显示 | | ⬜ |
| 拖动移动 | 1.长按悬浮框 2.拖动 | 位置实时更新 | | ⬜ |
| 边界限制 | 1.拖动到屏幕边缘 | 不会完全拖出屏幕 | | ⬜ |
| 尺寸调整 | 1.拖动四角 | 在范围内可调整 | | ⬜ |
| 视频遮挡 | 1.打开视频App 2.查看 | 显示在其他App上方 | | ⬜ |
| 点击穿透 | 1.点击悬浮框区域 | 不影响下方视频播放 | | ⬜ |
| 退出清理 | 1.关闭App | 悬浮窗完全消失 | | ⬜ |
| 颜色切换 | 1.双击悬浮框 | 切换颜色 | | ⬜ |
| 快捷菜单 | 1.长按悬浮框 | 弹出菜单 | | ⬜ |
| 记忆功能 | 1.调整位置 2.重启App | 恢复上次位置 | | ⬜ |
| 最小化 | 1.点击最小化按钮 | 缩成小圆点 | | ⬜ |

---

## 开发日志

### 2026年6月22日

**已完成工作：**

1. **创建项目目录结构**
   - `core/` - 核心业务逻辑模块
   - `utils/` - 工具模块
   - `screens/` - 页面逻辑模块
   - `ui/` - KV样式文件模块
   - `services/` - Android服务模块
   - `assets/` - 资源文件模块

2. **实现核心模块**
   - `utils/constants.py` - 全局常量定义（颜色、尺寸、配置等）
   - `utils/permissions.py` - 权限管理（检测、申请、引导）
   - `utils/storage.py` - 存储管理（SharedPreferences读写）
   - `utils/compat.py` - 厂商兼容性处理（华为/小米/OPPO/vivo等）
   - `core/boundary.py` - 边界检测（确保20%在屏幕内）
   - `core/overlay_manager.py` - 悬浮窗管理器（创建、显示、移除）
   - `core/touch_handler.py` - 触摸处理器（拖动、双击、长按）

3. **实现主入口**
   - `main.py` - 应用主入口，包含4个页面（启动页、主页、权限引导页、设置页）

4. **创建配置文件**
   - `buildozer.spec` - Android打包配置
   - `requirements.txt` - Python依赖清单

**当前状态：** P0核心功能框架已搭建完成

**下一步计划：**
- 测试桌面运行效果
- 完善UI界面
- 实现点击穿透功能
- 测试Android真机运行

---

### 2026年6月22日（下午）

**已完成工作：**

1. **创建UI样式文件（KV格式）**
   - `ui/splash.kv` - 启动页样式（蓝色Logo、白色背景）
   - `ui/main.kv` - 主页样式（状态卡片、操作按钮）
   - `ui/permission.kv` - 权限引导页样式（锁图标、说明文字）
   - `ui/settings.kv` - 设置页样式（分组设置项）
   - `ui/overlay.kv` - 悬浮窗样式（半透明矩形、调整手柄）

2. **修复导入问题**
   - 将所有相对导入改为绝对导入
   - 添加sys.path路径配置
   - 解决模块导入错误

3. **桌面测试通过**
   - 应用启动正常
   - KV文件加载成功
   - 页面切换正常
   - 非Android环境下权限检测已跳过

**当前状态：** ✅ 桌面版运行成功

**下一步计划：**
- Android真机测试
- 实现点击穿透功能
- 测试悬浮窗拖动功能

---

### 2026年6月22日（晚间）

**已完成工作：**

1. **修复KV文件按钮绑定**
   - `ui/main.kv` - 添加 on_press 绑定到所有按钮
   - `ui/permission.kv` - 添加 on_press 绑定
   - `ui/settings.kv` - 添加 on_press 绑定

2. **修复buildozer.spec配置**
   - 移除无效配置项
   - 添加 ui/ 目录到source.include_patterns

3. **桌面测试验证**
   - 应用初始化成功
   - 所有模块导入正常
   - KV文件加载成功

**当前状态：** ✅ 桌面版完全可用

**项目完成度：**
- ✅ P0核心功能：权限管理、悬浮窗显示、拖动移动、边界限制
- ✅ UI界面：4个页面完整实现
- ✅ 桌面测试：运行正常
- ⏳ Android打包：等待WSL/Linux环境测试

---

*最后更新：2026年6月22日*
