"""
Conduit entrypoint
"""

import sys
import os

# Bad hack to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from main import main as _main

except ModuleNotFoundError:

    from mconduit import build_handler

    def _main():
        build_handler()


def main():
    """
    Runs the user main function 
    """

    _main()


if __name__ == "__main__":
    main()