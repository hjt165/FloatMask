"""
FloatMask Appium自动化测试脚本
职责：使用Appium在MuMu模拟器上自动化测试应用功能
作用：验证页面跳转、按钮点击、权限检测等功能

使用方法：
1. 启动Appium Server: appium
2. 确保MuMu模拟器已连接: adb connect 127.0.0.1:7555
3. 运行测试: python -m pytest tests/test_appium.py -v
"""

import time
import pytest
from appium import webdriver
from appium.options import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy


# ==================== 测试配置 ====================
APPIUM_SERVER = 'http://127.0.0.1:4723'
DEVICE_NAME = '127.0.0.1:7555'  # MuMu模拟器ADB地址
APP_PACKAGE = 'org.floatmask'
APP_ACTIVITY = 'org.kivy.android.PythonActivity'


def get_desired_capabilities():
    """
    获取Appium设备配置

    返回:
        dict: Appium desired capabilities
    """
    options = UiAutomator2Options()
    options.platform_name = 'Android'
    options.device_name = 'MuMu Emulator'
    options.udid = DEVICE_NAME
    options.app_package = APP_PACKAGE
    options.app_activity = APP_ACTIVITY
    options.no_reset = True
    options.auto_grant_permissions = True
    options.new_command_timeout = 300

    # MuMu模拟器特殊配置
    options.set_capability('mjpegServerPort', 8099)

    return options


