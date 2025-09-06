from confixer.merge import deep_merge


def test_deep_merge_nested_dicts():
    a = {"db": {"host": "localhost", "port": 5432}, "debug": False}
    b = {"db": {"port": 5433}, "debug": True}

    result = deep_merge(a, b)

    assert result["db"]["host"] == "localhost"  # kept from a
    assert result["db"]["port"] == 5433  # overridden by b
    assert result["debug"] is True  # overridden by b


def test_deep_merge_lists_replace():
    a = {"items": [1, 2, 3]}
    b = {"items": [4, 5]}
    result = deep_merge(a, b)

    assert result["items"] == [4, 5]  # list replaced, not merged
