import pytest

import sys
import os

# Ensure project root is on sys.path for imports
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


class DummyCursor:
    def __init__(self, description=None, rows=None):
        self._description = description or []
        self._rows = rows or []
        self._fetched = False

    @property
    def description(self):
        return self._description

    def execute(self, *args, **kwargs):
        pass

    def fetchall(self):
        return self._rows

    def fetchone(self):
        return None

    def close(self):
        pass

class DummyConnection:
    def cursor(self):
        return DummyCursor()

class DummyMySQL:
    def __init__(self):
        self.connection = DummyConnection()


def test_get_reservasi_by_user_returns_list(monkeypatch):
    import importlib
    import app
    dummy = DummyMySQL()
    monkeypatch.setattr(app, 'mysql', dummy)
    rm = importlib.reload(importlib.import_module('app.models.reservasi_model'))

    res = rm.get_reservasi_by_user(123)
    assert isinstance(res, list)


def test_get_all_reservasi_returns_list(monkeypatch):
    import importlib
    import app
    dummy = DummyMySQL()
    monkeypatch.setattr(app, 'mysql', dummy)
    rm = importlib.reload(importlib.import_module('app.models.reservasi_model'))

    res = rm.get_all_reservasi()
    assert isinstance(res, list)


def test_get_reservasi_returns_dict_for_missing(monkeypatch):
    import importlib
    import app
    dummy = DummyMySQL()
    monkeypatch.setattr(app, 'mysql', dummy)
    rm = importlib.reload(importlib.import_module('app.models.reservasi_model'))

    res = rm.get_reservasi(9999)
    assert isinstance(res, dict)
