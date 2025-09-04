from __future__ import annotations

import os
import typing

from configures.logging import logger
from configures.exceptions import (
    ConfiguresError,
    ConfigurationError,
)
from configures import configuration as _configuration
from configures import specification as _specification

logger = logger.getChild(__name__)


class Secrets(dict):
    """The Secrets class provides a singleton container to hold configuration"""

    _instance: Secrets = None
    _secrets: dict[str, object] = None
    _truthy: list[str] = None
    _falsey: list[str] = None
    _configuration: _configuration.Configuration = None
    _sentinel: object = None
    _backup: dict[str, object] = None

    def __new__(cls, *args, **kwargs):
        """Only allow instantiation of a singleton instance of the Secrets class"""

        if cls._instance is None:
            cls._instance = super(Secrets, cls).__new__(cls)

        return cls._instance

    def __init__(
        self,
        configuration: _configuration.Configuration = None,
        specification: str = None,
        callback: callable = None,
        truthy: list[str] | tuple[str] | set[str] = ["YES", "TRUE", "ON"],
        falsey: list[str] | tuple[str] | set[str] = ["NO", "FALSE", "OFF"],
        sentinel: object = None,
        secrets: dict[str, object] | Secrets = None,
        **kwargs,
    ):
        logger.debug(
            "%s.__init__(configuration: %s, specification: %s, callback: %s, kwargs: %s)"
            % (
                self.__class__.__name__,
                configuration,
                specification,
                callback,
                kwargs,
            )
        )

        self._secrets: dict[str, object] = {}

        if isinstance(secrets, dict):
            for name, value in secrets.items():
                self._secrets[name] = value
        elif isinstance(secrets, Secrets):
            for name, value in secrets.items():
                self._secrets[name] = value
        else:
            for name, value in os.environ.items():
                self._secrets[name] = value

        for name, value in kwargs.items():
            self._secrets[name] = value

        self._truthy: list[str] = []

        if not isinstance(truthy, (list, tuple, set)):
            raise TypeError(
                "The 'truthy' argument, if specified, must have a list, tuple or set value!"
            )
        else:
            for value in truthy:
                if not isinstance(value, str):
                    raise TypeError(
                        "The 'truthy' argument list must consist solely of string values!"
                    )
                self._truthy.append(value.upper())

        self._falsey: list[str] = []

        if not isinstance(falsey, (list, tuple, set)):
            raise TypeError(
                "The 'falsey' argument, if specified, must have a list, tuple or set value!"
            )
        else:
            for value in falsey:
                if not isinstance(value, str):
                    raise TypeError(
                        "The 'falsey' argument list must consist solely of string values!"
                    )
                self._falsey.append(value.upper())

        # Determine if there is any overlap between the truthy and falsey value lists:
        if len(overlap := set(self._truthy).intersection(set(self._falsey))) > 0:
            raise ConfiguresError(
                f"The 'truthy' and 'falsey' arguments must not contain any overlapping values; currently the following {'value is' if len(overlap) == 1 else 'values are'} present in both lists: {', '.join(overlap)}!"
            )

        if specification is None:
            pass
        elif not isinstance(specification, str):
            raise ConfiguresError(
                "The 'specification' argument, if specified, must have a string value!"
            )

        if configuration is None:
            if isinstance(specification, str):
                if not os.path.exists(specification):
                    raise ConfiguresError(
                        f"The 'specification' argument value, {specification}, references a configuration specification file that does not exist!"
                    )
                elif extension := os.path.splitext(specification)[-1]:
                    if extension == ".spec":
                        configuration = _configuration.Configuration(
                            specification=_specification.SpecificationFile(
                                filename=specification,
                            )
                        )
                    elif extension == ".json":
                        configuration = _configuration.Configuration(
                            specification=_specification.SpecificationFileJSON(
                                filename=specification,
                            )
                        )
                    elif extension in [".yaml", ".yml"]:
                        configuration = _configuration.Configuration(
                            specification=_specification.SpecificationFileYAML(
                                filename=specification,
                            )
                        )
                    else:
                        raise ValueError(
                            f"The 'specification' argument value, {specification}, references a configuration specification file of an unsupported file type ({extension}); supported types are SPEC, JSON and YAML!"
                        )
                else:
                    raise ValueError(
                        "The 'specification' argument value, if specified, must reference a configuration specification file!"
                    )
            else:
                configuration = _configuration.Configuration(
                    specification=_specification.SpecificationData(),
                )
        elif isinstance(configuration, _configuration.Configuration):
            for name, value in configuration.validate(secrets=self):
                logger.debug(" >>> %s => %s" % (name, value))
                self._secrets[name] = value
        else:
            raise ConfiguresError(
                "The 'configuration' argument, if specified, must reference a Configuration class instance!"
            )

        self._configuration = configuration

        # If a callback has been specified, call it once the initialisation is complete
        if callback is None:
            pass
        elif callable(callback):
            callback(self)
        else:
            raise ConfiguresError(
                "The 'callback' argument, if specified, must have a valid callable value!"
            )

        self._sentinel: object = sentinel

    def __enter__(self):
        logger.debug("%s.__enter__()" % (self.__class__.__name__))

        # Create a distinct copy of the secrets when entering a new context
        self._backup = self._secrets
        self._secrets = dict(self._secrets)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        logger.debug("%s.__exit__()" % (self.__class__.__name__))

        # Restore the secrets upon exiting the context
        self._secrets = self._backup
        self._backup = None

        return self

    def __call__(self, **kwargs):
        """Support calling a Secrets instance like a method, while providing the ability
        to update or add to the existing secrets via keyword arguments passed as part of
        the call. Any keyword arguments having the same name as an existing secret will
        overwrite the value of the matching secret, and any arguments that have unique
        names not yet encountered by the Secrets instance will become new secrets that
        subsequently will be accessible via the instance until deleted or destroyed."""

        self.update(**kwargs)

    def __getitem__(self, name: str) -> object | None:
        """Supports interacting with the Secrets class as though it was a dictionary."""

        if not isinstance(name, str):
            raise TypeError("The 'name' argument must have a string value!")

        if name in self._secrets:
            return self._secrets[name]
        else:
            raise KeyError(f"The '{name}' key does not exist in the secrets!")

    def __setitem__(self, name: str, value: object):
        """Supports interacting with the Secrets class as though it was a dictionary."""

        if not isinstance(name, str):
            raise TypeError("The 'name' argument must have a string value!")

        self._secrets[name] = value

    def __delitem__(self, name: str):
        """Supports interacting with the Secrets class as though it was a dictionary."""

        if not isinstance(name, str):
            raise TypeError("The 'name' argument must have a string value!")

        if name in self._secrets:
            del self._secrets[name]
        else:
            raise KeyError(f"The '{name}' key does not exist in the secrets!")

    def __contains__(self, name: object) -> bool:
        """Supports interacting with the Secrets class as though it was a dictionary."""

        if not isinstance(name, str):
            raise TypeError("The 'name' argument must have a string value!")

        return name in self._secrets

    def __len__(self) -> int:
        """Returns the number of secrets currently held by the Secrets instance."""

        return len(self._secrets)

    def __iter__(self) -> object:
        """Supports iterating over the secrets currently held by the Secrets instance."""

        return iter(self._secrets)

    @property
    def configuration(self) -> _configuration.Configuration:
        """Return the 'configuration' property value"""
        return self._configuration

    @property
    def sentinel(self) -> object:
        """Return the 'sentinel' value, used when determining if a secret is 'null'."""

        return self._sentinel

    @sentinel.setter
    @typing.final
    def sentinel(self, sentinel: object):
        """The 'sentinel' property can only be set via the constructor"""

        raise NotImplementedError(
            "The 'sentinel' property value can only be set during class instantiation!"
        )

    def get(self, name: str, default: object = None) -> object | None:
        """The 'get' method provides support for obtaining a named configuration value,
        if a matching secret exists as well as providing support for returning a default
        value if the named secret does not exist."""

        if not isinstance(name, str):
            raise TypeError("The 'name' argument must have a string value!")

        return self._secrets.get(name, default)

    def set(self, name: str, value: object) -> Secrets:
        """The 'set' method provides support for setting a named configuration value."""

        if not isinstance(name, str):
            raise TypeError("The 'name' argument must have a string value!")

        self._secrets[name] = value

        return self

    def require(self, name: str) -> object:
        """The 'require' method provides support for obtaining a named secret value,
        ensuring that a matching secret exists. If no matching secret is found, then an
        exception will be raised."""

        if not isinstance(name, str):
            raise TypeError("The 'name' argument must have a string value!")

        if not name in self._secrets:
            raise ConfigurationError(f"The required secret, '{name}', does not exist!")

        return self._secrets[name]

    def empty(self, name: str, default: object = None) -> bool:
        """The 'empty' method supports determining if the named configuration value has
        an empty value or not, returning True if it does or False otherwise."""

        if not isinstance(name, str):
            raise TypeError("The 'name' argument must have a string value!")

        if isinstance(value := self.get(name=name, default=default), str):
            return len(value := value.strip()) == 0

        return False

    def nonempty(self, name: str, default: object = None) -> bool:
        """The 'nonempty' method supports determining if the named configuration value
        has an non-empty value or not, returning True if it does or False otherwise."""

        if not isinstance(name, str):
            raise TypeError("The 'name' argument must have a string value!")

        if isinstance(value := self.get(name=name, default=default), str):
            return len(value := value.strip()) > 0

        return False

    def null(self, name: str, default: object = None) -> bool:
        """The 'null' method provides support for determining if the named configuration
        value has an "null" value or not; this is achieved by comparing the secret value
        against the configured class-level sentinel value. If a match is found then this
        method returns True or False otherwise."""

        return self.get(name=name, default=default) == self.sentinel

    def true(self, name: str, default: object = None) -> bool:
        """The 'true' method provides support for determining if the named configuration
        value has a truthy value or not; the truthy values are configured at class-level
        and if a match is found between the current configuration value and one of the
        truthy values, the method will return True, or False otherwise; if the variable
        has not been specified in the application's configuration, the default value, if
        specified, will be returned instead."""

        if not isinstance(name, str):
            raise TypeError("The 'name' argument must have a string value!")

        if isinstance(value := self.get(name=name, default=default), bool):
            return value is True
        elif isinstance(value := self.get(name=name, default=default), str):
            return value.upper() in self._truthy

        return False

    def false(self, name: str, default: object = None) -> bool:
        """The 'false' method supports determining if the named configuration value has
        a falsey value or not; the falsey values are configured at class-level and if a
        match is found between the current configuration value and one of the falsey
        values, the method will return True, or false otherwise; if the variable has not
        been specified in the application's configuration, the default value, if
        specified, will be returned instead."""

        if not isinstance(name, str):
            raise TypeError("The 'name' argument must have a string value!")

        if isinstance(value := self.get(name=name, default=default), bool):
            return value is False
        elif isinstance(value := self.get(name=name, default=default), str):
            return value.upper() in self._falsey

        return False

    def int(self, name: str, default: int = None) -> int | None:
        """The 'int' method provides support for returning the named configuration value
        cast to an 'int' value, if the configuration value has been specified, otherwise
        the default value, if specified, will be returned instead."""

        if not isinstance(name, str):
            raise TypeError("The 'name' argument must have a string value!")

        if default is None:
            pass
        elif not isinstance(default, int):
            raise TypeError(
                "The 'default' argument, if specified, must have an integer value!"
            )

        if name in self._secrets:
            return int(self._secrets[name])

        return default

    def float(self, name: str, default: float = None) -> float | None:
        """The 'float' method provides support for returning the named configuration
        value cast to a 'float' value, if the configuration value has been specified,
        otherwise the default value, if specified, will be returned instead."""

        if not isinstance(name, str):
            raise TypeError("The 'name' argument must have a string value!")

        if default is None:
            pass
        elif not isinstance(default, float):
            raise TypeError(
                "The 'default' argument, if specified, must have a floating-point value!"
            )

        if name in self._secrets:
            return float(self._secrets[name])

        return default

    def combine(
        self,
        variables: list[str] | tuple[str] | set[str],
        separator: str = None,
        strip: bool = False,
    ) -> str | None:
        """The 'combine' method provides support for combining the string values from
        multiple environment variables, joining parts with an optional separator
        character, and optionally stripping the separator character from the beginning
        and end of each environment variable value."""

        if not isinstance(variables, (list, tuple, set)):
            raise TypeError(
                "The 'variables' argument must have a list, tuple or set value!"
            )

        if separator is None:
            pass
        elif not isinstance(separator, str):
            raise TypeError(
                "The 'separator' argument, if specified, must have a string value!"
            )

        if not isinstance(strip, bool):
            raise TypeError("The 'strip' argument must have a boolean value!")

        combine: list[str] = []

        for name in variables:
            if not isinstance(name, str):
                raise TypeError("All variable names must be specified as strings!")

            if not name in self._secrets:
                raise KeyError(f"The variable, '{name}', has not been set!")

            if not isinstance(value := self._secrets[name], str):
                raise TypeError(f"The variable, '{name}', must have a string value!")

            if len(value) == 0:
                raise ValueError(
                    f"The variable, '{name}', must have a non-empty string value!"
                )

            if isinstance(separator, str) and len(separator) > 0 and strip is True:
                value = value.strip(separator)

            combine.append(value)

        if len(combine) > 0:
            if isinstance(separator, str) and len(separator) > 0:
                return separator.join(combine)
            else:
                return "".join(combine)

    def keys(self) -> list[str]:
        """Supports obtaining the keys for the secrets currently held by the Secrets instance."""

        return list(self._secrets.keys())

    def values(self) -> list[object]:
        """Supports obtaining the values for the secrets currently held by the Secrets instance."""

        return list(self._secrets.values())

    def items(self) -> list[tuple[str, object]]:
        """Supports obtaining the items for the secrets currently held by the Secrets instance."""

        return list(self._secrets.items())

    def update(self, **secrets: dict[str, object]):
        """Supports updating the secrets currently held by the Secrets instance."""

        for name, value in secrets.items():
            self[name] = value

        return self
