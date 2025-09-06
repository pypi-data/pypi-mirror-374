import pytest
from confixer.accessor import DotConfig


def test_dot_access_read():
    cfg = DotConfig({"db": {"host": "localhost", "port": 5432}})
    assert cfg.db.host == "localhost"
    assert cfg.db.port == 5432


def test_dot_access_write():
    cfg = DotConfig()
    cfg.api = {"key": "secret"}
    assert isinstance(cfg.api, DotConfig)
    assert cfg.api.key == "secret"


def test_key_error_raises_attribute_error():
    cfg = DotConfig()
    with pytest.raises(AttributeError):
        _ = cfg.missing
