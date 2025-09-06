from importlib.metadata import version as get_version
import sys
from typing import cast
import shutil

__version__ = get_version(cast("str", __package__))

DIVIDER = ("=" * shutil.get_terminal_size().columns)

print(
    f"\n{DIVIDER}\n"
    f"PACKAGE DEPRECATED: 'daydream' has been renamed to 'unpage'\n"
    f"{DIVIDER}\n"
    f"This package is no longer maintained.\n\n"
    f"Please uninstall 'daydream' and install 'unpage' instead:\n"
    f"  pip uninstall daydream\n"
    f"  pip install unpage\n\n"
    f"Repository: https://github.com/aptible/unpage\n"
    f"{DIVIDER}"
)

sys.exit(1)