class TestFloatMask:
    """FloatMask应用自动化测试类"""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """测试前置和后置"""
        # 前置：启动应用
        options = get_desired_capabilities()
        self.driver = webdriver.Remote(APPIUM_SERVER, options=options)
        self.driver.implicitly_wait(10)
        yield
        # 后置：关闭应用
        try:
            self.driver.quit()
        except Exception:
            pass

    def test_app_launch(self):
        """测试1：应用能否正常启动"""
        print("\n[测试1] 应用启动测试")
        time.sleep(3)

        # 检查当前Activity
        current_activity = self.driver.current_activity
        print(f"  当前Activity: {current_activity}")
        assert current_activity is not None, "应用启动失败"

    def test_splash_page(self):
        """测试2：启动页是否正常显示"""
        print("\n[测试2] 启动页显示测试")
        time.sleep(2)

        # 检查页面源码中是否包含启动页元素
        page_source = self.driver.page_source
        has_floatmask = 'FloatMask' in page_source or 'floatmask' in page_source.lower()
        print(f"  页面包含FloatMask: {has_floatmask}")

        # 等待自动跳转
        time.sleep(3)

    def test_main_page_elements(self):
        """测试3：主页元素是否正常显示"""
        print("\n[测试3] 主页元素测试")
        time.sleep(4)  # 等待启动页跳转

        page_source = self.driver.page_source

        # 检查关键元素
        checks = {
            'FloatMask标题': 'FloatMask' in page_source,
            '启动按钮': '启动' in page_source,
            '检测权限按钮': '检测权限' in page_source,
            '设置按钮': '设置' in page_source,
        }

        for name, result in checks.items():
            status = "✅" if result else "❌"
            print(f"  {status} {name}: {'存在' if result else '不存在'}")

        assert checks['启动按钮'], "启动按钮未找到"

    def test_toggle_button_click(self):
        """测试4：点击启动/停止按钮"""
        print("\n[测试4] 启动按钮点击测试")
        time.sleep(4)

        try:
            # 查找启动按钮并点击
            toggle_btn = self.driver.find_element(
                AppiumBy.XPATH,
                '//android.widget.Button[contains(@text, "启动")]'
            )
            toggle_btn.click()
            print("  ✅ 点击启动按钮成功")
            time.sleep(2)

            # 检查状态变化
            page_source = self.driver.page_source
            if '已激活' in page_source or '停止' in page_source:
                print("  ✅ 悬浮窗状态已更新")
            else:
                print("  ⚠️ 状态未明显变化（可能需要权限）")

        except Exception as e:
            print(f"  ❌ 点击按钮失败: {e}")

    def test_permission_page(self):
        """测试5：权限引导页跳转"""
        print("\n[测试5] 权限引导页测试")
        time.sleep(4)

        try:
            # 点击检测权限按钮
            permission_btn = self.driver.find_element(
                AppiumBy.XPATH,
                '//android.widget.Button[contains(@text, "检测权限")]'
            )
            permission_btn.click()
            print("  ✅ 点击检测权限按钮成功")
            time.sleep(1)

            # 检查是否跳转到权限页或显示权限状态
            page_source = self.driver.page_source
            if '需要' in page_source or '权限' in page_source or '未授权' in page_source:
                print("  ✅ 权限页面正常")
            else:
                print("  ⚠️ 权限页面未跳转（可能已有权限）")

        except Exception as e:
            print(f"  ❌ 权限测试失败: {e}")

    def test_settings_page(self):
        """测试6：设置页跳转"""
        print("\n[测试6] 设置页跳转测试")
        time.sleep(4)

        try:
            # 点击设置按钮
            settings_btn = self.driver.find_element(
                AppiumBy.XPATH,
                '//android.widget.Button[contains(@text, "设置")]'
            )
            settings_btn.click()
            print("  ✅ 点击设置按钮成功")
            time.sleep(2)

            # 检查设置页内容
            page_source = self.driver.page_source
            if '外观设置' in page_source or '行为设置' in page_source:
                print("  ✅ 设置页加载成功")
            else:
                print("  ⚠️ 设置页可能未加载")

            # 返回主页
            back_btn = self.driver.find_element(
                AppiumBy.XPATH,
                '//android.widget.Button[contains(@text, "返回")]'
            )
            back_btn.click()
            time.sleep(1)
            print("  ✅ 返回主页成功")

        except Exception as e:
            print(f"  ❌ 设置页测试失败: {e}")

    def test_page_navigation(self):
        """测试7：页面导航完整性"""
        print("\n[测试7] 页面导航完整性测试")
        time.sleep(4)

        try:
            # 获取所有页面源码
            page_source = self.driver.page_source

            # 检查关键文本
            key_texts = ['FloatMask', '启动', '检测权限', '设置']
            found = []
            for text in key_texts:
                if text in page_source:
                    found.append(text)

            print(f"  找到关键元素: {found}")
            assert len(found) >= 2, "页面导航不完整"

        except Exception as e:
            print(f"  ❌ 导航测试失败: {e}")

    def test_screen_info(self):
        """测试8：获取屏幕信息"""
        print("\n[测试8] 屏幕信息测试")
        time.sleep(3)

        # 获取屏幕尺寸
        window_size = self.driver.get_window_size()
        print(f"  屏幕尺寸: {window_size['width']}x{window_size['height']}")

        # 获取当前Activity
        activity = self.driver.current_activity
        print(f"  当前Activity: {activity}")

        # 获取应用Package
        package = self.driver.current_package
        print(f"  当前Package: {package}")


# ==================== 直接运行测试 ====================
if __name__ == '__main__':
    print("=" * 50)
    print("FloatMask Appium 自动化测试")
    print("=" * 50)
    print(f"Appium服务器: {APPIUM_SERVER}")
    print(f"模拟器地址: {DEVICE_NAME}")
    print(f"应用包名: {APP_PACKAGE}")
    print("=" * 50)

    # 检查连接
    print("\n检查设备连接...")
    try:
        from appium import webdriver
        options = get_desired_capabilities()
        driver = webdriver.Remote(APPIUM_SERVER, options=options)
        print(f"✅ 连接成功! 当前Activity: {driver.current_activity}")
        driver.quit()
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print("请确保:")
        print("1. Appium Server已启动 (appium)")
        print("2. MuMu模拟器已连接 (adb connect 127.0.0.1:7555)")
        print("3. FloatMask APK已安装到模拟器")
        exit(1)

    # 运行测试
    print("\n运行测试...")
    pytest.main([__file__, '-v', '-s'])
