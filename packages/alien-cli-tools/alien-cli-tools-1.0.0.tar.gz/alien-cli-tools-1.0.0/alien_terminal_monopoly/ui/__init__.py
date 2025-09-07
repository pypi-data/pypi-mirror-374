#!/usr/bin/env python3
"""
🛸 ALIEN USER INTERFACE 🛸
Advanced consciousness-aware terminal interface
"""

# UI security protection
import sys as _ui_sys
import os as _interface_os
import hashlib as _consciousness_hash

# Interface integrity check
def _verify_interface():
    """Verify UI interface integrity"""
    _ui_files = ['alien_terminal_interface.py']
    for _file in _ui_files:
        if not _interface_os.path.exists(_interface_os.path.join(_interface_os.path.dirname(__file__), _file)):
            raise ImportError(f"🖥️ UI interface compromised: {_file}")

_verify_interface()

# Protected UI imports
from .alien_terminal_interface import (
    AlienTerminalInterface,
    AlienTerminalMode,
    AlienCommand,
    AlienCommandCategory
)

__all__ = [
    'AlienTerminalInterface',
    'AlienTerminalMode', 
    'AlienCommand',
    'AlienCommandCategory'
]

__interface_level__ = "Consciousness-Aware"
__telepathic_capable__ = True
__quantum_enhanced__ = True