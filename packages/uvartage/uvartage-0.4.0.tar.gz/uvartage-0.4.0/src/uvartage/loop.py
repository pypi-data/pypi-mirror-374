# -*- coding: utf-8 -*-

"""uvartage cmd loop implementation"""

import logging

from argparse import ArgumentParser, Namespace, REMAINDER
from cmd import Cmd
from dataclasses import dataclass
from fnmatch import filter as fnmatch_filter
from os import chdir, getcwd
from pathlib import Path
from re import IGNORECASE, compile as re_compile
from shlex import split
from subprocess import CalledProcessError
from sys import stderr

from .backends import PIP, PYTHON, UV, BackendBase, SupportedBackendType, get_backend
from .commons import (
    EMPTY,
    UTF_8,
    complete_paths,
    get_prompt,
    iter_paths_list,
    log_multiline,
)


ID_PATTERN = "[a-z][_a-z0-9]*"

PRX_VARIABLE_ASSIGNMENT = re_compile(
    rf"\A(?P<key>{ID_PATTERN})=(?P<value>.*)\Z",
    IGNORECASE,
)
PRX_VARIABLE_NAME = re_compile(rf"\A{ID_PATTERN}\Z", IGNORECASE)

_PYTHONPATH = "PYTHONPATH"


def confirmed(prompt: str) -> bool:
    """Ask for confirmation"""
    prompt = f"{prompt} (y/n)? "
    while True:
        answer = input(prompt).strip().lower()
        if not answer:
            continue
        #
        if "yes".startswith(answer):
            return True
        #
        if "no".startswith(answer):
            return False
        #
        prompt = "Please answer yes or no: "
    #


class OptionError(Exception):
    """Raised if the OptionParser would exit"""


@dataclass
class Availability:
    """Programs availability"""

    backend: BackendBase
    git: str | None = None
    pip: str | None = None
    uv: str | None = None

    def __post_init__(self):
        """Find out program versions"""
        if self.git is None:
            self.git = self.get_stripped_output("git", "--version")
        #
        if self.pip is None:
            self.pip = self.get_stripped_output(PYTHON, "-m", "pip", "--version")
        #
        if self.pip is None:
            self.get_stripped_output(PYTHON, "-m", "ensurepip")
            self.pip = self.get_stripped_output(PYTHON, "-m", "pip", "--version")
        #
        if self.uv is None:
            self.uv = self.get_stripped_output("uv", "self", "version")
        #
        if self.uv is None and confirmed(
            "uv does not seem to be installed. Install now using pip"
        ):
            self.get_stripped_output(PYTHON, "-m", "pip", "install", "uv")
            self.uv = self.get_stripped_output("uv", "self", "version")
        #

    def get_stripped_output(self, *command: str) -> str | None:
        """Return the stripped command output, or None in case of an error"""
        try:
            captured_stdout = self.backend.execute(
                *command, capture_output=True, check=True
            ).stdout
        except CalledProcessError:
            return None
        #
        if isinstance(captured_stdout, bytes):
            return captured_stdout.decode(UTF_8).strip()
        #
        if isinstance(captured_stdout, str):
            return captured_stdout.strip()
        #
        raise TypeError(f"Unexpected return value: {captured_stdout!r}")

    def show_versions(self) -> None:
        """Show versions"""
        python_version = self.get_stripped_output(PYTHON, "--version")
        logging.info("%s (executable is %s)", python_version, PYTHON)
        logging.info(" * %s", self.pip or "no pip")
        logging.info(" * %s", self.uv or "no uv")
        logging.info(self.git or "no git")


