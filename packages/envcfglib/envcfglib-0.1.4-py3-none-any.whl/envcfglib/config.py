from os import environ
from typing import Any, Self
from collections.abc import Callable

__all__ = [
    "Config",
]


class Config:
    _instances: dict[str, Self] = dict()

    _loaded_configuration: dict[str, dict[str, Any]] = dict()
    _key_prefix: str = ""

    def __init__(self, key: str = ""):
        """
        Initialize the Config instance with a specific key prefix.
        Args:
            key (str): The prefix key for the configuration instance.
        """
        self._key_prefix = key
        self._loaded_configuration[key] = dict()

    def __new__(cls, key: str = "", *args, **kwargs) -> Self:
        """Singleton pattern implementation to ensure one instance per prefix key."""
        if key not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[key] = instance
        return cls._instances[key]

    def __getattr__(self, name: str):
        return self._get_value(name)

    def _get_value(self, key: str) -> Any:
        return self._loaded_configuration[self._key_prefix][key]

    def _set_value(self, key: str, value: Any) -> None:
        self._loaded_configuration[self._key_prefix][key] = value

    def _get_environ_key(self, key: str) -> str:
        if self._key_prefix:
            return f"{self._key_prefix}_{key}".upper()
        return key.upper()

    def load_configuration(
        self,
        key: str,
        *,
        factory: Callable[[str], Any] = str,
        default: Any | None = None,
    ) -> None:
        """
        Load a configuration value from environment variables.

        Args:
            key: The environment variable key to load.
            factory: A factory function to convert the string value to the desired type.
            default: A default value to use if the environment variable is not set.

        Returns:
            None

        Raises:
            KeyError: If the environment variable is not set and no default is provided.
        """
        try:
            val = environ[self._get_environ_key(key)]
        except KeyError:
            if default is None:
                raise
            self._set_value(key, default)
        else:
            self._set_value(key, factory(val))

    def get_value(
        self, key: str, *, factory: Callable[[Any], Any] | None = None
    ) -> Any:
        """
        Retrieve a loaded configuration value, optionally applying a factory function.

        Args:
            key: The key of the configuration value to retrieve.
            factory: A factory function to convert the value to the desired type.

        Returns:
            The requested value. If a factory is provided, the value is processed through it before returning.

        Raises:
            KeyError: If the key is not found in the loaded configuration.
        """
        val = self._get_value(key)

        if factory is None:
            return val

        return factory(val)
