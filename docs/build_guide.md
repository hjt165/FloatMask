# FloatMask APK 打包指南

## 方法一：Google Colab（推荐 - 最快）

### 步骤1：打开Colab
浏览器访问 https://colab.research.google.com → 新建笔记本

### 步骤2：安装Buildozer（执行一次）
在第一个Cell中粘贴运行：
```python
!sudo apt-get update
!sudo apt-get install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev automake autopoint gettext
!pip install --upgrade pip Cython==0.29.34
!pip install git+https://github.com/kivy/buildozer.git
```

### 步骤3：上传项目
1. 左侧文件面板点击 **上传** 图标
2. 将整个 `Comprehensive_Course_Design` 文件夹拖入
3. 等待上传完成

### 步骤4：打包APK
```python
import os
os.chdir('/content/Comprehensive_Course_Design')
!buildozer -v android debug 2>&1 | tee build.log
```

### 步骤5：下载APK
打包完成后，在左侧文件面板进入 `bin/` 目录，右键下载 `.apk` 文件

---

## 方法二：GitHub Actions（自动化）

### 步骤1：创建GitHub仓库
```bash
git init
git add .
git commit -m "FloatMask v1.0.0"
git remote add origin https://github.com/你的用户名/FloatMask.git
git push -u origin main
```

### 步骤2：自动构建
推送到GitHub后，Actions会自动打包APK

### 步骤3：下载APK
进入 GitHub 仓库 → Actions → 最新构建 → Artifacts → 下载 `FloatMask-APK`

---

## 真机安装与调试

### 1. 开启开发者选项
手机设置 → 关于手机 → 连续点击"版本号"7次 → 返回开启USB调试

### 2. 连接电脑
USB连接手机，执行：
```bash
adb devices                    # 确认设备已连接
adb install floatmask.apk      # 安装APK
```

### 3. 授予权限
```bash
adb shell pm grant org.floatmask.floatmask android.permission.SYSTEM_ALERT_WINDOW
```

### 4. 测试
1. 打开FloatMask应用
2. 点击"启动悬浮框"
3. 切换到视频App（B站/抖音/YouTube）
4. 测试拖拽、双击变色、长按菜单
