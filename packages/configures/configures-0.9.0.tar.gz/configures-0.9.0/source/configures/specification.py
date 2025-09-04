from __future__ import annotations

import abc
import os
import re
import typing
import json
import yaml

from configures.logging import logger
from configures import variable as _variable
from configures import validator as _validator

logger = logger.getChild(__name__)


class Specification(object, metaclass=abc.ABCMeta):
    """The Specification class is the abstract base class for defining a configuration
    specification. This class must be overridden and all abstract methods must be given
    a suitable implementation in the derived classes.

    The purpose of the provided configuration specification file is to list all of the
    required as well as any desired optional configuration options. For each option the
    specification defines the acceptable format or values an option can hold, as well as
    whether the option is required, whether the option is nullable, and a default value
    that can be used as a fallback when an non-required configuration option has not
    been specified."""

    _variables: dict[str, _variable.Variable] = {}

    @abc.abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    def __len__(self) -> int:
        """Returns the number of secrets specifications held by the Specification instance."""

        return len(self._variables)

    def __contains__(self, name: str) -> bool:
        if not isinstance(name, str):
            raise TypeError("The 'name' argument must have a string value!")

        return name in self._variables

    def __getitem__(self, name: str) -> _variable.Variable | None:
        """Supports interacting with the Specification class as though it was a dictionary."""

        if not isinstance(name, str):
            raise TypeError("The 'name' argument must have a string value!")

        if isinstance(variable := self._variables.get(name), _variable.Variable):
            return variable

    def __setitem__(self, name: str, value: _variable.Variable):
        """Supports interacting with the Specification class as though it was a dictionary."""

        if not isinstance(name, str):
            raise TypeError("The 'name' argument must have a string value!")

        if not isinstance(value, _variable.Variable):
            raise TypeError(
                "The 'value' argument must reference a Variable class instance!"
            )

        raise NotImplementedError(
            "The secrets specifications items cannot be modified after instantiation!"
        )

    def __delitem__(self, name: str):
        """Supports interacting with the Specification class as though it was a dictionary."""

        raise NotImplementedError(
            "The secrets specifications items cannot be deleted after instantiation!"
        )

    def __iter__(self) -> typing.Generator[tuple[str, _variable.Variable], None, None]:
        """Supports iterating over the secrets specifications held by the Specification instance."""

        return iter(self._variables)

    def update(self, *args, **kwargs):
        """Supports updating the secrets specifications held by the Specification instance."""

        raise NotImplementedError(
            "The secrets specifications cannot be updated after instantiation!"
        )

    def clear(self):
        """Supports clearing the secrets specifications held by the Specification instance."""

        raise NotImplementedError(
            "The secrets specifications cannot be cleared after instantiation!"
        )

    def copy(self) -> dict[str, _variable.Variable]:
        """Supports copying the secrets specifications held by the Specification instance."""

        return {name: variable for name, variable in self._variables.items()}

    def keys(self) -> list[str]:
        """Supports obtaining the keys for the secrets specification held by the Specification instance."""

        return list(self._variables.keys())

    def values(self) -> list[str]:
        """Supports obtaining the values for the secrets specification held by the Specification instance."""

        return list(self._variables.values())

    def items(self) -> typing.Generator[tuple[str, _variable.Variable], None, None]:
        """Supports obtaining the items for the secrets specification held by the Specification instance."""

        for name, variable in self._variables.items():
            yield (name, variable)

        return None


class SpecificationData(Specification):
    def __init__(self, **variables: dict[str, dict]):
        self._variables: dict[str, _variable.Variable] = {}

        for name, specification in variables.items():
            if not isinstance(name, str):
                raise TypeError("Each secrets variable name must have a string value!")

            if not isinstance(specification, dict):
                raise TypeError(
                    "Each secrets variable specification must have a dictionary value!"
                )

            required = specification.get("required") is True
            nullable = specification.get("nullable") is True
            validate: dict = specification.get("validate") or specification
            pattern: str = validate.get("pattern")
            options: list = validate.get("options")
            default: object = specification.get("default")

            validator: _validator.Validator = None

            if isinstance(pattern, str):
                validator = _validator.ValidatorRegex(
                    pattern=pattern,
                    required=required is True,
                    nullable=nullable is True,
                )
            elif isinstance(options, list):
                validator = _validator.ValidatorOption(
                    options=options,
                    required=required is True,
                    nullable=nullable is True,
                )

            self._variables[name] = _variable.Variable(
                name=name,
                validator=validator,
                default=default,
            )


