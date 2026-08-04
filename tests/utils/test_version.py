import pytest
from mconduit.utils.version import (
    Version, VersionCheck, InvalidVersion, InvalidVersionCheck,
    parse_version, is_new_version
)


def test_parse_semver():

    v = Version.from_string("1.2.3")
    assert v.major == 1
    assert v.minor == 2
    assert v.patch == 3
    assert v.pre_release is None
    assert v.build is None
    
    v2 = Version.from_string("1.2.3-alpha.1+build.123")
    assert v2.pre_release == "alpha.1"
    assert v2.build == "build.123"


def test_parse_mc_releases():

    v = Version.from_string("1.21")
    assert v.major == 1
    assert v.minor == 21
    assert v.patch == 0
    assert not v.is_snapshot

    v2 = Version.from_string("1.20.5 Pre-Release 4")
    assert v2.major == 1
    assert v2.minor == 20
    assert v2.patch == 5
    assert v2.pre_release == "Pre-Release 4"


def test_parse_mc_snapshots():

    v = Version.from_string("22w45a")
    assert v.is_snapshot
    assert v.snapshot_year == 22
    assert v.snapshot_week == 45
    assert v.snapshot_alpha == "a"
    
    v2 = Version.from_string("26.1 Snapshot 1")
    assert v2.is_snapshot
    assert v2.major == 26
    assert v2.minor == 1


def test_version_comparisons():

    # SemVer rules
    assert Version.from_string("1.2.3") < Version.from_string("1.2.4")
    assert Version.from_string("1.2.3") == Version.from_string("1.2.3")
    assert Version.from_string("1.2.3") > Version.from_string("1.2.2")
    
    # Prereleases are strictly considered lower priority than their non-prerelease equivalents
    assert Version.from_string("1.0.0-alpha.0") < Version.from_string("1.0.0")
    assert Version.from_string("1.20.5 Pre-Release 4") < Version.from_string("1.20.5")
    
    # Snapshot comparisons
    assert Version.from_string("22w45a") < Version.from_string("22w46a")


def test_parse_version_backward_compat():

    assert parse_version("1.2.3") == (1, 2, 3)
    assert parse_version("1.21") == (1, 21, 0)


def test_is_new_version():

    assert is_new_version("1.2.3", "1.2.4") is True
    assert is_new_version("1.2.3", "1.2.3") is False
    assert is_new_version("1.2.4", "1.2.3") is False
    

def test_version_check():

    vc1 = VersionCheck.from_string("minecraft>=1.20")

    assert vc1.dependency == "minecraft"
    assert vc1.check_for(Version.from_string("1.21")) is True
    assert vc1.check_for(Version.from_string("1.19")) is False

    vc2 = VersionCheck.from_string("==1.18.2")

    assert vc2.dependency is None
    assert vc2.check_for(Version.from_string("1.18.2")) is True
    assert vc2.check_for(Version.from_string("1.18.3")) is False


def test_version_check_invalid():

    with pytest.raises(InvalidVersionCheck):
        VersionCheck.from_string("invalid_format_without_operator")