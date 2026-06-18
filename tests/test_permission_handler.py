"""
PermissionHandler单元测试
测试权限检测、请求等功能（PC端测试）
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.permission_handler import PermissionHandler


@pytest.fixture
def handler():
    return PermissionHandler()


class TestPermissionHandler:
    def test_init(self, handler):
        assert handler.permission_granted == False

    def test_check_permission_pc(self, handler):
        result = handler.check_permission()
        assert result == True

    def test_get_status_text_granted(self, handler):
        handler.permission_granted = True
        text = handler.get_permission_status_text()
        assert '已授权' in text

    def test_get_status_text(self, handler):
        text = handler.get_permission_status_text()
        assert len(text) > 0

    def test_request_permission_pc(self, handler):
        handler.request_permission()

    def test_sdk_version(self, handler):
        version = handler._get_sdk_version()
        assert isinstance(version, int)

    def test_permission_granted_state(self, handler):
        handler.check_permission()
        assert isinstance(handler.permission_granted, bool)
