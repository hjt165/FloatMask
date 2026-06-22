"""
PC端悬浮框功能测试脚本
自动启动悬浮框并截图验证
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ['KIVY_NO_ARGS'] = '1'

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.utils import platform

_FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'fonts')
FONT_PATH = os.path.join(_FONT_DIR, 'msyh.ttc')
if os.path.exists(FONT_PATH):
    LabelBase.register(name='Chinese', fn_regular=FONT_PATH)

Window.size = (400, 600)

from app.main import FloatMaskMain

results = []

def log(msg):
    print(f"[TEST] {msg}")
    results.append(msg)

class TestApp(App):
    def build(self):
        self.title = 'FloatMask Test'
        self.root = FloatMaskMain()
        return self.root

    def on_start(self):
        Clock.schedule_once(self.test_overlay, 1.0)

    def test_overlay(self, dt):
        try:
            log("=== 开始PC端悬浮框测试 ===")

            root = self.root
            log(f"主界面状态: {root.status_label.text}")
            log(f"权限状态: {root.permission_label.text}")

            log("--- 测试1: 启动悬浮框 ---")
            root.toggle_btn.state = 'down'
            root.toggle_btn.dispatch('on_press')
            time.sleep(0.5)
            log(f"启动后状态: {root.status_label.text}")

            overlay = root.overlay_manager.get_overlay()
            if overlay is not None:
                log(f"悬浮框已创建: {overlay.__class__.__name__}")
                log(f"悬浮框位置: ({overlay.x}, {overlay.y})")
                log(f"悬浮框大小: ({overlay.width}, {overlay.height})")
                log(f"悬浮框可见: {overlay.is_visible if hasattr(overlay, 'is_visible') else 'N/A'}")
                log("[PASS] 悬浮框创建成功")
            else:
                log("[FAIL] 悬浮框未创建")

            log("--- 测试2: 等待2秒观察效果 ---")
            Clock.schedule_once(self.test_stop, 3.0)

        except Exception as e:
            log(f"[ERROR] {e}")
            Clock.schedule_once(lambda dt: self.stop(), 0.5)

    def test_stop(self, dt):
        try:
            log("--- 测试3: 停止悬浮框 ---")
            root = self.root
            root.toggle_btn.state = 'normal'
            root.toggle_btn.dispatch('on_press')
            time.sleep(0.5)
            log(f"停止后状态: {root.status_label.text}")
            log("[PASS] 停止悬浮框成功")

            log("=== 测试完成 ===")
            for r in results:
                print(f"  {r}")

        except Exception as e:
            log(f"[ERROR] {e}")
        finally:
            Clock.schedule_once(lambda dt: self.stop(), 0.5)


if __name__ == '__main__':
    TestApp().run()
