"""
Root conftest.py - patches AMPCS modules before any application imports.
This ensures that modules like mtak.wrapper, lad.client, etc. can be
imported without AMPCS being installed.
"""
import sys
from unittest.mock import MagicMock

# Patch AMPCS modules before any application imports
sys.modules['mtak'] = MagicMock()
sys.modules['mtak.wrapper'] = MagicMock()
sys.modules['lad'] = MagicMock()
sys.modules['lad.client'] = MagicMock()
sys.modules['lad.gdsclient'] = MagicMock()
