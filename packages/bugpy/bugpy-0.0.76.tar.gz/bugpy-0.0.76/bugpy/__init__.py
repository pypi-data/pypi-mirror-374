from .db_manager import Connection
from importlib.metadata import version

__version__ = version("bugpy")
print(f"Loaded bugpy version v{__version__}")

