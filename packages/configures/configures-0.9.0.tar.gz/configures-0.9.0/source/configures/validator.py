from __future__ import annotations

import abc
import re
import typing

from configures.logging import logger
from configures import variable as _variable

logger = logger.getChild(__name__)


class Validator(object, metaclass=abc.ABCMeta):
    """The Validator abstract base class, represents a mechanism for validating a
    configuration value, including whether it is required or nullable."""

    @typing.final
    def __init__(self, required: bool = True, nullable: bool = False):
        """Initialise the Validator class instance, setting the properties for use"""

        if not isinstance(required, bool):
            raise TypeError("The 'required' argument must have a boolean value!")

        self._required: bool = required

        if not isinstance(nullable, bool):
            raise TypeError("The 'nullable' argument must have a boolean value!")

        self._nullable: bool = nullable

    @property
    def required(self) -> bool:
        """Return the 'required' property boolean value"""

        return self._required

    @required.setter
    @typing.final
    def required(self, required: bool):
        """The 'required' property can only be set via the constructor"""

        raise NotImplementedError(
            "The 'required' property value can only be set during class instantiation!"
        )

    @property
    def nullable(self) -> bool:
        """Return the 'nullable' property boolean value"""

        return self._nullable

    @nullable.setter
    @typing.final
    def nullable(self, nullable: bool):
        """The 'nullable' property can only be set via the constructor"""

        raise NotImplementedError(
            "The 'nullable' property value can only be set during class instantiation!"
        )

    @abc.abstractmethod
    def valid(self, variable: _variable.Variable, value: object = None) -> bool:
        """Determine if the provided variable has a valid value; the method accepts an
        instance of a Variable class, and optionally a value override. If overridden,
        the provided value will override the value held within the Variable instance.
        The 'valid' method must be given a suitable implementation in all subclasses."""

        raise NotImplementedError(
            "The 'valid' method cannot be called on the abstract Validator base class!"
        )


class ValidatorOption(Validator):
    """The ValidatorOption class validates a configuration variable against its possible
    option values."""

    def __init__(self, options: list[object], typecast: bool = False, **kwargs):
        super().__init__(**kwargs)

        if not isinstance(options, list):
            raise TypeError("The 'options' argument must have a 'list' value!")
        elif len(options) == 0:
            raise ValueError("The 'options' argument must contain at least one option!")

        self._options = list(options)

        if not isinstance(typecast, bool):
            raise TypeError("The 'typecast' argument must have a boolean value!")

        self._typecast = typecast

    @property
    def options(self) -> list[object]:
        """Return the 'options' property value"""

        return self._options

    @options.setter
    @typing.final
    def options(self, options: list[object]):
        """The 'options' property can only be set via the constructor"""

        raise NotImplementedError(
            "The 'options' property value can only be set during class instantiation!"
        )

    @property
    def typecast(self) -> bool:
        """Return the 'typecast' property value"""

        return self._typecast

    @typecast.setter
    @typing.final
    def typecast(self, typecast: bool):
        """The 'typecast' property can only be set via the constructor"""

        raise NotImplementedError(
            "The 'typecast' property value can only be set during class instantiation!"
        )

    @property
    def typed(self) -> type:
        """Return the 'typed' property value"""

        typed: set[type] = set()

        for option in self._options:
            typed.add(type(option))

        if len(typed) > 1:
            raise TypeError("The options must all be of the same type!")

        return typed[0]

    @typed.setter
    def typed(self, typed: type):
        """The 'typed' property can only be set via the constructor"""

        raise NotImplementedError(
            "The 'typed' property value can only be set during class instantiation!"
        )

    def cast(self, source: object, target: type = None) -> object:
        """Support casting a source value to a target data type, where such type casting
        is possible and makes semantic sense."""

        if target is None:
            target = self.typed

        temp: object = None

        if isinstance(source, list):
            temp: list[object] = []

            for value in source:
                temp.append(self.cast(source=value, target=target))
        elif isinstance(source, dict):
            temp: dict[str, object] = {}

            for key, value in source.items():
                temp[key] = self.cast(source=value, target=target)
        elif isinstance(source, bool):
            if target is bool:
                temp = bool(source)
            elif target is str:
                temp = str(source)
            elif target is int:
                temp = int(source)
            elif target is float:
                temp = float(source)
            else:
                raise TypeError(
                    f"Unsupported typecasting between 'bool' and '{target.__name__}'!"
                )
        elif isinstance(source, int):
            if target is bool:
                temp = bool(source)
            elif target is str:
                temp = str(value)
            elif target is int:
                temp = int(source)
            elif target is float:
                temp = float(source)
            else:
                raise TypeError(
                    f"Unsupported typecasting between 'int' and '{target.__name__}'!"
                )
        elif isinstance(source, float):
            if target is bool:
                temp = bool(source)
            elif target is str:
                temp = str(source)
            elif target is int:
                temp = int(source)
            elif target is float:
                temp = float(source)
            else:
                raise TypeError(
                    f"Unsupported typecasting between 'float' and '{target.__name__}'!"
                )
        elif isinstance(source, str):
            if target is bool:
                temp = bool(source)
            elif target is str:
                temp = str(source)
            elif target is int:
                temp = int(source)
            elif target is float:
                temp = float(source)
            else:
                raise TypeError(
                    f"Unsupported typecasting between 'str' and '{target.__name__}'!"
                )
        else:
            raise TypeError(
                f"Unsupported typecasting between '{type(source)}' and '{target.__name__}'!"
            )

        return temp

    def valid(self, variable: _variable.Variable, value: object = None) -> bool:
        """Determine if the provided variable has a valid value; the method accepts an
        instance of a Variable class, and optionally a value override. If overridden,
        the provided value will override the value held within the Variable instance."""

        if not isinstance(variable, _variable.Variable):
            raise TypeError(
                "The 'variable' argument must reference a Variable class instance!"
            )

        value = value or variable.value

        if value is None:
            return self.nullable is True and self.required is False
        elif self.typecast is True:
            return self.cast(source=value) in self._options
        else:
            return value in self._options


class ValidatorRegex(Validator):
    """The ValidatorRegex class validates a configuration variable against a regular
    expression to ensure that its value conforms to the required expectations."""

    def __init__(self, pattern: re.Pattern | str, **kwargs):
        super().__init__(**kwargs)

        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        elif not isinstance(pattern, re.Pattern):
            raise TypeError(
                "The regular expression ('regex') must be provided as a 're.Pattern' instance or a valid regex string!"
            )

        self._pattern = pattern

    @property
    def pattern(self) -> re.Pattern:
        """Return the 'pattern' property value"""

        return self._pattern

    @pattern.setter
    @typing.final
    def pattern(self, pattern: re.Pattern):
        """The 'pattern' property can only be set via the constructor"""

        raise NotImplementedError(
            "The 'pattern' property value can only be set during class instantiation!"
        )

    def valid(self, variable: _variable.Variable, value: object = None) -> bool:
        """Determine if the provided variable has a valid value; the method accepts an
        instance of a Variable class, and optionally a value override. If overridden,
        the provided value will override the value held within the Variable instance."""

        if not isinstance(variable, _variable.Variable):
            raise TypeError(
                "The 'variable' argument must reference a Variable class instance!"
            )

        value = value or variable.value

        if value is None:
            return self.nullable is True and self.required is False
        elif isinstance(value, bool):
            value = "YES" if value else "NO"
        elif isinstance(value, (int, float)):
            value = str(value)
        elif not isinstance(value, str):
            raise TypeError(
                "The value must be provided as a string, integer, float or boolean for regular expression matching!"
            )

        return not self.pattern.match(value) is None
