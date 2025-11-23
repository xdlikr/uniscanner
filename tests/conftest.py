"""
Pytest配置和共享fixtures
"""

import pytest
from pathlib import Path
import sys

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def fixtures_dir():
    """测试夹具目录"""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def valid_constitution_path(fixtures_dir):
    """有效的宪法文件路径"""
    return fixtures_dir / "valid_constitution.yaml"


@pytest.fixture
def invalid_constitution_path(fixtures_dir):
    """无效的宪法文件路径"""
    return fixtures_dir / "invalid_constitution.yaml"


@pytest.fixture
def temp_log_dir(tmp_path):
    """临时日志目录"""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return log_dir

