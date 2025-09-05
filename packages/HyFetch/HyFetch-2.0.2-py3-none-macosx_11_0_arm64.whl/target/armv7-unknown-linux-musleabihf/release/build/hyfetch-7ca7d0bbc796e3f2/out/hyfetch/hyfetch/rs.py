import os
import platform
import subprocess
import sys
from pathlib import Path

from .color_util import printc
from .py import run_py


def run_rust():
    # Find the rust executable
    pd = Path(__file__).parent.joinpath('rust')
    pd = pd.joinpath('hyfetch.exe' if platform.system() == 'Windows' else 'hyfetch')
    if not pd.exists():
        if 'HYFETCH_DONT_WARN_RUST' not in os.environ:
            printc('&cThe executable for hyfetch v2 (rust) is not found, falling back to legacy v1.99.∞ (python).\n'
                   'You can add environment variable HYFETCH_DONT_WARN_RUST=1 to suppress this warning.\n')
        run_py()
        return

    # Run the rust executable, passing in all arguments
    subprocess.run([str(pd)] + sys.argv[1:])


if __name__ == '__main__':
    run_rust()
