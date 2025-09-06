import pytest
import yaml
import json
import tomli
from confixer.sources.base import ConfigSource
from confixer.sources.yaml_source import YamlSource
from confixer.sources.json_source import JsonSource
from confixer.sources.toml_source import TomlSource
from confixer.sources.env_source import EnvSource


class DummySource(ConfigSource):
    def load(self):
        return {"a": 1, "b": {"c": 2}}


def test_dummy_source_load():
    source = DummySource()
    data = source.load()
    assert data["a"] == 1
    assert data["b"]["c"] == 2


def test_load_valid_yaml(tmp_path):
    data = {"key": "value", "nested": {"a": 1}}
    file_path = tmp_path / "config.yaml"
    file_path.write_text(yaml.dump(data), encoding="utf-8")

    source = YamlSource(str(file_path))
    loaded = source.load()
    assert loaded == data


def test_load_invalid_yaml(tmp_path):
    invalid_yaml = "key: value\n: invalid"
    file_path = tmp_path / "invalid.yaml"
    file_path.write_text(invalid_yaml, encoding="utf-8")

    source = YamlSource(str(file_path))
    with pytest.raises(yaml.YAMLError):
        source.load()


def test_load_non_dict_root(tmp_path):
    yaml_data = ["item1", "item2"]
    file_path = tmp_path / "list_root.yaml"
    file_path.write_text(yaml.dump(yaml_data), encoding="utf-8")

    source = YamlSource(str(file_path))
    with pytest.raises(ValueError, match="YAML root must be a dict"):
        source.load()


def test_load_empty_yaml(tmp_path):
    file_path = tmp_path / "empty.yaml"
    file_path.write_text("", encoding="utf-8")

    source = YamlSource(str(file_path))
    with pytest.raises(ValueError, match="YAML root must be a dict"):
        source.load()


def test_load_valid_json(tmp_path):
    data = {"key": "value", "nested": {"a": 1}}
    file_path = tmp_path / "config.json"
    file_path.write_text(json.dumps(data), encoding="utf-8")

    source = JsonSource(str(file_path))
    loaded = source.load()
    assert loaded == data


def test_load_invalid_json(tmp_path):
    invalid_json = '{"key": "value", invalid}'
    file_path = tmp_path / "invalid.json"
    file_path.write_text(invalid_json, encoding="utf-8")

    source = JsonSource(str(file_path))
    with pytest.raises(json.JSONDecodeError):
        source.load()


def test_load_non_dict_root_json(tmp_path):
    json_data = ["item1", "item2"]  # list instead of dict
    file_path = tmp_path / "list_root.json"
    file_path.write_text(json.dumps(json_data), encoding="utf-8")

    source = JsonSource(str(file_path))
    with pytest.raises(ValueError, match="JSON root must be a dict"):
        source.load()


def test_load_empty_json(tmp_path):
    file_path = tmp_path / "empty.json"
    file_path.write_text("", encoding="utf-8")  # empty file

    source = JsonSource(str(file_path))
    with pytest.raises(json.JSONDecodeError):
        source.load()


def test_load_valid_toml(tmp_path):
    data = {"key": "value", "nested": {"a": 1}}
    file_path = tmp_path / "config.toml"
    file_path.write_text('key = "value"\n[nested]\na = 1\n', encoding="utf-8")

    source = TomlSource(str(file_path))
    loaded = source.load()
    assert loaded == data


def test_load_invalid_toml(tmp_path):
    invalid_toml = "key = 'value'\n= invalid"
    file_path = tmp_path / "invalid.toml"
    file_path.write_text(invalid_toml, encoding="utf-8")

    source = TomlSource(str(file_path))
    with pytest.raises(tomli.TOMLDecodeError):
        source.load()


def test_load_non_dict_root_toml(tmp_path):
    toml_data = "array = [1, 2, 3]"
    file_path = tmp_path / "array.toml"
    file_path.write_text(toml_data, encoding="utf-8")

    source = TomlSource(str(file_path))
    loaded = source.load()
    assert isinstance(loaded, dict)


def test_load_empty_toml(tmp_path):
    file_path = tmp_path / "empty.toml"
    file_path.write_text("", encoding="utf-8")

    source = TomlSource(str(file_path))
    loaded = source.load()
    assert loaded == {}


def test_envsource_load_from_os(monkeypatch):
    monkeypatch.setenv("FOO", "bar")
    source = EnvSource()
    data = source.load()
    assert "FOO" in data
    assert data["FOO"] == "bar"


def test_envsource_load_from_dotenv(tmp_path, monkeypatch):
    # Clear FOO if it exists in real environment
    monkeypatch.delenv("FOO", raising=False)

    env_file = tmp_path / ".env"
    env_file.write_text("FOO=from_file\nBAR=123\nEMPTY=\n", encoding="utf-8")

    source = EnvSource(path=str(env_file))
    data = source.load()

    assert data["FOO"] == "from_file"
    assert data["BAR"] == 123  # Type coerced to int
    # EMPTY should be dropped because dotenv returns None
    assert "EMPTY" not in data


def test_envsource_with_prefix(monkeypatch):
    monkeypatch.setenv("APP_HOST", "localhost")
    monkeypatch.setenv("APP_PORT", "8080")
    monkeypatch.setenv("OTHER", "ignore_me")

    source = EnvSource(prefix="APP_")
    data = source.load()

    # Prefix should be stripped, PORT coerced to int
    assert data == {"HOST": "localhost", "PORT": 8080}
    assert "OTHER" not in data


def test_envsource_empty(monkeypatch):
    monkeypatch.setenv("SHOULD_STAY", "yes")
    source = EnvSource(prefix="NONE_")  # no match
    data = source.load()
    assert data == {}
