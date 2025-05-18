from pathlib import Path

import toml  # type: ignore[import-untyped]


def test_get_version():
    """
    Test if the code in release.yml works as expected.
    """
    from_root = Path(__file__).parent.parent
    toml_file = str(from_root / "pyproject.toml")
    version = toml.load(toml_file)["tool"]["poetry"]["version"]
    assert isinstance(
        version, str
    ), 'toml.load(\'pyproject.toml\')["tool"]["poetry"]["version"] is used in .github/workflows/release.yml. You may need to update it.'
