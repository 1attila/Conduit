import pytest
from mconduit.enums.at import At


def test_selector_generation():

    sel = At.SELF.distance(5).limit(1)
    assert str(sel) == "@s[distance=5, limit=1]"


def test_selector_immutability():

    sel1 = At.ALL_PLAYERS.distance(10)
    sel2 = At.ALL_PLAYERS.limit(5)
    
    # Check that they didn't mutate the base class
    assert str(At.ALL_PLAYERS) == "@a"
    assert "limit" not in sel1.selectors
    assert "distance" not in sel2.selectors


def test_selector_complex():
    
    sel = At.ALL_ENTITIES.scores({"health": "10..", "kills": "5"}).nbt({"OnGround": 1})
    assert str(sel) == '@e[scores={health=10..,kills=5}, nbt={"OnGround": 1}]'