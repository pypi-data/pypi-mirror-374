from envcfglib import Config

# Example: factories and defaults
config = Config()

# Load value that is not set in the environment, using a default
config.load_configuration("DEBUG", default="false")

# Retrieve as a boolean using a conversion factory at get-time
is_debug = config.get_value("DEBUG", factory=lambda x: str(x).lower() == "true")
print(f"DEBUG enabled: {is_debug}")

# Load another value, converting at load-time
config.load_configuration("RETRIES", factory=int, default=3)
print(f"Retries: {config.get_value('RETRIES')}  (type: {type(config.get_value('RETRIES')).__name__})")
