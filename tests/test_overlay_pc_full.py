"""
PC端悬浮框全面交互测试 v2
修复: MockTouch复用/颜色断言/持久化尺寸
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

Window.size = (800, 600)

from app.main import FloatMaskMain
from app.ui.quick_menu import QuickMenu


class MockTouch:
    def __init__(self, x, y, uid='test'):
        self.x = x
        self.y = y
        self.uid = uid
        self.is_mouse_scroll = False
        self.button = 'left'
        self.grab_list = []

    def grab(self, w):
        pass

    def ungrab(self, w):
        pass


passed = 0
failed = 0
errors = []


def log_pass(name):
    global passed
    passed += 1
    print(f"  [PASS] {name}")


def log_fail(name, reason):
    global failed
    failed += 1
    errors.append((name, reason))
    print(f"  [FAIL] {name}: {reason}")


def log_section(name):
    print(f"\n{'='*50}")
    print(f"  {name}")
    print(f"{'='*50}")


class FullTestApp(App):
    def build(self):
        self.title = 'FloatMask Full Test'
        self.root_widget = FloatMaskMain()
        return self.root_widget

    def on_start(self):
        Clock.schedule_once(self.run_tests, 1.5)

    def run_tests(self, dt):
        root = self.root_widget
        overlay_mgr = root.overlay_manager

        log_section("1. 启动悬浮框")
        try:
            root.toggle_btn.state = 'down'
            root.toggle_btn.dispatch('on_press')
            overlay = overlay_mgr.get_overlay()
            if overlay and overlay_mgr.is_running:
                log_pass("启动悬浮框")
            else:
                log_fail("启动悬浮框", f"overlay={overlay} running={overlay_mgr.is_running}")
        except Exception as e:
            log_fail("启动悬浮框", str(e))
            overlay = overlay_mgr.get_overlay()

        log_section("2. 拖动悬浮框")
        self._test_drag(overlay, overlay_mgr)

    def _test_drag(self, overlay, overlay_mgr):
        try:
            ox, oy = overlay.x, overlay.y
            cx = ox + overlay.overlay_width / 2
            cy = oy + overlay.overlay_height / 2

            touch = MockTouch(cx, cy, 'drag')
            overlay._on_window_touch_down(Window, touch)

            touch.x = cx + 100
            touch.y = cy + 50
            overlay._on_window_touch_move(Window, touch)
            overlay._on_window_touch_up(Window, touch)

            new_ox, new_oy = overlay.x, overlay.y
            dx = abs(new_ox - ox)
            dy = abs(new_oy - oy)
            if dx > 50 and dy > 30:
                log_pass("拖动悬浮框")
            else:
                log_fail("拖动悬浮框", f"偏移不足 dx={dx} dy={dy} 期望>50,>30")
        except Exception as e:
            log_fail("拖动悬浮框", str(e))

        log_section("3. 调整大小（右下角）")
        self._test_resize_br(overlay, overlay_mgr)

    def _test_resize_br(self, overlay, overlay_mgr):
        try:
            old_w, old_h = overlay.overlay_width, overlay.overlay_height
            hx = overlay.x + overlay.overlay_width
            hy = overlay.y

            touch = MockTouch(hx, hy, 'resize')
            overlay._on_window_touch_down(Window, touch)

            touch.x = hx + 80
            touch.y = hy - 80
            overlay._on_window_touch_move(Window, touch)
            overlay._on_window_touch_up(Window, touch)

            new_w, new_h = overlay.overlay_width, overlay.overlay_height
            if new_w > old_w or new_h > old_h:
                log_pass("调整大小（右下角）")
            else:
                log_fail("调整大小（右下角）", f"尺寸未变化 w:{old_w}->{new_w} h:{old_h}->{new_h}")
        except Exception as e:
            log_fail("调整大小（右下角）", str(e))

        log_section("4. 最小化")
        self._test_minimize(overlay, overlay_mgr)

    def _test_minimize(self, overlay, overlay_mgr):
        try:
            if overlay.is_minimized:
                overlay.restore()

            btn_x = overlay.x + overlay.overlay_width - 15
            btn_y = overlay.y + overlay.overlay_height - 15

            touch = MockTouch(btn_x, btn_y, 'min')
            overlay._on_window_touch_down(Window, touch)

            if overlay.is_minimized:
                log_pass("最小化")
            else:
                log_fail("最小化", f"is_minimized={overlay.is_minimized}")
        except Exception as e:
            log_fail("最小化", str(e))

        log_section("5. 从最小化恢复")
        self._test_restore(overlay, overlay_mgr)

    def _test_restore(self, overlay, overlay_mgr):
        try:
            dot_x = overlay.x + overlay.minimized_size / 2
            dot_y = overlay.y + overlay.minimized_size / 2

            touch = MockTouch(dot_x, dot_y, 'restore')
            overlay._on_window_touch_down(Window, touch)

            if not overlay.is_minimized:
                log_pass("从最小化恢复")
            else:
                log_fail("从最小化恢复", f"is_minimized={overlay.is_minimized}")
        except Exception as e:
            log_fail("从最小化恢复", str(e))

        log_section("6. 双击切换颜色")
        self._test_double_tap(overlay, overlay_mgr)

    def _test_double_tap(self, overlay, overlay_mgr):
        try:
            old_color = tuple(overlay.overlay_color)
            cx = overlay.x + overlay.overlay_width / 2
            cy = overlay.y + overlay.overlay_height / 2

            t1 = MockTouch(cx, cy, 'dt1')
            overlay._on_window_touch_down(Window, t1)
            overlay._on_window_touch_up(Window, t1)
            time.sleep(0.05)

            t2 = MockTouch(cx, cy, 'dt2')
            overlay._on_window_touch_down(Window, t2)
            overlay._on_window_touch_up(Window, t2)
            time.sleep(0.1)

            new_color = tuple(overlay.overlay_color)
            if new_color != old_color:
                log_pass("双击切换颜色")
            else:
                log_fail("双击切换颜色", f"颜色未变化: {new_color}")
        except Exception as e:
            log_fail("双击切换颜色", str(e))

        log_section("7. 长按显示快捷菜单")
        self._test_long_press(overlay, overlay_mgr)

    def _test_long_press(self, overlay, overlay_mgr):
        try:
            overlay._on_long_press()

            if hasattr(overlay, 'quick_menu') and overlay.quick_menu.is_visible:
                log_pass("长按显示快捷菜单")
            else:
                log_fail("长按显示快捷菜单", "菜单未显示")
        except Exception as e:
            log_fail("长按显示快捷菜单", str(e))

        log_section("8. 快捷菜单 - 切换颜色")
        self._test_menu_color(overlay, overlay_mgr)

    def _test_menu_color(self, overlay, overlay_mgr):
        try:
            if hasattr(overlay, 'quick_menu') and overlay.quick_menu.is_visible:
                overlay.quick_menu.hide()

            overlay.set_color(1.0, 0.0, 0.0, 0.5)
            old_color = tuple(overlay.overlay_color)
            menu = QuickMenu(overlay_widget=overlay)
            menu.current_color_index = 0
            menu._on_color_change()
            time.sleep(0.1)

            new_color = tuple(overlay.overlay_color)
            if new_color != old_color:
                log_pass("快捷菜单 - 切换颜色")
            else:
                log_fail("快捷菜单 - 切换颜色", f"颜色未变化: {new_color}")
        except Exception as e:
            log_fail("快捷菜单 - 切换颜色", str(e))

        log_section("9. 快捷菜单 - 调节透明度")
        self._test_menu_opacity(overlay, overlay_mgr)

    def _test_menu_opacity(self, overlay, overlay_mgr):
        try:
            overlay.set_color(0.5, 0.5, 0.5, 0.4)
            old_a = overlay.overlay_color[3]

            menu = QuickMenu(overlay_widget=overlay)
            menu._on_opacity_change()

            new_a = overlay.overlay_color[3]
            if new_a > old_a:
                log_pass("快捷菜单 - 调节透明度")
            else:
                log_fail("快捷菜单 - 调节透明度", f"透明度未变化: {old_a} -> {new_a}")
        except Exception as e:
            log_fail("快捷菜单 - 调节透明度", str(e))

        log_section("10. 快捷菜单 - 关闭悬浮框")
        self._test_menu_close(overlay, overlay_mgr)

    def _test_menu_close(self, overlay, overlay_mgr):
        try:
            menu = QuickMenu(overlay_widget=overlay)
            menu._on_close()
            time.sleep(0.3)

            if not overlay_mgr.is_running:
                log_pass("快捷菜单 - 关闭悬浮框")
            else:
                log_fail("快捷菜单 - 关闭悬浮框", f"is_running={overlay_mgr.is_running}")
        except Exception as e:
            log_fail("快捷菜单 - 关闭悬浮框", str(e))

        log_section("11. 配置持久化")
        self._test_persistence(overlay_mgr)

    def _test_persistence(self, overlay_mgr):
        try:
            root = self.root_widget
            root.toggle_btn.state = 'down'
            root.toggle_btn.dispatch('on_press')
            time.sleep(0.5)

            overlay = overlay_mgr.get_overlay()
            if not overlay:
                log_fail("配置持久化", "首次创建失败")
                return

            overlay.x = 50
            overlay.y = 100
            overlay.overlay_width = 110
            overlay.overlay_height = 100
            overlay._draw_overlay()

            overlay_mgr.save_current_config()
            overlay_mgr.destroy()
            time.sleep(0.3)

            root.toggle_btn.state = 'down'
            root.toggle_btn.dispatch('on_press')
            time.sleep(0.5)

            overlay2 = overlay_mgr.get_overlay()
            if overlay2:
                w_ok = abs(overlay2.overlay_width - 110) < 15
                h_ok = abs(overlay2.overlay_height - 100) < 15
                if w_ok and h_ok:
                    log_pass("配置持久化")
                else:
                    log_fail("配置持久化", f"大小不匹配: {overlay2.overlay_width}x{overlay2.overlay_height} 期望≈110x100")
            else:
                log_fail("配置持久化", "重启后overlay为None")
        except Exception as e:
            log_fail("配置持久化", str(e))

        log_section("12. 主界面停止")
        self._test_stop()

    def _test_stop(self):
        try:
            root = self.root_widget
            root.toggle_btn.state = 'normal'
            root.toggle_btn.dispatch('on_press')
            time.sleep(0.5)

            if not root.overlay_manager.is_running:
                log_pass("主界面停止")
            else:
                log_fail("主界面停止", f"is_running={root.overlay_manager.is_running}")
        except Exception as e:
            log_fail("主界面停止", str(e))

        self._print_summary()

    def _print_summary(self):
        print(f"\n{'='*50}")
        print(f"  测试汇总: {passed} 通过, {failed} 失败, 共 {passed+failed} 项")
        print(f"{'='*50}")
        if errors:
            print("\n  失败详情:")
            for name, reason in errors:
                print(f"    - {name}: {reason}")
        print()
        Clock.schedule_once(lambda dt: self.stop(), 0.5)


if __name__ == '__main__':
    FullTestApp().run()
