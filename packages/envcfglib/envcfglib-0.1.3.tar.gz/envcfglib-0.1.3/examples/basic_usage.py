from envcfglib import Config
import os

# Example: basic usage
# Set an environment variable for the sake of the example
os.environ["APP_PORT"] = "8080"

config = Config()
config.load_configuration("APP_PORT", factory=int)

port = config.get_value("APP_PORT")
print(f"Port: {port}  (type: {type(port).__name__})")
