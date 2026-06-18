"""
BoundaryCalculator单元测试
测试边界计算、尺寸约束、位置约束等功能
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MockWindow:
    def __init__(self):
        self.width = 1920
        self.height = 1080
        self._callbacks = {}

    def bind(self, **kwargs):
        for key, callback in kwargs.items():
            self._callbacks[key] = callback

    def unbind(self, **kwargs):
        for key in kwargs:
            self._callbacks.pop(key, None)


@pytest.fixture
def mock_window(monkeypatch):
    window = MockWindow()
    monkeypatch.setattr('app.core.boundary_calculator.Window', window)
    return window


@pytest.fixture
def boundary(mock_window):
    from app.core.boundary_calculator import BoundaryCalculator
    return BoundaryCalculator()


class TestBoundaryCalculator:
    def test_initial_size(self, boundary):
        assert boundary.screen_width == 1920
        assert boundary.screen_height == 1080

    def test_min_size(self, boundary):
        min_w, min_h = boundary.get_min_size()
        assert min_w == 80
        assert min_h == 80

    def test_max_size(self, boundary):
        max_w, max_h = boundary.get_max_size()
        assert max_w == int(1920 * 0.3)
        assert max_h == int(1080 * 0.3)

    def test_constrain_size_min(self, boundary):
        w, h = boundary.constrain_size(50, 50)
        assert w == 80
        assert h == 80

    def test_constrain_size_max(self, boundary):
        w, h = boundary.constrain_size(2000, 2000)
        assert w == int(1920 * 0.3)
        assert h == int(1080 * 0.3)

    def test_constrain_size_normal(self, boundary):
        w, h = boundary.constrain_size(300, 200)
        assert w == 300
        assert h == 200

    def test_constrain_position_center(self, boundary):
        x, y = boundary.constrain_position(500, 400, 200, 120)
        assert x == 500
        assert y == 400

    def test_constrain_position_left_edge(self, boundary):
        x, y = boundary.constrain_position(-200, 400, 200, 120)
        assert x >= -200 + 200 * 0.2

    def test_constrain_position_right_edge(self, boundary):
        x, y = boundary.constrain_position(2000, 400, 200, 120)
        assert x <= 1920 - 200 * 0.2

    def test_constrain_position_top_edge(self, boundary):
        x, y = boundary.constrain_position(500, 1200, 200, 120)
        assert y <= 1080 - 120 * 0.2

    def test_constrain_position_bottom_edge(self, boundary):
        x, y = boundary.constrain_position(500, -200, 200, 120)
        assert y >= -200 + 120 * 0.2

    def test_initial_position(self, boundary):
        x, y = boundary.calculate_initial_position(200, 120)
        assert 0 <= x <= 1920
        assert 0 <= y <= 1080

    def test_collision_detection(self, boundary):
        pos1 = (100, 100)
        size1 = (200, 120)
        pos2 = (150, 150)
        size2 = (200, 120)
        assert boundary.check_collision(pos1, size1, pos2, size2) == True

    def test_no_collision(self, boundary):
        pos1 = (100, 100)
        size1 = (200, 120)
        pos2 = (500, 500)
        size2 = (200, 120)
        assert boundary.check_collision(pos1, size1, pos2, size2) == False

    def test_visible_area_full(self, boundary):
        area = boundary.get_visible_area(100, 100, 200, 120)
        assert area == 1.0

    def test_visible_area_partial(self, boundary):
        area = boundary.get_visible_area(-100, 100, 200, 120)
        assert 0 < area < 1.0

    def test_position_valid(self, boundary):
        assert boundary.is_position_valid(100, 100, 200, 120) == True

    def test_position_invalid(self, boundary):
        assert boundary.is_position_valid(-500, -500, 200, 120) == False

    def test_window_resize(self, boundary, mock_window):
        boundary._on_window_resize(mock_window, 1280, 720)
        assert boundary.screen_width == 1280
        assert boundary.screen_height == 720
