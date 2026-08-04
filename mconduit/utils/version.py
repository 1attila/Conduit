from typing import Callable, Optional, Tuple
import functools
import re


SEMVER_PATTERN = re.compile(
    r"^(?P<major>\d+)\.(?P<minor>\d+)(?:\.(?P<patch>\d+))?"
    r"(?:-(?P<prerelease>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+(?P<build>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)

MC_RELEASE_PATTERN = re.compile(
    r"^(?P<major>\d+)\.(?P<minor>\d+)(?:\.(?P<patch>\d+))?"
    r"(?: (?P<prerelease>(?:Pre-Release|Release Candidate) \d+))?$", 
    re.IGNORECASE
)

MC_SNAPSHOT_PATTERN = re.compile(
    r"^(?P<year>\d+)w(?P<week>\d+)(?P<alpha>[a-z])$", 
    re.IGNORECASE
)

MC_OLD_SNAPSHOT_PATTERN = re.compile(
    r"^(?P<major>\d+)(\.(?P<minor>\d+)(\.(?P<patch>\d+))?)? Snapshot (?P<num>\d+)$", 
    re.IGNORECASE
)

VERSION_CHECK_PATTERN = re.compile(
    r"^(?P<dependency>[a-zA-Z0-9\-_.]*)(?P<operator>>=|<=|==|!=|~=|===|>|<)(?P<version>.*)$"
)


class InvalidVersion(Exception):
    ...

class InvalidVersionCheck(Exception):
    ...


def parse_version(version: str) -> Tuple[int, int, int]:
    """
    Splits a version string into a tuple (major, minor, patch).

    E.g: '1.2.3' -> (1, 2, 3)
    """

    return Version.from_string(version).as_tuple()

    
def is_new_version(v1: str, v2: str) -> bool:
    """
    Returns True if v2 is newer than v1, False otherwise
    """

    try:
        return Version.from_string(v2) > Version.from_string(v1)
    
    except InvalidVersion:
        return False


@functools.total_ordering
class Version:
    """
    Utility class that represents a version following sem-ver and Minecraft conventions.

    Useful to make checks
    """

    major: int
    minor: int
    patch: int
    pre_release: Optional[str]
    build: Optional[str]
    is_snapshot: bool
    snapshot_year: Optional[int]
    snapshot_week: Optional[int]
    snapshot_alpha: Optional[str]
    snapshot_num: Optional[int]


    def __init__(
        self,
        major: int = 0,
        minor: int = 0,
        patch: int = 0,
        pre_release: Optional[str] = None,
        build: Optional[str] = None,
        is_snapshot: bool = False,
        snapshot_year: Optional[int] = None,
        snapshot_week: Optional[int] = None,
        snapshot_alpha: Optional[str] = None,
        snapshot_num: Optional[int] = None
    ) -> None:
        
        self.major = major
        self.minor = minor
        self.patch = patch

        self.pre_release = pre_release
        self.build = build
        self.is_snapshot = is_snapshot

        self.snapshot_year = snapshot_year
        self.snapshot_week = snapshot_week
        self.snapshot_alpha = snapshot_alpha
        self.snapshot_num = snapshot_num


    @classmethod
    def from_string(cls, string: str) -> "Version":

        string = string.strip()

        if string.endswith(" Unobfuscated"):
            string = string[:-13]

        m = MC_SNAPSHOT_PATTERN.fullmatch(string)

        if m:
            return cls(
                is_snapshot = True,
                snapshot_year = int(m.group("year")),
                snapshot_week = int(m.group("week")),
                snapshot_alpha = m.group("alpha").lower()
            )
        
        m = MC_OLD_SNAPSHOT_PATTERN.fullmatch(string)

        if m:
            return cls(
                major = int(m.group("major")),
                minor = int(m.group("minor") or 0),
                patch = int(m.group("patch") or 0),
                is_snapshot = True,
                snapshot_num = int(m.group("num"))
            )

        m = MC_RELEASE_PATTERN.fullmatch(string)

        if m:
            return cls(
                major = int(m.group("major")),
                minor = int(m.group("minor") or 0),
                patch = int(m.group("patch") or 0),
                pre_release = m.group("prerelease")
            )
        
        m = SEMVER_PATTERN.fullmatch(string)

        if m:
            return cls(
                major = int(m.group("major")),
                minor = int(m.group("minor") or 0),
                patch = int(m.group("patch") or 0),
                pre_release = m.group("prerelease"),
                build = m.group("build")
            )
        
        raise InvalidVersion(f"Expected valid version, found: {string}")


    def as_tuple(self) -> Tuple[int, int, int]:
        return self.major, self.minor, self.patch
    

    def _get_pre_release_key(self) -> Tuple[int, Tuple]:

        if self.pre_release is None:
            return (1, ())

        parts = self.pre_release.replace(" ", ".").split(".")
        parsed_parts = []

        for part in parts:

            if part.isdigit():
                parsed_parts.append((0, int(part)))

        return (0, tuple(parsed_parts))
    

    def _cmp_key(self) -> Tuple:

        if self.is_snapshot:

            return (
                1,
                self.snapshot_year or 0,
                self.snapshot_week or 0,
                self.snapshot_alpha or "",
                self.major,
                self.minor,
                self.patch,
                self.snapshot_num or 0
            )

        return (
            2,
            self.major,
            self.minor,
            self.patch,
            self._get_pre_release_key()
        )


    def __eq__(self, other: object) -> bool:

        if isinstance(other, Version):
            return self._cmp_key() == other._cmp_key()
        
        if isinstance(other, str):
            return self == Version.from_string(other)

        raise NotImplementedError
    

    def __lt__(self, other: object) -> bool:

        if isinstance(other, Version):
            return self._cmp_key() < other._cmp_key()
        
        if isinstance(other, str):
            return self < Version.from_string(other)
        
        raise NotImplementedError


    def __gt__(self, other: object) -> bool:

        if isinstance(other, Version):
            return self._cmp_key() > other._cmp_key()
        
        if isinstance(other, str):
            return self > Version.from_string(other)
        
        raise NotImplementedError
    

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


class VersionCheck:
    """
    Represents a string containing versioning data.

    Format: `<dependency-name>?<comparison-operator><version>`

    E.g: "minecraft>=1.13" or "==1.21"
    """

    dependency: Optional[str]
    version: Version
    comparison: str
    _comparison_fn: Callable[[Version, Version], bool]
    

    def __init__(
        self,
        dependency: Optional[str],
        version: Version,
        comparison: str
    ) -> None:
        
        self.dependency = dependency
        self.version = version
        self.comparison = comparison
        
        self._parse_comparison(comparison)

    
    def _parse_comparison(self, comparison: str) -> None:

        match comparison:

            case ">":
                self._comparison_fn = lambda v_req, v_given: v_given > v_req # type: ignore

            case "<":
                self._comparison_fn = lambda v_req, v_given: v_given < v_req # type: ignore

            case ">=":
                self._comparison_fn = lambda v_req, v_given: v_given >= v_req # type: ignore

            case "<=":
                self._comparison_fn = lambda v_req, v_given: v_given <= v_req # type: ignore

            case "==":
                self._comparison_fn = lambda v_req, v_given: v_given == v_req # type: ignore

            case "~=":
                self._comparison_fn = lambda v_req, v_given: v_given != v_req # type: ignore

            case "!=":
                self._comparison_fn = lambda v_req, v_given: v_given != v_req # type: ignore

            case _:
                raise ValueError("Invalid operator for comparison")


    @classmethod
    def from_string(cls, string: str) -> "VersionCheck":

        string = string.replace(" ", "")
        parsed = re.match(VERSION_CHECK_PATTERN, string)

        if parsed is None:
            raise InvalidVersionCheck(f"Expected <dependency-name>?<comparison-operator><version>, found {string}")

        dependency = parsed.group("dependency")

        if not dependency:
            dependency = None
        
        comparison = parsed.group("operator")
        version = Version.from_string(parsed.group("version"))

        return cls(
            dependency,
            version,
            comparison # type: ignore
        )


    def check_for(self, other: Version) -> bool:
        return self._comparison_fn(self.version, other)