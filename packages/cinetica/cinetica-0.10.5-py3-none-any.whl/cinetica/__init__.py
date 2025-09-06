"""
Cinetica - Una librería para cálculos de cinemática
"""

__version__ = "0.10.5"

from .cinematica import (
    circular,
    espacial,
    oscilatorio,
    parabolico,
    rectilineo,
    relativo,
    graficos,
)

__all__ = [
    "circular",
    "espacial",
    "oscilatorio",
    "parabolico",
    "rectilineo",
    "relativo",
    "graficos",
    "__version__",
]