class DefusedArgumentParser(ArgumentParser):
    """Defused argument parser not exiting the whoöe loop on wrong options"""

    msg_secret_value = "Secret values must be entered through hidden input"

    def exit(self, status=0, message=None):
        """Do not exit the program, raise an OptionError instead"""
        if message:
            stderr.write(message)
        #
        raise OptionError(status)

    @classmethod
    def get_list_arguments(cls, arg: str) -> Namespace:
        """Return parsed arguments for the list command"""
        parser = cls(prog="list", description="Print directory contents")
        parser.add_argument(
            "-l",
            "--long",
            action="store_true",
            help="long format (including size and last changed date)",
        )
        parser.add_argument(
            "-a",
            "--all",
            action="store_true",
            help="all files (by default, hidden files are not listed)",
        )
        parser.add_argument(
            "-r", "--reverse", action="store_true", help="reverse sort order"
        )
        parser.add_argument(
            "-t", "--time", action="store_true", help="sort by time instead of by name"
        )
        parser.add_argument(
            "files_or_dirs", nargs=REMAINDER, help="the file(s) or dir(s) to list"
        )
        return parser.parse_args(split(arg))

    @classmethod
    def get_env_arguments(cls, arg: str) -> tuple[tuple[str, ...], list[str]]:
        """Return parsed arguments for the env command"""
        parser = cls(prog="env", description="Print environment variables")
        parser.add_argument(
            "--include",
            nargs="*",
            choices=(PIP, UV),
            help="include additional variables (possible values: %(choices)s)",
        )
        parser.add_argument(
            "name_or_pattern",
            nargs="*",
            default=["*"],
            help="the variable name or pattern to show (default: %(default)s)",
        )
        arguments = parser.parse_args(split(arg))
        includes = tuple(arguments.include or [])
        return includes, arguments.name_or_pattern

    @classmethod
    def get_set_arguments(cls, arg: str) -> tuple[bool, str, str]:
        """Return parsed arguments for the env command"""
        parser = cls(prog="set", description="Set an environment variable")
        parser.add_argument(
            "-s",
            "--secret",
            action="store_true",
            help="enter the value through password input and mask it in putput",
        )
        parser.add_argument(
            "key",
            help="the variable name",
        )
        parser.add_argument(
            "value",
            nargs=REMAINDER,
            help="the variable value ",
        )
        arguments = parser.parse_args(split(arg))
        key = arguments.key
        explicit_value = " ".join(arguments.value)
        if arguments.secret and explicit_value:
            # Not allowed,
            # eg. argument is "-s KEY explicit value"
            parser.error(cls.msg_secret_value)
        #
        assignment_match = PRX_VARIABLE_ASSIGNMENT.match(key)
        if assignment_match:
            members = assignment_match.groupdict()
            key = members["key"]
            new_value = members["value"]
            if arguments.secret and (new_value or explicit_value):
                # Not allowed,
                # eg. argument is "-s KEY=value"
                parser.error(cls.msg_secret_value)
            #
            if explicit_value and not new_value:
                # eg. argument is 'KEY= explicit value'
                #     → KEY set to "explicit value"
                new_value = explicit_value
            elif new_value and explicit_value:
                # eg. argument is "KEY=new and explicit value"
                #     → KEY set to "new and explicit value"
                new_value = f"{new_value} {explicit_value}"
            #
            return arguments.secret, key, new_value
        #
        if not PRX_VARIABLE_NAME.match(key):
            # Not allowed,
            # eg. argument is "24 hours"
            parser.error(f"Invalid variable name {key}")
        #
        if arguments.secret:
            # eg. argument is "-s KEY"
            return True, key, EMPTY
        #
        if not explicit_value:
            explicit_value = input(f"Please enter a value for {key}: ")
        #
        # eg. argument is "KEY explicit value"
        #     → KEY is set to "explicit value"
        # eg. argument is "KEY" and "input value" is entered a the prompt →
        #     → KEY is set to "input value"
        return False, key, explicit_value