class SpecificationFile(Specification):
    r"""The SpecificationFile class provides support for loading a configuration
    validation specification from a configuration validation file in plain-text format.

    The configuration validation file specification must conform to the following format
    with one or more lines expressed according to the pattern illustrated below:

    [<optional?>]<environment-variable-name>=(<regex>)[\[<optional-default-value>\]]

    Where <environment-variable-name> is the name of the environment variable as set in
    the environment and as specified in the application or package software; the names
    of environment variables are usually capitalised, but this is a convention rather
    than a requirement, and will depend upon the application or package in question.
    The [<optional?>] flag notes if an environment variable is optional; this is
    specified by prefixing the environment variable's name with a question mark ("?")
    character – required environment variables must be listed in the file without the
    optional flag. Following the environment variable's name a regular expression can
    be provided which will be used to validate the form and accepted values of the
    environment variable; if no regular expression is provided, only the presence of
    the environment variable will be checked and unless it is marked as being optional,
    a ConfigurationError will be raised if it is not available.

    Below is an example highlighting the structure of a possible rule:

    ?TZ=([A-Za-z]+(\_[A-Za-z]+)?/[A-Za-z\_]+(\_[A-Za-z])?)[America/Los_Angeles]

    The rule specifies that the "TZ" environment variable is optional, but if it is
    specified, that its value must consist of at least one of characters "A-Z" and
    "a-z", optionally followed by one or more of the characters "A-Z", "a-z" and "_"
    then a "/" separator character, followed by one or more of the characters "A-Z",
    "a-z", optionally followed by one or more of the characters "A-Z", "a-z" and "_"
    such that a value like "America/New_York" would be considered valid, whereas
    a value like "123" or "America" would not. As this rule also specifies an optional
    default value of "America/Los_Angeles", if the environment variable is not set the
    default value will be applied to the current environment's configuration instead.

    The regular expression rules can also be used to specify a range of fixed values
    such as "YES" and "NO" with a rule similar to the following:

    SOME_FEATURE_FLAG=(YES|NO)

    By being able to provide a listing of the environment variables used within the
    application or package as well as being able to note which environment variables
    are optional, as well as specifying the acceptable values in a concise way, the
    configuration can be validated to be within the expected range of the software
    during the very first steps of initialisation, allowing for configuration issues
    to be highlighted at startup before any issues related to misconfiguration could
    occur."""

    @typing.final
    def __init__(self, *args, filename: str, **kwargs):
        if not isinstance(filename, str):
            raise TypeError("The 'filename' must have a string value!")
        elif not os.path.exists(filename):
            raise RuntimeError(f"The specification file, {filename}, does not exist!")

        self._variables: dict[str, _variable.Variable] = {}

        required: dict = {}
        optional: dict = {}
        nullable: list = []
        defaults: dict = {}

        pattern = re.compile(
            r"(?P<optional>\?)?(?P<name>[A-Za-z][A-Za-z0-9_]+)(?P<nullable>\?)?(=\((?P<pattern>.*?)\)(\[(?P<default>.*)\])?)?"
        )

        with open(filename, "r") as handle:
            while line := handle.readline():
                if len(line := line.strip()) > 0:
                    if line.startswith("#"):
                        continue

                    if (matches := re.match(pattern, line)) is None:
                        raise ValueError(
                            "The environment variable validation regex is invalid!"
                        )

                    logger.debug(
                        " >>> %s => %s (%s) [%s]"
                        % (
                            matches.group("name"),
                            matches.group("pattern"),
                            matches.group("default"),
                            "YES" if matches.group("optional") else "NO",
                        )
                    )

                    if matches.group("optional") == "?":
                        optional[matches.group("name")] = matches.group("pattern")
                    else:
                        required[matches.group("name")] = matches.group("pattern")

                    if matches.group("nullable") == "?":
                        nullable.append(matches.group("name"))

                    if default := matches.group("default"):
                        defaults[matches.group("name")] = default

        required.update(optional)

        for name, pattern in required.items():
            default: object = defaults.get(name)

            self._variables[name] = _variable.Variable(
                name=name,
                validator=_validator.ValidatorRegex(
                    pattern=pattern,
                    required=(name in optional) is False,
                    nullable=(name in nullable) is True,
                ),
                default=default,
            )


