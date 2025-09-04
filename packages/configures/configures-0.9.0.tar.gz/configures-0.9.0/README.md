# Configures: Simplifies Configuration Access & Validation

The Configures library provides a streamlined interface for application configuration, validation and access.

The library provides support for specifying expected configuration options, often termed secrets, for an application, allowing for secrets to be marked as required or optional, along with the ability to define the "shape" of the value for each secret, either according to a regular expression or a list of acceptable values, as well as allowing a default fallback value to be specified that will be used if the secret is absent at runtime.

The Configures library also provides a streamlined and consistent interface to access secrets at runtime, including convenience functionality such as to dynamically cast values to different data types. Furthermore, secrets can be added and modified at runtime if needed.

### Requirements

The Configures library has been tested with Python 3.10, 3.11, 3.12 and 3.13. The library
has not been tested with, nor is it likely compatible with Python 3.9 and earlier.

### Installation

The Configures library is available from PyPI, so may be added to a project's dependencies
via its `requirements.txt` file or similar by referencing the Configures library's name,
`configures`, or the library may be installed directly into the local runtime environment
using `pip install` by running the following command:

	$ pip install configures

### Usage Example

To use the Configures library, simply import the library into your project and create an instance of the `Secrets` class. By default the `Secrets` class will import all of the secrets defined in the current runtime environment, and if a configuration specification file has been defined for the application, and if it exists either in one of the standard locations, or if the file's location has been provided to the `Secrets` class, it will load the configuration specification, and validate the secrets that are referenced in the specification against the configuration.

The `Secrets` class supports several ways of providing a configuration specification, and offers a range of methods for getting and temporarily setting or modifying secrets within an application at runtime.

