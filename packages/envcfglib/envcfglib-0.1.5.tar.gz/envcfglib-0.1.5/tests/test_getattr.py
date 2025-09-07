import os
import pytest
from unittest.mock import patch

from envcfglib.config import Config


def setup_function(function):
    # Reset class-level state to avoid cross-test interference
    Config._instances = {}
    Config._loaded_configuration = {}


def test_dunder_getattr_returns_loaded_value():
    config = Config()
    with patch.dict(os.environ, {"FOO": "bar"}):
        config.load_configuration("FOO")
    # Access via attribute should mirror get_value
    assert config.FOO == "bar"


def test_dunder_getattr_raises_keyerror_for_missing_key():
    config = Config()
    with pytest.raises(KeyError):
        # __getattr__ is only called for missing attributes; expecting KeyError from _get_value
        _ = config.MISSING_KEY


def test_dunder_getattr_with_prefix():
    cfg = Config("APP")
    with patch.dict(os.environ, {"APP_PORT": "8080"}):
        cfg.load_configuration("PORT", factory=int)
    # Access as attribute name without prefix
    assert cfg.PORT == 8080
