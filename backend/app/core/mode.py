"""
Global mode manager - switches between Real and Test modes
Real mode: live trading with real wallets
Test mode: simulated trading with mock data, completely isolated
"""

_mode = "test"  # Default to test mode


def get_mode():
    """Get current app mode: 'real' or 'test'"""
    return _mode


def set_mode(mode: str):
    """Set app mode. Only 'real' or 'test' allowed."""
    global _mode
    if mode in ("real", "test"):
        _mode = mode
        return True
    return False


def is_real():
    return _mode == "real"


def is_test():
    return _mode == "test"