class SpecificationFileJSON(Specification):
    r"""The SpecificationFileJSON class provides support for loading a configuration
    validation specification from a configuration specification file in JSON format.

    The configuration validation specification must conform to the following format with
    one or more nested JSON dictionaries expressed according to the pattern below:

    {
        "<environment-variable-name>": {
            "optional": <optional>,
            "nullable": <nullable>,
            "validate": {
                "pattern": <pattern>
            },
            "default": <default>
        },
        ...
        "<environment-variable-name>": {
            "optional": <optional>,
            "nullable": <nullable>,
            "validate": {
                "options": ...
            },
            "default": <default>
        }
    }

    Each block must note the configuration variable name to which it applies, and each
    configuration variable should only be named once, otherwise the last instance will
    be used. The <configuration-variable-name> expressed as a string must match the name
    of the configuration variable as held in the secrets and as used in the software.

    The validation specification for the variable is then detailed within the block.

    The <optional> (boolean) flag notes if a configuration variable is optional or not;
    this is specified by providing the "optional" key with a boolean value of `true` if
    the associated configuration variable is optional, and thus does not need specifying
    in the secrets. For required configuration variables, the "optional" key can either
    be omitted from the specification for the variable, or it must have a `false` value.

    The <nullable> (boolean) flag notes if a configuration variable's value can hold a
    null value or not; this is specified by providing the "nullable" key with a boolean
    value of `true`. The "nullable" key only needs specifying as noted for variables
    that are nullable; for non-nullable variables, the "nullable" key can either be
    omitted from the specification for the variable, or it must have a `false` value.

    In order to validate the value of a configuration variable, the library currently
    provides the following validation mechanisms:

        * regular expression matching
        * basic options list matching

    To validate the value of a configuration variable, at least one of the validation
    mechanisms must be configured via the "validate" key for the relevant variable.

    To use regular expression matching, a regular expression must be provided under the
    "validate" -> "pattern" key-path for the relevant variable. The regular expression
    must be written so that it matches against the valid options for the variable.

    To use basic options list matching, a list of one or more accepted option values,
    must be provided via the "validate" -> "options" key-path for the relevant variable.

    Each configuration variable will be validated through the validation mechanisms that
    have been defined for it in the specification. One should ensure the validations are
    compatible with each other – that is that a configuration variable value will either
    match or fail to match through all of the validation mechanisms defined for a given
    variable. A validation regular expression for example should not result in a match
    when the corresponding options list match would fail or vice-versa.

    If no validation mechanisms are defined for a given configuration variable, only
    the presence of the configuration variable will be checked, and unless it is marked
    as being optional, a ConfigurationError will be raised if it has not been defined.

    An example configuration variable specification may look something like the below:

    {
        "TIMEZONE": {
            "optional": false,
            "nullable": false,
            "validate": {
                "pattern": "[A-Z]{1}[A-Za-z]+/[A-Za-z\_]+(\_[A-Za-z])?"
            },
            "default": "America/Los_Angeles"
        },
        "UI_COLOR_THEME": {
            "optional": true,
            "nullable": false,
            "validate": {
                "pattern": "[A-Z]{1}([a-z]{1,})?/[A-Z]{1}([a-z]{1,})?",
                "options": [
                    "Grey/Blue",
                    "Grey/Orange",
                    "Grey/Red"
                ]
            },
            "default": "Grey/Blue"
        },
    }
    """

    @typing.final
    def __init__(self, *args, filename: str, **kwargs):
        if not isinstance(filename, str):
            raise TypeError("The 'filename' must have a string value!")
        elif not os.path.exists(filename):
            raise RuntimeError(f"The specification file, {filename}, does not exist!")

        self._variables: dict[str, _variable.Variable] = {}

        with open(filename, "r") as handle:
            if specifications := json.load(handle):
                for name, specification in specifications.items():
                    required = specification.get("required") is True
                    nullable = specification.get("nullable") is True
                    default = specification.get("default")
                    validate = specification.get("validate") or specification

                    if pattern := validate.get("pattern"):
                        self._variables[name] = _variable.Variable(
                            name=name,
                            validator=_validator.ValidatorRegex(
                                pattern=pattern,
                                required=required,
                                nullable=nullable,
                            ),
                            default=default,
                        )
                    elif options := validate.get("options"):
                        self._variables[name] = _variable.Variable(
                            name=name,
                            validator=_validator.ValidatorOption(
                                options=options,
                                required=required,
                                nullable=nullable,
                            ),
                            default=default,
                        )
                    else:
                        raise ValueError(
                            "The specification must define a regex 'pattern' or an 'options' list validation!"
                        )


