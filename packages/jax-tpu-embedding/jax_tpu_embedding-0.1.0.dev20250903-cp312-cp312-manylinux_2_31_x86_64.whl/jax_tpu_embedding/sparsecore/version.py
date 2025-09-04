"""JAX TPU Embedding versioning utilities

For releases, the version is of the form:
  xx.yy.zz

For nightly builds, the date of the build is added:
  xx.yy.zz-devYYYMMDD
"""

_base_version = "0.1.0"
_version_suffix = "dev20250903"

# Git commit corresponding to the build, if available.
__git_commit__ = "d37c01be15c7f2885f42c4d8746b07e0b4b90cb1"

# Library version.
__version__ = _base_version + _version_suffix

