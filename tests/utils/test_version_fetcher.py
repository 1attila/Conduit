import pytest
from unittest.mock import MagicMock, patch
from mconduit.utils.version_fetcher import (
    fetch_vanilla_versions, fetch_fabric_versions, fetch_vanilla_url,
    download_server_jar, agree_eula, generate_server_properties,
    fetch_server_type, VersionFetcher, UnableToFetchVersion
)


@patch("mconduit.utils.version_fetcher.requests.get")
def test_fetch_vanilla_versions(mock_get):

    mock_resp = MagicMock()
    mock_resp.json.return_value = {"versions": [{"id": "1.20", "type": "release", "url": "url1"}]}
    mock_get.return_value = mock_resp
    
    assert fetch_vanilla_versions() == ["1.20"]
    assert fetch_vanilla_versions(include_url=True) == {"1.20": "url1"}


@patch("mconduit.utils.version_fetcher.requests.get")
def test_fetch_fabric_versions(mock_get):

    def side_effect(url, **kwargs):

        mock_resp = MagicMock()
        if "game" in url: mock_resp.json.return_value = [{"version": "1.20", "stable": True}]
        elif "loader" in url: mock_resp.json.return_value = [{"version": "0.14.21", "stable": True}]
        elif "installer" in url: mock_resp.json.return_value = [{"version": "0.11.2", "stable": True}]
        return mock_resp
        
    mock_get.side_effect = side_effect
    assert fetch_fabric_versions() == ["1.20"]


@patch("mconduit.utils.version_fetcher.requests.get")
@patch("mconduit.utils.version_fetcher.NamedTemporaryFile")
@patch("mconduit.utils.version_fetcher.Path")

def test_download_server_jar(mock_path, mock_tempfile, mock_get):

    mock_resp = MagicMock()
    mock_resp.iter_content.return_value = [b"chunk1", b"chunk2"]
    mock_get.return_value.__enter__.return_value = mock_resp
    
    mock_temp = MagicMock()
    mock_tempfile.return_value = mock_temp
    
    download_server_jar("url", "folder")
    assert mock_temp.write.call_count == 2


def test_agree_eula(tmp_path):

    agree_eula(tmp_path)
    assert "eula=true" in (tmp_path / "eula.txt").read_text()


def test_fetch_server_type(tmp_path):

    (tmp_path / "paper.yml").touch()
    assert fetch_server_type(tmp_path) == "Paper"
    (tmp_path / "paper.yml").unlink()

    (tmp_path / "fabric-server-launcher.properties").touch()
    assert fetch_server_type(tmp_path) == "Fabric"


def test_version_fetcher_is_v1_21_5():

    mock_server = MagicMock()
    mock_server.execute.return_value = '{"text": "success"}'
    assert VersionFetcher.is_v1_21_5(mock_server) is True
    
    mock_server.execute.return_value = None

    with pytest.raises(UnableToFetchVersion):
        VersionFetcher.is_v1_21_5(mock_server)


def test_version_fetcher_check_version():

    mock_server = MagicMock()
    
    def exec_side_effect(commands):
        return ["No player was found" if "cherry_log" in c else "Unknown item" for c in commands]
        
    mock_server.execute.side_effect = exec_side_effect
    assert VersionFetcher.check_version(mock_server) == "1.20"