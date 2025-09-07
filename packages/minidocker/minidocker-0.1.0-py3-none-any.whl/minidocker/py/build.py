import pathlib
import sys

from . import _build_for_pkg, _build_for_proj


if __name__ == "__main__":
    if pathlib.Path("docker").is_dir():
        _build_for_proj.build(sys.argv[1:])
    else:
        _build_for_pkg.build(sys.argv[1:])
