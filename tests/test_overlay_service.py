"""
OverlayService单元测试
测试悬浮窗后台服务功能（PC端测试）
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, MagicMock
from app.services.overlay_service import OverlayService


@pytest.fixture
def service():
    return OverlayService()


class TestOverlayService:
    def test_init(self, service):
        assert service.is_running == False
        assert service.overlay_widget is None

    def test_start_pc(self, service):
        mock_widget = MagicMock()
        service.start(mock_widget)
        assert service.is_running == True
        assert service.overlay_widget == mock_widget

    def test_stop_pc(self, service):
        mock_widget = MagicMock()
        service.start(mock_widget)
        service.stop()
        assert service.is_running == False
        assert service.overlay_widget is None

    def test_double_start_guard(self, service):
        mock_widget = MagicMock()
        service.start(mock_widget)
        service.start(mock_widget)
        assert service.is_running == True

    def test_stop_without_start(self, service):
        service.stop()
        assert service.is_running == False

    def test_start_stop_lifecycle(self, service):
        mock_widget = MagicMock()
        service.start(mock_widget)
        assert service.is_running == True
        service.stop()
        assert service.is_running == False
        service.start(mock_widget)
        assert service.is_running == True

    def test_overlay_widget_cleared_on_stop(self, service):
        mock_widget = MagicMock()
        service.start(mock_widget)
        assert service.overlay_widget is not None
        service.stop()
        assert service.overlay_widget is None

    def test_is_service_running_pc(self, service):
        assert service.is_service_running() == False
        service.start(MagicMock())
        assert service.is_service_running() == True

    def test_keep_alive_delegation(self, service):
        assert service.is_running == False
        service.start(MagicMock())
        assert service.is_service_running() == True
