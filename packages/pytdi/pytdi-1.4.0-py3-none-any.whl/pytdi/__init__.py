"""PyTDI module."""

from importlib.metadata import PackageNotFoundError, metadata, version

from .core import LISAClockCorrection, LISATDICombination, TDICombination
from .interface import Data

try:
    __version__ = version(__name__)
    __license__ = metadata(__name__)["license"]
except PackageNotFoundError:
    __version__ = "0.0.0"  # Fallback for development mode
    __license__ = "Undefined"

__copyright__ = (
    "2021, Max Planck Institute for Gravitational Physics "
    "(Albert Einstein Institute) and California Institute of Technology"
)
