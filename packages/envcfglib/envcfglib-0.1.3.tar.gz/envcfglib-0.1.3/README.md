# envcfglib

A simple library to load configuration from environment variables.

## Installation

This package targets Python 3.12+.

```
pip install envcfglib
```

## Quick start

Load values from the environment with optional conversion (factory) and defaults.

```python
from envcfglib import Config

config = Config()

# Load an integer value from the environment (raises if missing)
# export APP_PORT=8080
config.load_configuration("APP_PORT", factory=int)

# Retrieve the value (already converted by the factory at load-time)
port = config.get_value("APP_PORT")
print(port)  # e.g., 8080
```

## Factories and defaults

You can control conversion either when loading or when retrieving.

```python
from envcfglib import Config

config = Config()

# Provide a default if the variable is not set
config.load_configuration("DEBUG", default="false")

# Convert when getting the value
is_debug = config.get_value("DEBUG", factory=lambda x: str(x).lower() == "true")
print(is_debug)  # False

# Or convert during load
config.load_configuration("RETRIES", factory=int, default=3)
print(config.get_value("RETRIES"))  # 3
```

## Multiple instances

Config implements a singleton-per-key pattern. Creating instances with different keys
allows you to conceptually group configuration, but all loaded values are accessible
from any instance.

```python
from envcfglib import Config

app1 = Config("APP1")
app2 = Config("APP2")

# Suppose these are in the environment
# export APP1_VAR=alpha
# export APP2_VAR=beta

app1.load_configuration("VAR")
app2.load_configuration("VAR")

print(app1.get_value("VAR"))  # alpha
print(app2.get_value("VAR"))  # beta
```
