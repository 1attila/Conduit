from unittest.mock import MagicMock, patch
from mconduit.utils.rcon import Rcon
import rcon


@patch("mconduit.utils.rcon.rcon.Client")
def test_rcon_execute_single(mock_client_cls):

    mock_client = MagicMock()
    mock_client_cls.return_value.__enter__.return_value = mock_client
    mock_client.run.return_value = "Player list"
    
    r = Rcon("127.0.0.1", 25575, "pass")

    assert r.execute("list") == "Player list"
    mock_client.run.assert_called_once_with("list")


@patch("mconduit.utils.rcon.rcon.Client")
def test_rcon_execute_multiple(mock_client_cls):

    mock_client = MagicMock()
    mock_client_cls.return_value.__enter__.return_value = mock_client
    mock_client.run.side_effect = ["Output1", "Output2"]
    
    r = Rcon("127.0.0.1", 25575, "pass")

    assert r.execute(["cmd1", "cmd2"]) == ["Output1", "Output2"]
    assert mock_client.run.call_count == 2


@patch("mconduit.utils.rcon.rcon.Client")
def test_rcon_all_at_once(mock_client_cls):

    mock_client = MagicMock()
    mock_client_cls.return_value.__enter__.return_value = mock_client
    
    r = Rcon("127.0.0.1", 25575, "pass")

    with r.all_at_once():

        r.execute("cmd1")
        r("cmd2")
        r.execute(["cmd3", "cmd4"])
        mock_client.run.assert_not_called()
    
    assert mock_client.run.call_count == 4


@patch("mconduit.utils.rcon.rcon.Client")
def test_rcon_timeout(mock_client_cls):

    mock_client_cls.return_value.__enter__.side_effect = rcon.SessionTimeout("Timeout")
    r = Rcon("127.0.0.1", 25575, "pass")

    assert r.execute("list") == ""


@patch("mconduit.utils.rcon.rcon.Client", side_effect=Exception("General error"))
@patch("mconduit.utils.rcon.logger.error")
def test_rcon_general_exception(mock_log, mock_client_cls):

    r = Rcon("127.0.0.1", 25575, "pass", log_errors=True)

    assert r.execute("fail") == ""
    assert mock_log.call_count == 2