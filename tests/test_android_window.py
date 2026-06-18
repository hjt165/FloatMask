"""
AndroidWindowManager和NativeOverlay单元测试
测试Android原生窗口管理功能（PC端测试）
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, MagicMock
from app.services.android_window import AndroidWindowManager, NativeOverlay, GRAVITY_TOP_LEFT


@pytest.fixture
def manager():
    return AndroidWindowManager()


@pytest.fixture
def overlay():
    return NativeOverlay()


class TestAndroidWindowManager:
    def test_init(self, manager):
        assert manager._window_manager is None
        assert manager._view is None
        assert manager._params is None
        assert manager._is_showing == False

    def test_gravity_constant(self):
        assert GRAVITY_TOP_LEFT == 0x33

    def test_check_permission_pc(self, manager):
        result = manager.check_permission()
        assert result == True

    def test_initialize_pc(self, manager):
        result = manager.initialize()
        assert result == False

    def test_add_overlay_view_pc(self, manager):
        result = manager.add_overlay_view(100, 100, 200, 120)
        assert result == False

    def test_remove_overlay_view_pc(self, manager):
        result = manager.remove_overlay_view()
        assert result == False

    def test_update_position_pc(self, manager):
        result = manager.update_position(200, 200)
        assert result == False

    def test_update_size_pc(self, manager):
        result = manager.update_size(300, 300)
        assert result == False

    def test_set_touch_through_pc(self, manager):
        result = manager.set_touch_through(True)
        assert result == False

    def test_is_showing_property(self, manager):
        assert manager.is_showing == False

    def test_is_showing_after_failed_add(self, manager):
        manager.add_overlay_view(0, 0, 100, 100)
        assert manager.is_showing == False


class TestNativeOverlay:
    def test_init(self, overlay):
        assert overlay._initialized == False
        assert overlay.manager is not None

    def test_initialize_pc(self, overlay):
        result = overlay.initialize()
        assert result == False

    def test_show_pc(self, overlay):
        result = overlay.show()
        assert result == False

    def test_hide_pc(self, overlay):
        result = overlay.hide()
        assert result == False

    def test_move_pc(self, overlay):
        result = overlay.move(200, 200)
        assert result == False

    def test_resize_pc(self, overlay):
        result = overlay.resize(300, 300)
        assert result == False

    def test_set_passthrough_pc(self, overlay):
        result = overlay.set_passthrough(True)
        assert result == False

    def test_is_visible_property(self, overlay):
        assert overlay.is_visible == False

    def test_show_auto_initializes(self, overlay):
        overlay.show()
        assert overlay._initialized == False
