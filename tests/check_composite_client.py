"""
Check the CompositeClient class signature.
"""
import inspect
from v4_client_py.clients import CompositeClient

# Get the signature of the CompositeClient constructor
signature = inspect.signature(CompositeClient.__init__)

# Print the signature
print(f"CompositeClient.__init__ signature: {signature}")

# Print the parameters
print("Parameters:")
for name, param in signature.parameters.items():
    print(f"  {name}: {param.default}")
