"""
ConfigManager单元测试
测试配置加载、保存、默认值等功能
"""

import pytest
import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.config import ConfigManager


@pytest.fixture
def config():
    return ConfigManager()


@pytest.fixture
def temp_config(tmp_path):
    monkeypatch = pytest.MonkeyPatch()

    original_get = ConfigManager._get_config_file_path
    config_file = str(tmp_path / 'test_config.json')

    def mock_get_path(self):
        return config_file

    monkeypatch.setattr(ConfigManager, '_get_config_file_path', mock_get_path)

    yield ConfigManager()

    monkeypatch.undo()


class TestConfigManager:
    def test_default_config(self, config):
        assert 'overlay' in config.config
        assert 'behavior' in config.config
        assert 'memory' in config.config

    def test_overlay_defaults(self, config):
        overlay = config.get_overlay_config()
        assert overlay['width'] == 200
        assert overlay['height'] == 120
        assert overlay['color'] == [0.5, 0.5, 0.5, 0.5]

    def test_get_value(self, config):
        assert config.get('overlay', 'width') == 200
        assert config.get('overlay', 'nonexistent', 'default') == 'default'

    def test_set_value(self, temp_config):
        temp_config.set('test', 'key', 'value')
        assert temp_config.get('test', 'key') == 'value'

    def test_set_overlay_position(self, temp_config):
        temp_config.set_overlay_position(100, 200)
        assert temp_config.get('overlay', 'x') == 100
        assert temp_config.get('overlay', 'y') == 200

    def test_set_overlay_size(self, temp_config):
        temp_config.set_overlay_size(300, 250)
        assert temp_config.get('overlay', 'width') == 300
        assert temp_config.get('overlay', 'height') == 250

    def test_set_overlay_color(self, temp_config):
        temp_config.set_overlay_color(1.0, 0.0, 0.0, 0.8)
        assert temp_config.get('overlay', 'color') == [1.0, 0.0, 0.0, 0.8]

    def test_reset_to_default(self, temp_config):
        temp_config.set('overlay', 'width', 500)
        assert temp_config.config['overlay']['width'] == 500
        temp_config.reset_to_default()
        assert temp_config.config['overlay']['width'] == 200

    def test_save_and_load(self, temp_config):
        temp_config.set_overlay_position(150, 250)
        temp_config.set_overlay_size(350, 280)

        new_config = ConfigManager()
        assert new_config.get('overlay', 'x') == 150
        assert new_config.get('overlay', 'y') == 250
        assert new_config.get('overlay', 'width') == 350
        assert new_config.get('overlay', 'height') == 280

    def test_behavior_config(self, config):
        behavior = config.config.get('behavior', {})
        assert behavior.get('min_visible_percent') == 0.2
        assert behavior.get('long_press_threshold') == 0.5
        assert behavior.get('double_tap_threshold') == 0.3

    def test_memory_config(self, config):
        memory = config.config.get('memory', {})
        assert memory.get('remember_position') == True
        assert memory.get('remember_size') == True
        assert memory.get('remember_color') == False

    def test_click_through_default(self, config):
        assert config.get_click_through() == False

    def test_click_through_set(self, temp_config):
        temp_config.set_click_through(True)
        assert temp_config.get_click_through() == True
        temp_config.set_click_through(False)
        assert temp_config.get_click_through() == False

    def test_overlay_mode_default(self, config):
        assert config.get_overlay_mode() == 'auto'

    def test_overlay_mode_set(self, temp_config):
        temp_config.set_overlay_mode('native')
        assert temp_config.get_overlay_mode() == 'native'
        temp_config.set_overlay_mode('kivy')
        assert temp_config.get_overlay_mode() == 'kivy'

    def test_overlay_mode_invalid(self, temp_config):
        with pytest.raises(ValueError):
            temp_config.set_overlay_mode('invalid')

    def test_overlay_defaults_include_new_fields(self, config):
        overlay = config.get_overlay_config()
        assert 'click_through' in overlay
        assert 'overlay_mode' in overlay
        assert overlay['click_through'] == False
        assert overlay['overlay_mode'] == 'auto'
