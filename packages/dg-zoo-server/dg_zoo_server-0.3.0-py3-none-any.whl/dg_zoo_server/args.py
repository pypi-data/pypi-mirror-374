#
# args.py - DeGirum Zoo Server: command line argument parsing
# Copyright DeGirum Corp. 2024
#
# Contains DeGirum Zoo Server command line argument parsing implementation
#

import argparse
from typing import Optional

# default zoo root directory
_zoo_root_default = "./zoo"

# Global variable to store parsed command line arguments
_args: Optional[argparse.Namespace] = None


def get_args(args_str: Optional[str] = None) -> argparse.Namespace:
    """Parse command line arguments and return them

    Args:
        args_str (str, optional): Command line arguments string. Defaults to None. If None, sys.argv is used.

    Returns:
        argparse.Namespace: Parsed command line arguments
    """

    global _args
    if _args is not None:

        if args_str is not None:
            raise ValueError("get_args() can be called with args_str only once")
        return _args

    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Start DeGirum local zoo server.")
    parser.add_argument(
        "--port",
        type=int,
        default=8878,
        help="Port number to run the server on (default: 8878)",
    )
    parser.add_argument(
        "--zoo",
        type=str,
        default=_zoo_root_default,
        help=f"Zoo root directory (default: {_zoo_root_default})",
    )
    parser.add_argument(
        "--reload", action="store_true", help="Autoreload server sources on change"
    )

    _args, _ = parser.parse_known_args(args=args_str.split() if args_str else None)

    return _args
