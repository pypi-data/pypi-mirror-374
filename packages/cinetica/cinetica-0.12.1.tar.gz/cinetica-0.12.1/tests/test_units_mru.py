import pytest
from cinetica.cinematica.rectilineo.movimiento_rectilineo_uniforme import MovimientoRectilineoUniforme
from cinetica.units import ureg, Q_

def test_mru_posicion_with_units():
    mru = MovimientoRectilineoUniforme(posicion_inicial=10 * ureg.meter, velocidad_inicial=5 * ureg.meter / ureg.second)
    pos = mru.posicion(2 * ureg.second)
    assert pos == 20 * ureg.meter

def test_mru_posicion_without_units():
    mru = MovimientoRectilineoUniforme(posicion_inicial=10, velocidad_inicial=5)
    pos = mru.posicion(2)
    assert pos == 20 * ureg.meter

def test_mru_velocidad_with_units():
    mru = MovimientoRectilineoUniforme(posicion_inicial=10 * ureg.meter, velocidad_inicial=5 * ureg.meter / ureg.second)
    vel = mru.velocidad()
    assert vel == 5 * ureg.meter / ureg.second

def test_mru_velocidad_without_units():
    mru = MovimientoRectilineoUniforme(posicion_inicial=10, velocidad_inicial=5)
    vel = mru.velocidad()
    assert vel == 5 * ureg.meter / ureg.second

def test_mru_aceleracion_with_units():
    mru = MovimientoRectilineoUniforme()
    acc = mru.aceleracion()
    assert acc == 0.0 * ureg.meter / ureg.second**2

def test_mru_aceleracion_without_units():
    mru = MovimientoRectilineoUniforme()
    acc = mru.aceleracion()
    assert acc == 0.0 * ureg.meter / ureg.second**2