See the [**Classes & Methods**](#classes-and-methods) section for more information about
the classes, methods and properties provided by the library.

```python
from configures import Secrets

secrets = Secrets()

print(secrets.get("MY_SECRET", default="<default fallback value>"))
```

### Methodology

The Configures library supports verifying that any required secrets exist, and optionally that their values are of the expected type and format as specified in the provided configuration specification file. Secrets can also be marked as optional and will only be validated if they are available.

The configuration specification file consists of a list of named secrets that *should* or *must* exist as well as optional regular expressions or lists of option values that define the acceptable format and values for each variable.

A configuration specification file may be provided in one of three supported formats:

 * a text file that provides a list of secrets and their corresponding specifications
 * a JSON file that provides a dictionary of secrets and their corresponding specifications
 * a YAML file that provides a dictionary of secrets and their corresponding specifications

By being able to provide a listing of the secrets used within an application, to noting which secrets are optional, as well as being able to specify the acceptable values in a concise way, runtime configuration can be validated to ensure it is within the expected range of the software during the very first steps of its initialisation, allowing for configuration issues to be highlighted at startup before any issues related to misconfiguration can occur.

<a id="classes-and-methods"></a>
### Classes & Methods

The Configures library provides several classes which are documented below along with their available methods and properties.

#### Secrets Class Methods & Properties

The `Secrets` class offers the following methods:

* `get(name: str, default: object = None)` (`object`) – The `get()` method provides support
for obtaining a named secret, if a matching secret exists, as well as providing support for returning a default fallback value if the named secret does not exist.

* `set(name: str, value: object)` – The `set()` method provides support for setting a
named secret on the `Secrets` class. The method expects the secret to have a name defined as a string along with the secret's value. If a matching secret already exists, its value will be overwritten with the provided value. The method returns a reference to `self` so that calls to `set()` may be chained with calls to other methods on the `Secrets` class.

* `require(name: str)` (`object`) – The `require()` method provides support for obtaining
a named secret value, ensuring that a matching secret exists. If no matching secret is
found, then a `ConfigurationError` exception will be raised.

* `empty(name: str, default: object = None)` (`bool`) – The `empty()` method supports
determining if the named secret has an empty value or not, returning `True` if it
does or `False` otherwise.

* `nonempty(name: str, default: object = None)` (`bool`) – The `nonempty()` method
supports determining if the named secret has an non-empty value or not, returning
`True` if it does or `False` otherwise.

* `null(name: str, default: object = None)` (`bool`) – The `null()` method provides
support for determining if the named secret has an "null" value or not; this is achieved by comparing the secret value against the configured class-level `sentinel` property value. If a match is found then this method returns `True` or `False` otherwise.

* `true(name: str, default: object = None)` (`bool`) – The `true()` method provides
support for determining if the named secret value has a truthy value or not; the truthy
values are configured at class-level and if a match is found between the current
configuration value and one of the truthy values, the method will return `True`, or `False`
otherwise; if the secret has not been specified in the application's configuration,
the default value, if specified, will be returned instead.

* `false(name: str, default: object = None)` (`bool`) – The `false()` method supports
determining if the named configuration value has a falsey value or not; the falsey values
are configured at class-level and if a match is found between the current configuration
value and one of the falsey values, the method will return True, or false otherwise; if
the secret has not been specified in the application's configuration, the default value,
if specified, will be returned instead.

* `int(name: str, default: object = None)` (`int`) – The `int()` method provides support
for returning the named secret cast to an `int` value, if the secret has been specified, otherwise the default value, if specified, will be returned instead.

* `float(name: str, default: object = None)` (`float`) – The `float()` method provides support
for returning the named secret cast to an `float` value, if the secret has been specified, otherwise the default value, if specified, will be returned instead.

* `combine(variables: list[str], separator: str = None, strip: bool = False)` (`str`) – The `combine()` method provides support for combining the string values from multiple secrets, joining parts with an optional separator character, and optionally stripping the separator character from the beginning and end of each secret value.

* `keys()` (`list[str]`) – The `keys()` method supports obtaining the keys for the secrets
currently held by the `Secrets` instance.

* `values()` (`list[object]`) – The `values()` method supports obtaining the values for
the secrets currently held by the `Secrets` instance.

* `items()` (`list[tuple[str, object]]`) – The `items()` method supports obtaining the
items for the secrets currently held by the `Secrets` instance.

* `update(**secrets: dict[str, object])` (`Secrets`) – The `update()` method supports
updating the secrets currently held by the `Secrets` instance. The method returns a
reference to `self` so calls to the `update()` method can be chained with calls to other
methods and or access to properties on the `Secrets` class.

The `Secrets` class offers the following properties:

* `configuration` (`Configuration`) – The `configuration` property provides access to the `Secret` class' associated `Configuration` class instance.

* `sentinel` (`object`) – The `sentinel` property provides access to the sentinel value,
if any, that was optionally set when the `Secrets` class was instantiated. This value can only be specified when the `Secrets` class is instantiated via the `sentinel` keyword argument, and is used when determining if any given secret has a "null" value by comparing the secret's value against the sentinel value.

The `Secrets` class also offers dictionary-style access to the secrets using standard
dictionary patterns for getting, setting, deleting, counting and checking existence:

```python
from configures import Secrets

secrets = Secrets(secrets=dict(TZ="Europe/Rome"))

assert len(secrets) == 1

# Checking if a secret exists or not:
assert "TZ" in secrets

# Accessing an existing secret (if the secret does not exist, a KeyError will be raised):
timezone = secrets["TZ"]

assert timezone == "Europe/Rome"

# Setting a secret (either a new secret, or to overwrite an existing secret's value):
secrets["TZ"] = "Europe/London"

assert secrets["TZ"] == "Europe/London"

# Deleting a secret (if the secret does not exist, a KeyError will be raised):
del secrets["TZ"]

# Getting a count of the current secrets:
assert len(secrets) == 0

# Checking if a secret exists or not:
assert not "TZ" in secrets
```

⚠️ Note: The same access caveats apply as with dictionary access in that if you reference
a key (a secret name) that does not exist, a `KeyError` will be raised both when trying
to get or delete a non-existent key.

#### Configuration Class Methods & Properties

The `Configuration` class offers the following methods:

* `validate(secrets: Secrets)` (`generator`) – The `validate()` method provides support
for validating the provided secrets with the provided configuration specification. The
validation step ensures that each secret that has been referenced in the configuration
specification passes the validation rules, including ensuring that required secrets are
present, and that values conform to any defined regular expression or options list
validation.

The `Configuration` class offers the following properties:

* `specification` (`Specification`) – The `specification` property returns a reference
to the `Specification` class instance that holds the parsed specification provided when
the `Configuration` class was instantiated.

#### Specification Class Methods & Properties

The `Specification` class offers the following methods:

* `update(**specifications: dict[str, Variable])` – The `update()` method supports
updating the secrets specifications held by the Specification instance.

* `copy()` (`dict[str, Variable]`) – The `copy()` method supports copying the secrets
specifications held by the Specification instance.

* `keys()` (`list[str]`) – The `keys()` method supports obtaining the keys for the
secrets specification held by the Specification instance.

* `values()` (`list[str]`) – The `values()` method supports obtaining the values for the
secrets specification held by the Specification instance.

* `items()` (`generator`) – The `items()` method supports obtaining the items for the
secrets specification held by the Specification instance via a generator.

The `Specification` class also offers dictionary-style access to the secrets specifications
using standard dictionary patterns for getting, counting and checking for existence. The
class does not allow secrets specifications to be modified, so dictionary-style setting,
deleting or clearing of secrets specifications are not supported and will raise an error.

```python
from configures import Secrets

secrets = Secrets()

# Accessing a secret specification (`None` will be returned for a non-existent spec):
specification = secrets.configuration.specification["TZ"]

# Checking if a secret specification exists:
assert not "OTHER" in secrets.configuration.specification
```

#### Validator Class Methods & Properties

The `Validator` class offers the following methods:

* `valid(variable: Variable, value: object = None)` – The `valid()` method determines if
the provided variable has a valid value according to the specified secrets specification
for the variable, if one has been provided; the method accepts an instance of a `Variable`
class, and optionally a `value` override. If provided, the `value` argument will override
the value held within the `Variable` instance.

The `Validator` class offers the following properties:

* `required` (`bool`) – The `required` property returns the `required` property value.
* `nullable` (`bool`) – The `nullable` property returns the `nullable` property value.

#### ValidatorOption Class Methods & Properties

The `ValidatorOption` class offers the following methods:

* `cast(source: object, target: type = None)` – The `cast()` method supports casting a
source value to a target data type, where such type casting is possible and makes sense;
when no semantically sensible type casting exists between the provided source value and
the specified target data type, a `TypeError` exception will be raised.

* `valid(variable: Variable, value: object = None)` – The `valid()` method determines if
the provided variable has a valid value according to the specified secrets specification
for the variable, if one has been provided; the method accepts an instance of a `Variable`
class, and optionally a `value` override. If provided, the `value` argument will override
the value held within the `Variable` instance.

The `ValidatorOption` class offers the following properties:

* `options` (`list[str]`) – The `options` property returns the accepted secret options,
as defined in the secrets specification for the associated secret.

* `typecast` (`bool`) – The `typecast` property returns whether the secret value can be
type cast or not.

* `typed` (`type`) – The `typed` property returns the data type of the options values.

#### ValidatorRegex Class Methods & Properties

The `ValidatorRegex` class offers the following methods:

* `valid(variable: Variable, value: object = None)` – The `valid()` method determines if
the provided variable has a valid value according to the specified secrets specification
for the variable, if one has been provided; the method accepts an instance of a `Variable`
class, and optionally a `value` override. If provided, the `value` argument will override
the value held within the `Variable` instance.

The `ValidatorRegex` class offers the following properties:

* `pattern` (`re.Pattern`) – The `pattern` property provides access to the regular expression
pattern as defined in the secrets specification for the associated secret.

#### Variable Class Methods & Properties

The `Variable` class offers the following methods:

* `validate(value: object = None)` (`bool`) – The `validate()` method validates the
`Variable` class's value via the associated `Validator` instance, returning `True` if
the variable passes the validation defined in the secrets specification, or `False` if
it does not.

The `Variable` class offers the following properties:

* `name` (`str`) – The `name` property returns the name of the variable.

* `validator` (`Validator`) – The `validator` property returns the `Validator` class
instance that is associated with the variable.

* `value` (`object`) – The `value` property returns the value, if any, of the variable.

* `default` (`object`) – The `default` property returns the default, if any, of the variable.

<a id="specification"></a>
### Configuration Specifications

The configuration specification files consists of a list of named secret that *should* or *must* exist as well as optional regular expressions that define the acceptable format and values for each configuration option.

A configuration specification file may be provided in one of three supported formats: an
`.env` style file that lists one secret per line and its corresponding specification; a
JSON file that provides a dictionary of secrets and their corresponding specifications, or a
YAML file that provides a dictionary of secrets and their corresponding specifications.

### Configuration Specification: Environment Variable-Style File

Configuration specifications provided using an `.env` style file must use the format
noted below where each line represents a named secret and its corresponding specification.
Each line must adhere to the format noted below. Lines starting with a `#` character are considered to be comments and are ignored:

```shell
[<optional?>]<secret-name>=(<regex>)[<optional-default-value>]
```

Where `<secret-name>` is the name of the secret as set in the environment and as specified in the application or package software; the names of secrets are usually capitalised, but this is a convention rather than a requirement, and will depend upon the style guidelines of the application or package that is making use the configuration options in question.

The `[<optional?>]` flag notes if a secret is optional for the application; this is noted by prefixing the secret's name with a question mark (`?`) character – required secrets must be listed in the file without the optional flag.

Following the secret's name, a regular expression can be provided which will be used to validate the format and optionally the accepted values of the secret; if no regular expression is provided, only the presence of the secret will be checked, and unless it is marked as being optional, a `ConfigurationError` will be raised if it is not available in the current runtime environment.

Finally the `[<optional-default-value>]` can be used to specify an optional default for
the secret if the secret has not been defined in the current runtime environment.

Below is an example highlighting the structure of a possible rule:

```shell
?TZ=([A-Za-z]+(_[A-Za-z]+)?/[A-Za-z_]+(_[A-Za-z])?)[America/Los_Angeles]
```

The rule specifies that the `TZ` secret is optional as the line starts with a `?` character, but if it is specified, its value must consist of at least one of characters `A-Z` or `a-z`, optionally followed by one or more additional characters from the range `A-Z`, `a-z` and `_`, then followed by a required `/` separator character which must then be followed by one or more of the characters `A-Z`, `a-z`, optionally followed by one or more of the characters `A-Z`, `a-z` and `_`, such that a value like `America/New_York` would be considered valid, whereas a value like `123` or `America` would not.

As this rule also specifies an optional default value of `America/Los_Angeles`, if the `TZ` secret has not been defined in the current runtime environment, the default value will be applied to the current environment's configuration instead.

The regular expression rules can also be used to specify a range of fixed values such as `YES` and `NO` with a rule similar to the following:

```shell
?SOME_FEATURE_FLAG=(YES|NO)[NO]
```

### Configuration Specification: JSON File

JSON configuration validation specification files must conform to the following format
with one or more nested JSON dictionaries expressed according to the pattern below:

```json
{
    "<secret-name>": {
        "optional": "<optional>",
        "nullable": "<nullable>",
        "validate": {
            "pattern": "<pattern>"
        },
        "default": "<default>"
    },
    "<secret-name>": {
        "optional": "<optional>",
        "nullable": "<nullable>",
        "validate": {
            "options": [
                "RED",
                "GREEN",
                "BLUE"
            ]
        },
        "default": "<default>"
    }
}
```

Each block must note the configuration variable name to which it applies, and each secret should only be named once, otherwise the last instance will be used. The `<secret-name>` expressed as a string must match the name of the secret as held in the secrets and as used in the software.

The validation specification for the secret is then detailed within the block.

The `<optional>` (`boolean`) flag notes if a secret is optional or not; this is specified by providing the `optional` key with a boolean value of `true` if the associated secret is optional, and thus does not need specifying in the secrets. For required secrets, the `optional` key can either be omitted from the specification for the secret, or it must have a `false` value.

The `<nullable>` (`boolean`) flag notes if a secret's value can hold a `null` (`None`) value or not; this is specified by providing the `nullable` key with a boolean value of `true`. The `nullable` key only needs specifying for secrets that are nullable; for non-nullable secrets, the `nullable` key can either be omitted from the specification for the secret, or must have a `false` value.

In order to validate the value of a secret, the library currently provides the following validation mechanisms:

    * regular expression matching
    * basic options list matching

To validate the value of a secret, at least one of the validation mechanisms must be configured via the `validate` key for the relevant secret.

To use regular expression matching, a regular expression must be provided under the
`validate.pattern` key-path for the relevant variable. The regular expression must be
written so that it matches against the valid options for the secret.

To use basic options list matching, a list of one or more accepted option values,
must be provided via the `validate.options` key-path for the relevant secret.

Each secret will be validated through the validation mechanisms that have been defined for it in the specification. One should ensure the validations are compatible with each other – that is that a secret value will either match or fail to match through all of the validation mechanisms defined for a given secret. A validation regular expression for example should not result in a match when the corresponding options list match would fail or vice-versa.

If no validation mechanism are defined for a given secret, only the presence of the configuration variable will be checked, and unless it is marked as being optional, a `ConfigurationError` will be raised if it has not been defined.

An example JSON-serialised secrets specification may look something like the following:

```json
{
    "TIMEZONE": {
        "optional": false,
        "nullable": false,
        "validate": {
            "pattern": "[A-Z]{1}[A-Za-z]+/[A-Za-z_]+(_[A-Za-z])?"
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
```

### Configuration Specification: YAML File

YAML configuration validation specification files must conform to the following format with one or more nested YAML dictionaries expressed according to the pattern below:

```yaml
<secret-name>:
  optional: <optional>
  nullable: <nullable>
  validate:
    pattern: <pattern>
  default: <default>

<secret-name>:
  optional: <optional>
  nullable: <nullable>
  validate:
    options:
      - '1'
      - '2'
      - '3'
  default: <default>
```

Each block must note the secret's name to which it applies, and each configuration variable should only be named once, otherwise the last instance will be used. The `<secret-name` expressed as a string must match the name of the secret as held in the secrets and as used in the software.

The validation specification for the secret is then detailed within the block.

The `<optional>` (`boolean`) flag notes if a secret is optional or not; this is specified by providing the `optional` key with a boolean value of `true` if the associated secret is optional, and thus does not need specifying in the secrets. For required secrets, the `optional` key can either be omitted from the specification for the variable, or it must have a `false` value.

The `<nullable>` (`boolean`) flag notes if a secret's value can hold a `null` (`None`) value or not; this is specified by providing the `nullable` key with a boolean value of `true`. The `nullable` key only needs specifying for secrets that are nullable; for non-nullable variables, the `nullable` key can either be omitted from the specification for the secret, or must have a `false` value.

In order to validate the value of a configuration variable, the library currently provided the following validation mechanisms:

    * regular expression matching
    * basic options list matching

To validate the value of a secret, at least one of the validation mechanisms must be configured via the `validate` key for the relevant secret.

To use regular expression matching, a regular expression must be provided under the
`validate.pattern` key-path for the relevant variable. The regular expression must be
written so that it matches against the valid options for the secret.

To use basic options list matching, a list of one or more accepted option values,
must be provided via the `validate.options` key-path for the relevant secret.

Each secret will be validated through the validation mechanisms that have been defined for it in the specification. One should ensure the validations are compatible with each other – that is that a configuration variable value will either match or fail to match through all of the validation mechanisms defined for a given variable. A validation regular expression for example should not result in a match when the corresponding options list match would fail or vice-versa.

If no validation mechanism are defined for a given secret, only the presence of the secret will be checked, and unless it is marked as being optional, a `ConfigurationError` will be raised if it has not been defined.

An example configuration variable specification may look something like the following:

```yaml
TIMEZONE:
  optional: false
  nullable: false
  validate:
    pattern: '[A-Z]{1}[A-Za-z]+/[A-Za-z_]+(_[A-Za-z])?'
  default: America/Los_Angeles

UI_COLOR_THEME:
  optional: true
  nullable: false
  validate:
    pattern: '[A-Z]{1}([a-z]{1,})?/[A-Z]{1}([a-z]{1,})?'
    options:
      - Grey/Blue
      - Grey/Orange
      - Grey/Red
  default: Grey/Blue
```

### Unit Tests

The Configures library includes a suite of comprehensive unit tests which ensure that
the library functionality operates as expected. The unit tests were developed with and
are run via `pytest`.

To ensure that the unit tests are run within a predictable runtime environment where all
of the necessary dependencies are available, a [Docker](https://www.docker.com) image is
created within which the tests are run. To run the unit tests, ensure Docker and Docker
Compose is [installed](https://docs.docker.com/engine/install/), and perform the
following commands, which will build the Docker image via `docker compose build` and
then run the tests via `docker compose run` – the output the tests will be displayed:

```shell
$ docker compose build
$ docker compose run tests
```

To run the unit tests with optional command line arguments being passed to `pytest`,
append the relevant arguments to the `docker compose run tests` command, as follows, for
example passing `-v` to enable verbose output and `-s` to print standard output:

```shell
$ docker compose run tests -v -s
```

See the documentation for [PyTest](https://docs.pytest.org/en/latest/) regarding
available optional command line arguments.

### Copyright & License Information

Copyright © 2023–2025 Daniel Sissman; licensed under the MIT License.