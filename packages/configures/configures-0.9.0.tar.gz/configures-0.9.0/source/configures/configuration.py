from __future__ import annotations

import typing

from configures.logging import logger
from configures.exceptions import ConfigurationError
from configures import specification as _specification
from configures import secrets as _secrets

logger = logger.getChild(__name__)


class Configuration(object):
    """The Configuration class validates and enforces the expected configuration for the
    associated codebase by reading the provided configuration specification file which
    specifies environment variables that should or must exist, as well as the acceptable
    values for each environment variable, specified via a regular expression.

    If any variation is found between the expected and found environment configurations,
    a ConfigurationError exception will be raised until any configuration issues are
    rectified. This ensures that the configuration is within the expected parameters."""

    @typing.final
    def __init__(self, *args, specification: _specification.Specification, **kwargs):
        if not isinstance(specification, _specification.Specification):
            raise TypeError(
                "The 'specification' argument must have a Specification class instance value!"
            )

        self._specification = specification

    @property
    def specification(self) -> _specification.Specification:
        """Return the 'specification' property Specification value"""

        return self._specification

    @specification.setter
    def specification(self, specification: _specification.Specification):
        """The 'specification' property can only be set via the constructor"""

        raise NotImplementedError(
            "The 'specification' property value can only be set during class instantiation!"
        )

    @typing.final
    def validate(
        self,
        secrets: _secrets.Secrets,
    ) -> typing.Generator[tuple[str, object], None, None]:
        """The validate method provides support for validating the provided secrets with
        the provided configuration specification. The validation step ensures that each
        secret that has been referenced in the configuration specification passes the
        validation rules, including ensuring that required secrets are present, and that
        values conform to any defined regular expression or options list validation."""

        logger.debug("%s.validate(secrets: %s)" % (self.__class__.__name__, secrets))

        if not isinstance(secrets, _secrets.Secrets):
            raise TypeError(
                "The 'secrets' argument must have a Secrets class instance value!"
            )

        for name, variable in self.specification.items():
            logger.debug(" >>> %s => %s (%s)" % (name, variable, variable.default))

            if not name in secrets:
                if not variable.default is None:
                    logger.debug(" >>>> (found default)")

                    yield (name, variable.default)
                elif variable.validator.required is True:
                    logger.debug(" >>>> (no default for required variable)")

                    raise ConfigurationError(
                        "The required environment variable, '%s', has not been configured!"
                        % (name)
                    )
                else:
                    logger.debug(" >>>> (no default for non-required variable)")
            elif variable.validate(value=secrets[name]) is False:
                raise ConfigurationError(
                    "The required environment variable, '%s', has an unexpected value, '%s', and must match the its specification!"
                    % (name, secrets[name])
                )
            else:
                yield (name, secrets[name])
