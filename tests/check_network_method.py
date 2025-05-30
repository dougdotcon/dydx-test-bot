"""
Check the Network.config_network method.
"""
import inspect
from v4_client_py.clients.constants import Network

# Get the signature of the config_network method
signature = inspect.signature(Network.config_network)

# Print the signature
print(f"Network.config_network signature: {signature}")

# Print the parameters
print("Parameters:")
for name, param in signature.parameters.items():
    print(f"  {name}: {param.default}")
