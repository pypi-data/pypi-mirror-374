"""
Módulo de movimientos oscilatorios
"""

from .movimiento_armonico_simple import MovimientoArmonicoSimple
from .movimiento_armonico_complejo import MovimientoArmonicoComplejo

# Alias para compatibilidad con los tests
mac = movimiento_armonico_complejo

__all__ = ["MovimientoArmonicoSimple", "MovimientoArmonicoComplejo", "mac"]
