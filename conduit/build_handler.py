"""
Conduit entrypoint
"""

from typing import Optional
import sys

from .handler import Handler
from .load_config import load_config


def build_handler(config_path: Optional[str]=None) -> Handler:
    """
    Builds the handler
    """

    config = load_config(config_path) if config_path else load_config() 
    
    restart = "--restart" in sys.argv
    gui = "--gui" in sys.argv

    handler = Handler(config, restart, gui)

    return handler