"""
KeepAliveService单元测试
测试服务保活功能（PC端测试）
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, MagicMock
from app.services.keep_alive_service import KeepAliveService


@pytest.fixture
def service():
    return KeepAliveService()


class TestKeepAliveService:
    def test_init(self, service):
        assert service.is_running == False
        assert service._wake_lock is None
        assert service._notification_id == 1001

    def test_start_pc(self, service):
        service.start()
        assert service.is_running == True

    def test_stop_pc(self, service):
        service.start()
        service.stop()
        assert service.is_running == False

    def test_double_start_guard(self, service):
        service.start()
        service.start()
        assert service.is_running == True

    def test_stop_without_start(self, service):
        service.stop()
        assert service.is_running == False

    def test_start_stop_lifecycle(self, service):
        service.start()
        assert service.is_running == True
        service.stop()
        assert service.is_running == False
        service.start()
        assert service.is_running == True

    def test_wake_lock_initial_none(self, service):
        assert service._wake_lock is None

    def test_stop_releases_wake_lock(self, service):
        service._wake_lock = MagicMock()
        service._wake_lock.isHeld.return_value = True
        service.start()
        service.stop()
        assert service.is_running == False

    def test_notification_id(self, service):
        assert service._notification_id == 1001
        assert isinstance(service._notification_id, int)
