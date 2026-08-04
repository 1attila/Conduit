import pytest
import yaml
from pathlib import Path
from mconduit.lang.syncer import LangSyncer


@pytest.fixture
def mock_env(tmp_path):
    
    lang_dir = tmp_path / "resources"
    code_dir = tmp_path / "code"
    lang_dir.mkdir()
    code_dir.mkdir()

    # Pre-existing file
    with open(lang_dir / "en_us.yml", "w") as f:
        yaml.safe_dump({"existing_key": "Existing Translation"}, f)

    # Dummy Code triggering regex matches
    with open(code_dir / "main.py", "w") as f:
        f.write('self.lang["test.new_translation"]\n')
        f.write('l["another_translation"]\n')

    return tmp_path, lang_dir, code_dir


def test_lang_syncer(mock_env):

    _, lang_dir, code_dir = mock_env
    syncer = LangSyncer(lang_dir, code_dir)
    syncer.run()

    with open(lang_dir / "en_us.yml", "r") as f:
        synced_lang = yaml.safe_load(f)

    # Validate that it persisted it to file
    assert "existing_key" in synced_lang
    assert "test.new_translation" in synced_lang
    assert synced_lang["another_translation"] == "another_translation"