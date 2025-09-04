# -*- coding: utf-8 -*-

"""uvartage: wrapper for uv with artifact storage in airgapped environments"""

import logging

from enum import Enum
from getpass import getpass
from os import environ
from pathlib import Path
from subprocess import run, CompletedProcess
from sys import orig_argv
from urllib.parse import urlunsplit, quote

from .commons import EMPTY, enforce_str


_SSL_CERT_FILE = "SSL_CERT_FILE"
_MASK = "[MASKED]"

PIP = "pip"
UV = "uv"
UVX = "uvx"
_EXTRA = "extra"

PYTHON = orig_argv[0]


def get_index_url(base_url: str, repository_name: str) -> str:
    """Index URL for the provided repository name"""
    return f"{base_url}{repository_name}/simple"


class SupportedBackendType(str, Enum):
    """Supported Backend types"""

    ARTIFACTORY = "artifactory"

    def __str__(self):
        """required for proper argparse display,
        compare <https://stackoverflow.com/a/46385352>
        """
        return self.value


# pylint: disable=too-many-instance-attributes


class BackendBase:
    """Backend base class"""

    api_path = "/"
    scheme = "https"

    def __init__(
        self,
        hostname_argument: str,
        default_username: str,
        *repositories: str,
        require_login: bool = True,
        ca_file: Path | None = None,
    ) -> None:
        """Store the URL parts and the username"""
        self.__base_environment = dict(environ)
        if isinstance(ca_file, Path):
            ca_full_path = ca_file.resolve()
            if not ca_full_path.is_file():
                raise ValueError(f"{ca_full_path} does not exist or is not a file")
            #
            self.__base_environment.update(SSL_CERT_FILE=str(ca_full_path))
        elif _SSL_CERT_FILE not in self.__base_environment:
            logging.warning(
                "Neither the environment variable %r has been set,"
                " nor a CA file explicitly through --ca-file.",
                _SSL_CERT_FILE,
            )
            logging.warning(
                "You might encounter problems if using a non-standard"
                " (i.e. organization internal) certificate authority."
            )
        #
        try:
            self.__username, self.__hostname = hostname_argument.split("@")
        except ValueError:
            self.__username = default_username
            self.__hostname = hostname_argument
        #
        self.__api_base_url = enforce_str(
            urlunsplit((self.scheme, self.__hostname, self.api_path, EMPTY, EMPTY))
        )
        if require_login:
            self.__password = getpass(
                f"Please enter the password for {self.__username}"
                f" on {self.__hostname} (input is hidden): "
            )
            if not self.__password:
                raise ValueError("Stopping due to empty password input")
            #
        else:
            self.__username = EMPTY
            self.__password = EMPTY
        #
        self.__environment_additions: dict[str, dict[str, str]] = {_EXTRA: {}}
        self.__masked_overrides: dict[str, str] = {}
        self.__deleted_keys: set[str] = set()
        self.repositories = tuple(repositories)

    @property
    def hostname(self) -> str:
        """hostname property"""
        return self.__hostname

    @property
    def username(self) -> str:
        """Username property"""
        return self.__username

    @property
    def api_base_url(self) -> str:
        """API base URL"""
        return self.__api_base_url

    @property
    def deleted_keys(self) -> set[str]:
        """all deleted keys"""
        return set(self.__deleted_keys)

    @property
    def all_available_keys(self) -> set[str]:
        """all keys available as environment variables, except deleted keys"""
        return self.keys() - self.__deleted_keys

    def _get_environment(self, *include_additions: str) -> dict[str, str]:
        """Return the enwironment including the named additions"""
        environment: dict[str, str] = dict(self.__base_environment)
        for single_addition in [
            item for item in include_additions if item != _EXTRA
        ] + [_EXTRA]:
            environment |= self._get_additions(single_addition)
        #
        # Subtract deletions
        return {
            key: value
            for key, value in environment.items()
            if key in set(environment) - self.__deleted_keys
        }

    def get_masked_environment(self, *include_additions: str) -> dict[str, str]:
        """Return the enwironment including the named additions,
        values masked if necessary
        """
        return {
            key: self.__masked_overrides.get(key, value)
            for key, value in self._get_environment(*include_additions).items()
        }

    def execute(
        self,
        command: str,
        *args: str,
        check: bool = True,
        capture_output: bool = False,
        shell: bool = False,
    ) -> CompletedProcess:
        """Execute a command with the matching environment"""
        include_additions: list[str] = []
        if command in (PYTHON, PIP):
            include_additions.append(PIP)
        #
        if command in (UV, UVX):
            include_additions.append(UV)
        #
        environment = self._get_environment(*include_additions)
        if shell:
            ignoring = f" (ignoring {args})" if args else ""
            logging.warning("Executing with shell=True: %r%s", command, ignoring)
            return run(
                command,
                env=environment,
                check=check,
                capture_output=capture_output,
                shell=True,
            )
        #
        full_command = [command, *args]
        logging.info("Executing command: %r", full_command)
        return run(
            full_command,
            env=environment,
            check=check,
            capture_output=capture_output,
            shell=False,
        )

    def keys(self) -> set[str]:
        """Return all keys as a set, including deleted ones"""
        found_keys = set(self.__base_environment)
        for addition_key in (PIP, UV, _EXTRA):
            found_keys |= set(self._get_additions(addition_key))
        #
        return found_keys

    def _make_pip_environment(self) -> dict[str, str]:
        """Return the pip environment with PIP_INDEX_URL, and
        (if necessary) PIP_CERT and/or PIP_EXTRA_INDEX_URL
        """
        additions: dict[str, str] = {}
        ssl_cert_file = self.__base_environment.get(_SSL_CERT_FILE)
        if ssl_cert_file:
            additions.setdefault("PIP_CERT", ssl_cert_file)
        #
        if self.__username:
            pip_api_base_url = enforce_str(
                urlunsplit(
                    (
                        self.scheme,
                        f"{quote(self.__username, safe=EMPTY)}:"
                        f"{quote(self.__password, safe=EMPTY)}@"
                        f"{self.__hostname}",
                        self.api_path,
                        EMPTY,
                        EMPTY,
                    )
                )
            )
            masked_pip_api_base_url = enforce_str(
                urlunsplit(
                    (
                        self.scheme,
                        f"{quote(self.__username, safe=EMPTY)}:{_MASK}@{self.__hostname}",
                        self.api_path,
                        EMPTY,
                        EMPTY,
                    )
                )
            )
        else:
            pip_api_base_url = self.__api_base_url
            masked_pip_api_base_url = EMPTY
        #
        additions["PIP_INDEX_URL"] = get_index_url(
            pip_api_base_url, self.repositories[0]
        )
        extra_urls = [
            get_index_url(pip_api_base_url, extra_repo)
            for extra_repo in self.repositories[1:]
        ]
        masked_extra_urls = []
        if masked_pip_api_base_url:
            self.__masked_overrides["PIP_INDEX_URL"] = get_index_url(
                masked_pip_api_base_url, self.repositories[0]
            )
            masked_extra_urls = [
                get_index_url(masked_pip_api_base_url, extra_repo)
                for extra_repo in self.repositories[1:]
            ]
        #
        if extra_urls:
            additions["PIP_EXTRA_INDEX_URL"] = " ".join(extra_urls)
            if masked_extra_urls:
                self.__masked_overrides["PIP_EXTRA_INDEX_URL"] = " ".join(
                    masked_extra_urls
                )
            #
        #
        return additions

    def _make_uv_environment(self) -> dict[str, str]:
        """Return the uv environment with UV_DEFAULT_INDEX,
        UV_INDEX containing all extra indexes if any are defined
        (ie. if the number of repositiories is greater than 1),
        and UV_INDEX_{KEY}_USERNAME and UV_INDEX_{KEY}_PASSWORD for each index key
        (ie. "primary" for the default index with sequence number 0,
        and "extraN" for each extra index where N is its sequence number)
        """
        additions: dict[str, str] = {}
        extra_indexes = []
        for index_number, index_repo in enumerate(self.repositories):
            index_key = f"extra{index_number}" if index_number else "primary"
            index_cred_prefix = f"UV_INDEX_{index_key.upper()}"
            current_index = (
                f"{index_key}={get_index_url(self.__api_base_url, index_repo)}"
            )
            if index_number:
                extra_indexes.append(current_index)
            else:
                additions["UV_DEFAULT_INDEX"] = current_index
            #
            if self.__username:
                additions.update(
                    {
                        f"{index_cred_prefix}_USERNAME": self.__username,
                        f"{index_cred_prefix}_PASSWORD": self.__password,
                    }
                )
                self.__masked_overrides[f"{index_cred_prefix}_PASSWORD"] = _MASK
            #
        #
        if extra_indexes:
            additions.update(UV_INDEX=" ".join(extra_indexes))
        #
        return additions

    def _get_additions(self, flavor: str) -> dict[str, str]:
        """Return or set the environment additions"""
        try:
            return self.__environment_additions[flavor]
        except KeyError:
            logging.debug("Setting environment additions for %s ...", flavor)
        #
        if flavor == UV:
            additions_creator_function = self._make_uv_environment
        elif flavor == PIP:
            additions_creator_function = self._make_pip_environment
        else:
            raise ValueError(f"unsupported flavor {flavor!r}")
        #
        return self.__environment_additions.setdefault(
            flavor, additions_creator_function()
        )

    def delete_entry(self, key: str) -> None:
        """Mark key as deleted"""
        self.__deleted_keys.add(key)

    def recover_entry(self, key: str) -> None:
        """Recover and rea previously deleted entry"""
        if key in self.all_available_keys:
            logging.info("%s was still available", key)
            return
        #
        try:
            self.__deleted_keys.remove(key)
        except KeyError:
            logging.warning("%s not found")
        #

    def set_extra_entry(self, key: str, value: str) -> None:
        """Add or update an entry in the "extra" environment additions"""
        if not value:
            raise ValueError(f"Empty value, will not add or update {key}")
        #
        self.__environment_additions[_EXTRA][key] = value

    def set_masked_extra_entry(self, key: str) -> None:
        """Add or update a masked entry in the "extra" environment additions"""
        secret_value = getpass(f"Please enter the value for {key} (input is hidden): ")
        self.set_extra_entry(key, secret_value)
        self.__masked_overrides[key] = _MASK


class Artifactory(BackendBase):
    """Artifactory backend"""

    api_path = "/artifactory/api/pypi/"


def get_backend(
    backend_type: SupportedBackendType,
    hostname_argument: str,
    default_username: str,
    *repositories: str,
    ca_file: Path | None = None,
) -> BackendBase:
    """Return the backend for backend_type ans hostname_argument"""
    match backend_type:
        case SupportedBackendType.ARTIFACTORY:
            return Artifactory(
                hostname_argument, default_username, *repositories, ca_file=ca_file
            )
        #
    #
    raise ValueError(f"Unsupported backend {backend_type!r}")
