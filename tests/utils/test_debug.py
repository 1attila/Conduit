from unittest.mock import MagicMock, patch
from mconduit.utils.debug import debug, debug_plg, create_plg_debug


@patch("mconduit.utils.debug.inspect.getframeinfo")
def test_debug(mock_getframeinfo):
    
    mock_context = MagicMock()
    mock_context.code_context = ["debug(my_var)\n"]
    mock_getframeinfo.return_value = mock_context

    print_mock = MagicMock()
    debug(42, print=print_mock)
    
    print_mock.assert_called_once()
    assert "my_var" in str(print_mock.call_args[0][0])
    assert "42" in str(print_mock.call_args[0][0])


@patch("mconduit.utils.debug.inspect.getframeinfo")
def test_debug_plg(mock_getframeinfo):

    mock_context = MagicMock()
    mock_context.code_context = ["debug_plg(test_var)\n"]
    mock_getframeinfo.return_value = mock_context

    mock_plugin = MagicMock()
    mock_plugin.server.name = "TestServer"
    mock_plugin.name = "TestPlugin"
    mock_plugin.debug_plg = create_plg_debug(mock_plugin)
    
    mock_plugin.debug_plg("hello")
    mock_plugin.server.handler.cli.out.assert_called_once()
    assert "test_var" in str(mock_plugin.server.handler.cli.out.call_args[0][0].plain_text)


@patch("mconduit.utils.debug.debug_plg")
def test_create_plg_debug(mock_debug_plg):

    mock_plugin = MagicMock()
    debug_fn = create_plg_debug(mock_plugin)
    
    debug_fn("test")
    mock_debug_plg.assert_called_once_with(mock_plugin, "test")