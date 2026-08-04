from mconduit.utils.errors import ConduitError, get_last_error


def test_conduit_error_from_exception():

    try:
        1 / 0
    except Exception as e:

        err = ConduitError.from_exception(e)

        assert err.name == "ZeroDivisionError"
        assert err.info == "division by zero"
        assert err.traceback is not None
        assert err.traceback["function"] == "test_conduit_error_from_exception"


def test_conduit_error_equality():

    err1 = ConduitError("TestError", None, None, None)
    err2 = ConduitError("TestError", None, None, None)
    err3 = ConduitError("OtherError", None, None, None)
    
    assert err1 == err2
    assert err1 != err3
    assert err1 != "NotAnError"


def test_conduit_error_to_text():

    err = ConduitError("TestError", "An info", "Some docs", {
        "file": "test.py",
        "function": "main",
        "line": 42,
        "code": "print('hello')"
    })
    text_obj = err.to_text()

    assert text_obj is not None


def test_get_last_error():

    try:
        raise ValueError("Oops")

    except ValueError:
        
        err = get_last_error()
        
        assert err is not None
        assert err.name == "ValueError"
        assert err.info == "Oops"
        assert err.traceback["function"] == "test_get_last_error"

    assert get_last_error() is None