class SpecificationFileYAML(Specification):
    r"""The SpecificationFileYAML class provides support for loading a configuration
    validation specification from a configuration specification file in YAML format.

    The configuration validation specification must conform to the following format with
    one or more nested YAML dictionaries expressed according to the pattern below:

    <environment-variable-name-one>:
      optional: <optional>
      nullable: <nullable>
      validate:
        pattern: <pattern>
      default: <default>

    <environment-variable-name-two>:
      optional: <optional>
      nullable: <nullable>
      validate:
      options:
        - '1'
        - '2'
        - '3'
      default: <default>

    Each block must note the configuration variable name to which it applies, and each
    configuration variable should only be named once, otherwise the last instance will
    be used. The <configuration-variable-name> expressed as a string must match the name
    of the configuration variable as held in the secrets and as used in the software.

    The validation specification for the variable is then detailed within the block.

    The <optional> (boolean) flag notes if a configuration variable is optional or not;
    this is specified by providing the "optional" key with a boolean value of `true` if
    the associated configuration variable is optional, and thus does not need specifying
    in the secrets. For required configuration variables, the "optional" key can either
    be omitted from the specification for the variable, or it must have a `false` value.

    The <nullable> (boolean) flag notes if a configuration variable's value can hold a
    null value or not; this is specified by providing the "nullable" key with a boolean
    value of `true`. The "nullable" key only needs specifying as noted for variables
    that are nullable; for non-nullable variables, the "nullable" key can either be
    omitted from the specification for the variable, or it must have a `false` value.

    In order to validate the value of a configuration variable, the library currently
    provides the following validation mechanisms:

        * regular expression matching
        * basic options list matching

    To validate the value of a configuration variable, at least one of the validation
    mechanisms must be configured via the "validate" key for the relevant variable.

    To use regular expression matching, a regular expression must be provided under the
    "validate" -> "pattern" key-path for the relevant variable. The regular expression
    must be written so that it matches against the valid options for the variable.

    To use basic options list matching, a list of one or more accepted option values,
    must be provided via the "validate" -> "options" key-path for the relevant variable.

    Each configuration variable will be validated through the validation mechanisms that
    have been defined for it in the specification. One should ensure the validations are
    compatible with each other – that is that a configuration variable value will either
    match or fail to match through all of the validation mechanisms defined for a given
    variable. A validation regular expression for example should not result in a match
    when the corresponding options list match would fail or vice-versa.

    If no validation mechanisms are defined for a given configuration variable, only
    the presence of the configuration variable will be checked, and unless it is marked
    as being optional, a ConfigurationError will be raised if it has not been defined.

    An example configuration variable specification may look something like the below:

    TIMEZONE:
      optional: false
      nullable: false
      validate:
        pattern: "[A-Z]{1}[A-Za-z]+/[A-Za-z\_]+(\_[A-Za-z])?"
      default: "America/Los_Angeles"

    UI_COLOR_THEME:
      optional: true
      nullable: false
      validate:
        pattern: "[A-Z]{1}([a-z]{1,})?/[A-Z]{1}([a-z]{1,})?"
        options:
          - "Grey/Blue"
          - "Grey/Orange"
          - "Grey/Red"
      default: "Grey/Blue"
    """

    @typing.final
    def __init__(self, *args, filename: str, **kwargs):
        if not isinstance(filename, str):
            raise TypeError("The 'filename' must have a string value!")
        elif not os.path.exists(filename):
            raise RuntimeError(f"The specification file, {filename}, does not exist!")

        self._variables: dict[str, _variable.Variable] = {}

        with open(filename, "r") as handle:
            if specifications := yaml.load(handle, Loader=yaml.SafeLoader):
                for name, specification in specifications.items():
                    required = specification.get("required") is True
                    nullable = specification.get("nullable") is True
                    default = specification.get("default")
                    validate = specification.get("validate") or specification

                    if pattern := validate.get("pattern"):
                        self._variables[name] = _variable.Variable(
                            name=name,
                            validator=_validator.ValidatorRegex(
                                pattern=pattern,
                                required=required,
                                nullable=nullable,
                            ),
                            default=default,
                        )
                    elif options := validate.get("options"):
                        self._variables[name] = _variable.Variable(
                            name=name,
                            validator=_validator.ValidatorOption(
                                options=options,
                                required=required,
                                nullable=nullable,
                            ),
                            default=default,
                        )
                    else:
                        raise ValueError(
                            "The specification must define a regex 'pattern' or an 'options' list validation!"
                        )
