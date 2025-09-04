import configures


def test_configures_with_file_specification(path: callable):
    """Test the library with a plain-text specification file."""

    specification = path("specifications/sample.spec")

    assert isinstance(specification, str)

    secrets = configures.Secrets(
        configuration=configures.Configuration(
            specification=configures.SpecificationFile(
                filename=specification,
            ),
        ),
    )

    assert isinstance(secrets, configures.Secrets)

    assert "TZ" in secrets
    assert isinstance(secrets["TZ"], str)
    assert secrets["TZ"] == "Somewhere/There"


def test_configures_with_json_specification(path: callable):
    """Test the library with a JSON-serialised specification file."""

    specification = path("specifications/sample.json")

    assert isinstance(specification, str)

    secrets = configures.Secrets(
        configuration=configures.Configuration(
            specification=configures.SpecificationFileJSON(
                filename=specification,
            ),
        ),
    )

    assert isinstance(secrets, configures.Secrets)

    assert "TZ" in secrets
    assert isinstance(secrets["TZ"], str)
    assert secrets["TZ"] == "Somewhere/There"


def test_configures_with_yaml_specification(path: callable):
    """Test the library with a YAML-serialised specification file."""

    specification = path("specifications/sample.yaml")

    assert isinstance(specification, str)

    secrets = configures.Secrets(
        configuration=configures.Configuration(
            specification=configures.SpecificationFileYAML(
                filename=specification,
            ),
        ),
    )

    assert isinstance(secrets, configures.Secrets)

    assert "TZ" in secrets
    assert isinstance(secrets["TZ"], str)
    assert secrets["TZ"] == "Somewhere/There"
