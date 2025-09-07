from envcfglib import Config
import os

# Example: multiple instances (singleton per key)
app1 = Config("app1")
app2 = Config("app2")

# Simulate environment
os.environ["APP1_VAR"] = "alpha"
os.environ["APP2_VAR"] = "beta"

app1.load_configuration("APP1_VAR")
app2.load_configuration("APP2_VAR")

print("app1 -> APP1_VAR:", app1.get_value("APP1_VAR"))
print("app2 -> APP2_VAR:", app2.get_value("APP2_VAR"))

# Instances can access all loaded keys
print("app1 sees APP2_VAR:", app1.get_value("APP2_VAR"))
print("app2 sees APP1_VAR:", app2.get_value("APP1_VAR"))
