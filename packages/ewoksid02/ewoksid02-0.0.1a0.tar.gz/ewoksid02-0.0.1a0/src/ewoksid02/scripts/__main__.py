import argparse
import os
import shutil
import sys

from ..utils import AVAILABLE_TEMPLATES, TEMPLATE_MESSAGE
from .parsers import add_saxs_arguments, add_xpcs_arguments
from .saxs.main import main as main_saxs
from .xpcs.__main__ import main as main_xpcs

TECHNIQUES = [
    "saxs",
    "xpcs",
]


def main(argv=None):
    """Main function to run the offline scripts

    Inputs:
        - argv: command line arguments
    """
    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(
        prog="ewoksid02",
        description="Run data processing pipelines for SAXS or XPCS.",
        usage="ewoksid02 {saxs | xpcs | templates} [...]",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparser_saxs = subparsers.add_parser("saxs", help="Trigger SAXS pipelines")
    add_saxs_arguments(subparser_saxs)

    subparser_xpcs = subparsers.add_parser("xpcs", help="Trigger XPCS pipelines")
    add_xpcs_arguments(subparser_xpcs)

    subparser_templates = subparsers.add_parser(  # noqa
        "templates", help="Download available templates for ID02 offline pipelines"
    )

    if len(argv) == 1:
        parser.print_help()
        sys.exit(1)

    if argv[1] == "templates":
        print(TEMPLATE_MESSAGE)
        for _, template_info in AVAILABLE_TEMPLATES.items():
            os.makedirs(template_info["directory"], exist_ok=True)
            shutil.copy(template_info["path"], template_info["future_path"])
        return

    args = parser.parse_args(argv[1:])
    if args.command == "saxs":
        if len(args.FILES) == 0:
            subparser_saxs.print_help()
            sys.exit(1)
        main_saxs(args)
    elif args.command == "xpcs":
        main_xpcs(args)
    elif args.command == "templates":
        print(TEMPLATE_MESSAGE)
        for _, template_info in AVAILABLE_TEMPLATES.items():
            os.makedirs(template_info["directory"], exist_ok=True)
            shutil.copy(template_info["path"], template_info["future_path"])
        return
    else:
        parser.print_help()
        sys.exit(1)
