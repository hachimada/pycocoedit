import re
from pathlib import Path

import pytest
import toml

# Compile regex to match X.Y.Z or X.Y.ZrcW
SEMVER_OR_RC_RE: re.Pattern[str] = re.compile(
    r"^(0|[1-9]\d*)"  # X
    r"\.(0|[1-9]\d*)"  # .Y
    r"\.(0|[1-9]\d*)"  # .Z
    r"(?:rc(0|[1-9]\d*))?$"  # optional rcW
)


@pytest.fixture(scope="session")
def project_version() -> str:
    """
    Return version defined in *pyproject.toml*.

    Returns
    -------
    str
        Version string under ``tool.poetry.version``.
    """
    project_root: Path = Path(__file__).resolve().parents[1]
    pyproject: dict = toml.load(project_root / "pyproject.toml")
    return pyproject["tool"]["poetry"]["version"]


def test_version_format(project_version: str) -> None:
    """
    Validate that the project version matches ``X.Y.Z`` or ``X.Y.ZrcW``.

    Parameters
    ----------
    project_version : str
        Version string provided by fixture.
    """
    assert SEMVER_OR_RC_RE.fullmatch(project_version), (
        f"Invalid version '{project_version}'. " "Use 'X.Y.Z' or 'X.Y.ZrcW' without a leading 'v'."
    )


# ----------------------------------------------------------------------
# Unit tests for the regex itself


@pytest.mark.parametrize(
    "version",
    [
        "0.0.0",
        "1.2.3",
        "10.20.30",
        "1.2.3rc1",
        "0.0.1rc10",
    ],
)
def test_regex_accepts_valid(version: str) -> None:
    """
    Ensure the regex accepts valid versions.

    Parameters
    ----------
    version : str
        Candidate version string expected to match.
    """
    assert SEMVER_OR_RC_RE.fullmatch(version) is not None, version


@pytest.mark.parametrize(
    "version",
    [
        "v1.2.3",
        "1.2",
        "1.2.3rc",
        "1.2.3rc01",
        "01.2.3",
        "1.2.3dev1",
        "1.2.3.post1",
        "1.2.3b1",
        "1.2.3rc-1",
    ],
)
def test_regex_rejects_invalid(version: str) -> None:
    """
    Ensure the regex rejects invalid versions.

    Parameters
    ----------
    version : str
        Candidate version string expected *not* to match.
    """
    assert SEMVER_OR_RC_RE.fullmatch(version) is None, version
