"""
GestureHandler单元测试
测试手势识别、双击检测、长按检测、边缘检测等功能
"""

import pytest
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.gesture_handler import GestureHandler, MultiTouchHandler


class MockTouch:
    def __init__(self, x, y, uid=None):
        self.x = x
        self.y = y
        self.uid = uid or str(id(self))


@pytest.fixture
def handler():
    return GestureHandler()


@pytest.fixture
def multitouch_handler():
    return MultiTouchHandler()


class TestGestureHandler:
    def test_init(self, handler):
        assert handler.callback is None
        assert handler.tap_count == 0

    def test_callback(self):
        results = []
        def callback(gesture_type, data):
            results.append((gesture_type, data))

        handler = GestureHandler(callback=callback)
        touch = MockTouch(100, 100)
        handler.on_touch_down(touch, (50, 50), (200, 120))
        assert len(results) == 0

    def test_edge_detection_bottom_left(self, handler):
        touch = MockTouch(50, 50)
        edge = handler._detect_edge(50, 50, (50, 50), (200, 120))
        assert edge == 'bottom_left'

    def test_edge_detection_bottom_right(self, handler):
        edge = handler._detect_edge(250, 50, (50, 50), (200, 120))
        assert edge == 'bottom_right'

    def test_edge_detection_top_left(self, handler):
        edge = handler._detect_edge(50, 170, (50, 50), (200, 120))
        assert edge == 'top_left'

    def test_edge_detection_top_right(self, handler):
        edge = handler._detect_edge(250, 170, (50, 50), (200, 120))
        assert edge == 'top_right'

    def test_edge_detection_no_edge(self, handler):
        edge = handler._detect_edge(150, 110, (50, 50), (200, 120))
        assert edge is None

    def test_resize_calculation(self, handler):
        new_pos, new_size = handler.calculate_resize(
            touch_pos=(350, 50),
            edge='bottom_right',
            overlay_pos=(50, 50),
            overlay_size=(200, 120),
            min_size=(80, 80),
            max_size=(600, 400)
        )
        assert new_size[0] == 300
        assert new_size[1] == 120

    def test_resize_with_min_limit(self, handler):
        new_pos, new_size = handler.calculate_resize(
            touch_pos=(30, 30),
            edge='bottom_right',
            overlay_pos=(50, 50),
            overlay_size=(200, 120),
            min_size=(80, 80),
            max_size=(600, 400)
        )
        assert new_size[0] >= 80
        assert new_size[1] >= 80

    def test_resize_with_max_limit(self, handler):
        new_pos, new_size = handler.calculate_resize(
            touch_pos=(800, 600),
            edge='bottom_right',
            overlay_pos=(50, 50),
            overlay_size=(200, 120),
            min_size=(80, 80),
            max_size=(600, 400)
        )
        assert new_size[0] <= 600
        assert new_size[1] <= 400

    def test_double_tap_detection(self):
        results = []
        def callback(gesture_type, data):
            results.append((gesture_type, data))

        handler = GestureHandler(callback=callback)

        touch1 = MockTouch(100, 100)
        handler.on_touch_down(touch1, (50, 50), (200, 120))

        handler.last_touch_time = time.time() - 0.1

        touch2 = MockTouch(100, 100)
        handler.on_touch_down(touch2, (50, 50), (200, 120))

        assert len(results) == 1
        assert results[0][0] == 'double_tap'

    def test_drag_detection(self):
        results = []
        def callback(gesture_type, data):
            results.append((gesture_type, data))

        handler = GestureHandler(callback=callback)

        touch = MockTouch(100, 100)
        handler.on_touch_down(touch, (50, 50), (200, 120))

        move_touch = MockTouch(200, 200)
        result = handler.on_touch_move(move_touch, (50, 50), (200, 120))

        assert result == 'drag'


class TestMultiTouchHandler:
    def test_init(self, multitouch_handler):
        assert multitouch_handler.touches == {}

    def test_single_touch(self, multitouch_handler):
        touch = MockTouch(100, 100, uid='1')
        multitouch_handler.on_touch_down(touch, (200, 120))
        assert '1' in multitouch_handler.touches

    def test_two_finger_touch(self, multitouch_handler):
        touch1 = MockTouch(100, 100, uid='1')
        touch2 = MockTouch(200, 200, uid='2')

        multitouch_handler.on_touch_down(touch1, (200, 120))
        multitouch_handler.on_touch_down(touch2, (200, 120))

        assert multitouch_handler.initial_distance > 0
        assert multitouch_handler.initial_size == (200, 120)

    def test_pinch_zoom(self):
        results = []
        def callback(gesture_type, data):
            results.append((gesture_type, data))

        handler = MultiTouchHandler(callback=callback)

        touch1 = MockTouch(100, 100, uid='1')
        touch2 = MockTouch(200, 200, uid='2')

        handler.on_touch_down(touch1, (200, 120))
        handler.on_touch_down(touch2, (200, 120))

        touch1_move = MockTouch(150, 150, uid='1')
        touch2_move = MockTouch(250, 250, uid='2')

        handler.touches['1'] = (150, 150)
        handler.touches['2'] = (250, 250)

        scale = handler.on_touch_move(touch1_move)

        assert scale is not None
        assert scale > 0

    def test_touch_up(self, multitouch_handler):
        touch = MockTouch(100, 100, uid='1')
        multitouch_handler.on_touch_down(touch, (200, 120))
        assert '1' in multitouch_handler.touches

        multitouch_handler.on_touch_up(touch)
        assert '1' not in multitouch_handler.touches

    def test_distance_calculation(self, multitouch_handler):
        d = multitouch_handler._calculate_distance((0, 0), (3, 4))
        assert d == 5.0
