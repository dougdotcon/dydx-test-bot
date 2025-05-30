"""
Check the Network class.
"""
import inspect
from v4_client_py.clients.constants import Network

# Print the Network class
print(f"Network class: {Network}")

# Print the attributes of the Network class
print("Network attributes:")
for attr in dir(Network):
    if not attr.startswith('__'):
        value = getattr(Network, attr)
        print(f"  {attr}: {value}")
