class ConfiguresError(RuntimeError):
    """The ConfiguresError exception is raised if an issue is detected with the setup or
    initialisation of the Configures library classes."""

    pass


class ConfigurationError(RuntimeError):
    """The ConfigurationError exception is raised if an issue is encountered with any of
    the secrets, such as if a required secret is missing or fails to pass its associated
    validation rules. The ConfigurationError exception is reserved exclusively for use
    to report errors with secrets rather than setup or initialisation of the library to
    make it easier to filter and catch such errors."""

    pass