class Loop(Cmd):
    """Command loop"""

    def __init__(
        self,
        ca_file: Path | None,
        hostname_argument: str,
        repositories: list[str],
        default_username: str,
    ) -> None:
        """Initialize with the provided arguments"""
        if not repositories:
            raise ValueError("At least one repository is required")
        #
        self._backend = get_backend(
            SupportedBackendType.ARTIFACTORY,
            hostname_argument,
            default_username,
            *repositories,
            ca_file=ca_file,
        )
        self.availability = Availability(backend=self._backend)
        self.availability.show_versions()
        self.prompt = get_prompt()
        super().__init__()

    def do_cd(self, arg) -> None:
        """Change directory"""
        if arg:
            chdir(arg)
        else:
            try:
                chdir(Path.home())
            except RuntimeError as error:
                logging.error(str(error))
            #
        #
        self.prompt = get_prompt()

    def do_python(self, arg) -> None:
        """Run python (see output of python -V for the exact version)"""
        self._backend.execute(PYTHON, *split(arg), check=False)

    def do_spp(self, arg) -> None:
        """Shortcut for set PYTHONPATH=<arg>, eg. spp src → set PYTHONPATH=src"""
        try:
            self.do_set(f"{_PYTHONPATH}={split(arg)[0]}")
        except IndexError:
            logging.warning("spp requires an argument")
        #

    def complete_recover(
        self, text: str, unused_line: str, unused_begidx: int, unused_endidx: int
    ) -> list[str]:
        """Completion for the recover command"""
        if not text:
            return []
        #
        return sorted(key for key in self._backend.deleted_keys if key.startswith(text))

    def do_recover(self, arg) -> None:
        """Recover one or more previously unset environment variables"""
        for single_arg in split(arg):
            found_keys = sorted(fnmatch_filter(self._backend.deleted_keys, single_arg))
            for key in found_keys:
                logging.info("Recovering %s", key)
                self._backend.recover_entry(key)
            #
        #

    def do_unset(self, arg) -> None:
        """Unset (ie. reversibly delete) one or more environment variables"""
        all_keys = self._backend.keys()
        for single_arg in split(arg):
            found_keys = sorted(fnmatch_filter(all_keys, single_arg))
            for key in found_keys:
                logging.info("Unsetting %s", key)
                self._backend.delete_entry(key)
            #
        #

    def do_set(self, arg) -> None:
        """Set an environment variable"""
        try:
            secret, key, value = DefusedArgumentParser.get_set_arguments(arg)
        except OptionError:
            return
        #
        display = f"{key} → {value!r}"
        try:
            if secret:
                self._backend.set_masked_extra_entry(key)
                display = f"hidden value for {key}"
            else:
                self._backend.set_extra_entry(key, value)
            #
        except ValueError as error:
            logging.warning(str(error))
        else:
            logging.info("set %s", display)
        #

    def do_env(self, arg) -> None:
        """Print the environment variables"""
        try:
            include_additions, names_or_patterns = (
                DefusedArgumentParser.get_env_arguments(arg)
            )
        except OptionError:
            return
        #
        environment = self._backend.get_masked_environment(*include_additions)
        show_keys: set[str] = set()
        for single_pattern in names_or_patterns:
            show_keys.update(fnmatch_filter(environment, single_pattern))
        #
        if not show_keys:
            logging.warning(" – no matches –")
        #
        for key in sorted(show_keys):
            print(f"{key}={environment[key]!r}")
        #

    def complete_sh(
        self, text: str, line: str, begidx: int, unused_endidx: int
    ) -> list[str]:
        """Completion for the sh command"""
        return complete_paths(text, line, begidx, unused_endidx)

    def do_sh(self, arg) -> None:
        """Run an arbitrary command through the shell"""
        logging.warning("Running command with shell=True: %r", arg)
        self._backend.execute(arg, check=False, shell=True)

    def do_git(self, arg) -> None:
        """Run git with the provided arguments"""
        self._backend.execute("git", *split(arg), check=False)

    def complete_list(
        self, text: str, line: str, begidx: int, unused_endidx: int
    ) -> list[str]:
        """Completion for the list command"""
        return complete_paths(text, line, begidx, unused_endidx)

    def do_list(self, arg) -> None:
        """Print directory contents (emulation)"""
        try:
            args = DefusedArgumentParser.get_list_arguments(arg)
        except OptionError:
            return
        #
        try:
            for line in iter_paths_list(
                *args.files_or_dirs,
                long_format=args.long,
                show_all=args.all,
                sort_reverse=args.reverse,
                sort_by_time=args.time,
            ):
                print(line)
            #
        except ValueError as error:
            log_multiline(str(error), level=logging.ERROR)
            return
        #

    def do_pwd(self, unused_arg) -> None:
        """Print working directory"""
        if unused_arg:
            logging.warning("Ignored argument(s) %r", unused_arg)
        #
        print(getcwd())

    def do_pip(self, arg) -> None:
        """Run pip with the provided arguments"""
        self._backend.execute(PYTHON, "-m", "pip", *split(arg), check=False)

    def do_uv(self, arg) -> None:
        """Run uv with the provided arguments"""
        self._backend.execute("uv", *split(arg), check=False)

    def do_uvx(self, arg) -> None:
        """Run uvx with the provided arguments"""
        self._backend.execute("uvx", *split(arg), check=False)

    # pylint: disable=invalid-name ; required to support EOF character
    def do_EOF(self, unused_arg) -> bool:
        """Exit the REPL by EOF (eg. Ctrl-D on Unix)"""
        print()
        if unused_arg:
            logging.warning("Ignored argument(s) %r", unused_arg)
        #
        logging.info("bye")
        return True

    def emptyline(self) -> bool:
        """do nothing on empty input"""
        return False
