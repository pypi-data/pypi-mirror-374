import argparse
import os
from typing import List

from codestripper.code_stripper import strip_files
from codestripper.utils import FileUtils, set_logger_level, get_working_directory
from codestripper.utils.enums import UnexpectedInputOptions


def add_commandline_arguments(parser: argparse.ArgumentParser) -> None:
    """Add command line arguments"""
    # Add positional arguments
    parser.add_argument("include", nargs="+", help="files to include for code stripping (multiple files or glob)")
    # Add optional arguments
    parser.add_argument("-x", "--exclude", action="append",
                        help="files to include for code stripping (glob)", default=[])
    parser.add_argument("-c", "--comment", action="append",
                        help="comment symbol(s) for the given language, usage: <extension>:<comment> (e.g. .java://")
    parser.add_argument("-v", "--verbosity", action="count", help="increase output verbosity", default=0)
    parser.add_argument("-o", "--output", action="store",
                        help="output directory to store the stripped files", default="out")
    parser.add_argument("-r", "--recursive", action="store_false",
                        help="do NOT use recursive globs for include/exclude")
    parser.add_argument("-d", "--dry-run", action="store_true",
                        help="dry run of the codestripper, no output is written")
    parser.add_argument("-w", "--working-directory", action="store",
                        help="set the working directory for include/exclude", default=os.getcwd())
    parser.add_argument("-e", "--fail-on-error", action="store_false",
                        help="Fail if an error occurs during code stripping")
    parser.add_argument("-b", "--binary", choices=list(UnexpectedInputOptions), default=UnexpectedInputOptions.FAIL,
                        action="store", help="What to do if binary file is matched")
    parser.add_argument("-u", "--unknown", choices=list(UnexpectedInputOptions), default=UnexpectedInputOptions.FAIL,
                        action="store", help="What to do if a file with unknown extension is matched")


def main() -> None:
    """Parse the command line arguments, find all the files and strip the found files"""

    # Handle command line arguments
    parser = argparse.ArgumentParser()
    add_commandline_arguments(parser)
    args = parser.parse_args()

    # Setup the logger
    logger_name = "codestripper"
    set_logger_level(logger_name, args.verbosity)

    # Find the files, based on the command line arguments
    cwd = get_working_directory(args.working_directory)
    files = FileUtils(args.include, args.exclude, cwd, args.recursive, logger_name).get_matching_files()
    # Strip all the files

    strip_files(files, cwd, comments=args.comment, output=args.output, dry_run=args.dry_run,
                fail_on_error=args.fail_on_error)
