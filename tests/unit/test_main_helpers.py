"""Unit tests for main.py helper functions."""
import sys
import os

# Ensure the repo root is on sys.path so main can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from main import check_default_cmd_string


class TestCheckDefaultCmdString:
    def test_value_a(self):
        assert check_default_cmd_string('A') == 'A'

    def test_value_b(self):
        assert check_default_cmd_string('B') == 'B'

    def test_value_ab(self):
        assert check_default_cmd_string('AB') == 'AB'

    def test_default_returns_none(self):
        assert check_default_cmd_string('DEFAULT') is None

    def test_none_returns_none(self):
        assert check_default_cmd_string(None) is None

    def test_invalid_returns_none(self):
        assert check_default_cmd_string('XYZ') is None
