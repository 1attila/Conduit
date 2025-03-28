"""
Conduit entrypoint
"""

import sys
import os

# Bad hack to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import main as _main


def main():
    """
    Runs the user main function 
    """

    _main()


if __name__ == "__main__":
    main()