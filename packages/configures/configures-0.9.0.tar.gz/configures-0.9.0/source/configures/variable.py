from __future__ import annotations

import typing

from configures.logging import logger
from configures import validator as _validator

logger = logger.getChild(__name__)


class Variable(object):
    """The Variable class represents a configuration variable including its unique name,
    its associated Validator class, and its default fallback value if-any."""

    def __init__(
        self,
        name: str,
        validator: _validator.Validator,
        value: object = None,
        default: object = None,
    ):
        if not (isinstance(name, str) and len(name := name.strip()) > 0):
            raise TypeError("The 'name' argument must have a non-empty string value!")

        if not isinstance(validator, _validator.Validator):
            raise TypeError(
                "The 'validator' argument must have a Validator instance value!"
            )

        self._name: str = name
        self._validator: _validator.Validator = validator
        self._value: object = value
        self._default: object = default

    @property
    def name(self) -> str:
        """Return the 'name' property value associated with this Variable"""

        return self._name

    @name.setter
    @typing.final
    def name(self, name: str):
        """The 'name' property can only be set via the constructor"""

        raise NotImplementedError(
            "The 'name' property value can only be set during class instantiation!"
        )

    @property
    def validator(self) -> _validator.Validator:
        """Return the Validator instance associated with this Variable"""

        return self._validator

    @validator.setter
    @typing.final
    def validator(self, value: _validator.Validator):
        """The 'validator' property can only be set via the constructor"""

        raise NotImplementedError(
            "The 'validator' property value can only be set during class instantiation!"
        )

    @property
    def value(self) -> object:
        """Return the 'value' property value associated with this Variable"""

        return self._value

    @value.setter
    @typing.final
    def value(self, value: object):
        """The 'value' property can only be set via the constructor"""

        raise NotImplementedError(
            "The 'value' property value can only be set during class instantiation!"
        )

    @property
    def default(self) -> object:
        """Return the 'default' property value"""

        return self._default

    @default.setter
    @typing.final
    def default(self, default: object):
        """The 'default' property can only be set via the constructor"""

        raise NotImplementedError(
            "The 'default' property value can only be set during class instantiation!"
        )

    def validate(self, value: object = None) -> bool:
        """Validate the Variable's value via the associated Validator instance"""

        return self.validator.valid(variable=self, value=value) is True
