import os
import pytest
from unittest.mock import patch

from envcfglib.config import Config


class TestConfig:
    def setup_method(self):
        # Reset the Config class state before each test
        Config._instances = {}
        Config._loaded_configuration = {}

    def test_singleton_pattern(self):
        """Test that Config implements the singleton pattern correctly."""
        # Create two instances with the same key
        config1 = Config("test_key")
        config2 = Config("test_key")

        # They should be the same instance
        assert config1 is config2

        # Create an instance with a different key
        config3 = Config("different_key")

        # It should be a different instance
        assert config1 is not config3

    def test_init_creates_empty_configuration(self):
        """Test that initializing a Config creates an empty configuration dict."""
        Config("test_key")
        assert "test_key" in Config._loaded_configuration
        assert Config._loaded_configuration["test_key"] == {}

    @patch.dict(os.environ, {"TEST_ENV_VAR": "test_value"})
    def test_load_configuration_from_env(self):
        """Test loading configuration from environment variables."""
        config = Config()
        config.load_configuration("TEST_ENV_VAR")

        assert config._loaded_configuration["TEST_ENV_VAR"] == "test_value"

    @patch.dict(os.environ, {"TEST_INT_VAR": "42"})
    def test_load_configuration_with_factory(self):
        """Test loading configuration with a factory function."""
        config = Config()
        config.load_configuration("TEST_INT_VAR", factory=int)

        assert config._loaded_configuration["TEST_INT_VAR"] == 42

    def test_load_configuration_with_default(self):
        """Test loading configuration with a default value when env var is not set."""
        config = Config()
        config.load_configuration("NON_EXISTENT_VAR", default="default_value")

        assert config._loaded_configuration["NON_EXISTENT_VAR"] == "default_value"

    def test_load_configuration_missing_raises_error(self):
        """Test that loading a missing configuration without default raises KeyError."""
        config = Config()

        with pytest.raises(KeyError):
            config.load_configuration("NON_EXISTENT_VAR")

    @patch.dict(os.environ, {"TEST_ENV_VAR": "test_value"})
    def test_get_value(self):
        """Test retrieving a loaded configuration value."""
        config = Config()
        config.load_configuration("TEST_ENV_VAR")

        value = config.get_value("TEST_ENV_VAR")
        assert value == "test_value"

    @patch.dict(os.environ, {"TEST_ENV_VAR": "42"})
    def test_get_value_with_factory(self):
        """Test retrieving a value with a factory function."""
        config = Config()
        config.load_configuration("TEST_ENV_VAR")

        value = config.get_value("TEST_ENV_VAR", factory=int)
        assert value == 42

    def test_get_value_missing_raises_error(self):
        """Test that getting a missing value raises KeyError."""
        config = Config()

        with pytest.raises(KeyError):
            config.get_value("NON_EXISTENT_VAR")

    @patch.dict(os.environ, {"TEST_BOOL_VAR": "true"})
    def test_complex_type_conversion(self):
        """Test more complex type conversion scenarios."""
        config = Config()

        # Load with string factory (default)
        config.load_configuration("TEST_BOOL_VAR")
        assert config.get_value("TEST_BOOL_VAR") == "true"

        # Convert during retrieval
        bool_value = config.get_value(
            "TEST_BOOL_VAR", factory=lambda x: x.lower() == "true"
        )
        assert bool_value is True

    def test_multiple_config_instances(self):
        """Test using multiple config instances with different prefixes."""
        config1 = Config("app1")
        config2 = Config("app2")

        with patch.dict(
            os.environ, {"APP1_VAR": "app1_value", "APP2_VAR": "app2_value"}
        ):
            config1.load_configuration("APP1_VAR")
            config2.load_configuration("APP2_VAR")

            assert config1.get_value("APP1_VAR") == "app1_value"
            assert config2.get_value("APP2_VAR") == "app2_value"

            # All config instances can access all loaded configuration values
            # regardless of which instance loaded them
            assert config1.get_value("APP2_VAR") == "app2_value"
            assert config2.get_value("APP1_VAR") == "app1_value"
