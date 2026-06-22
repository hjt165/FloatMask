"""
pytest配置文件
设置测试路径和全局fixtures
"""

import sys
import os

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
