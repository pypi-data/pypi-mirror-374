"""
Cinetica - Una librería para cálculos de cinemática
"""

__version__ = "0.18.0"

from .units import ureg, Q_

from .cinematica import (
    circular,
    espacial,
    oscilatorio,
    parabolico,
    rectilineo,
    relativo,
)
from . import graficos
from . import dinamica

__all__ = [
    "circular",
    "espacial",
    "oscilatorio",
    "parabolico",
    "rectilineo",
    "relativo",
    "graficos",
    "dinamica",
    "__version__",
]
