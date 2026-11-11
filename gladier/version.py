from importlib.metadata import PackageNotFoundError, version

try:
    # Derived from the git tag at build/install time by setuptools-scm (see pyproject.toml)
    __version__ = version("gladier")
except PackageNotFoundError:  # pragma: no cover
    # Running from a source tree which has not been installed
    __version__ = "0.0.0+unknown"
