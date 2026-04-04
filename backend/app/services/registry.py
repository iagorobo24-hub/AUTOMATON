"""
Global service registry - stores references to running services
"""

from typing import Any, Optional

_trading_engine: Any = None
_snapshot_service: Any = None
_mock_engine: Any = None
_replication_service: Any = None


def set_trading_engine(engine):
    global _trading_engine
    _trading_engine = engine


def get_trading_engine():
    return _trading_engine


def set_snapshot_service(service):
    global _snapshot_service
    _snapshot_service = service


def get_snapshot_service():
    return _snapshot_service


def set_mock_engine(engine):
    global _mock_engine
    _mock_engine = engine


def get_mock_engine():
    return _mock_engine


def set_replication_service(service):
    global _replication_service
    _replication_service = service


def get_replication_service():
    return _replication_service
