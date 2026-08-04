import pytest
import yaml
from mconduit.lang.lang import Lang


@pytest.fixture
def temp_lang_env(tmp_path):

    lang_file = tmp_path / "en_us.yml"
    data = {
        "hello": "Hello World",
        "{player} joined the game": "Look out, {player} has joined the game!"
    }

    with open(lang_file, "w") as f:
        yaml.safe_dump(data, f)

    return tmp_path


def test_lang_loading_and_exact_match(temp_lang_env):

    l = Lang(temp_lang_env, "en_us")

    assert l["hello"] == "Hello World"


def test_lang_regex_formatting(temp_lang_env):

    l = Lang(temp_lang_env, "en_us")
    result = l["Steve joined the game"]

    assert result == "Look out, Steve has joined the game!"


def test_lang_fallback(temp_lang_env):

    l = Lang(temp_lang_env, "en_us")

    assert l["Non existent key"] == "Non existent key"