import pytest
from cinetica.cinematica.rectilineo.movimiento_rectilineo_uniformemente_variado import MovimientoRectilineoUniformementeVariado
from cinetica.units import ureg, Q_

def test_mruv_posicion_with_units():
    mruv = MovimientoRectilineoUniformementeVariado(
        posicion_inicial=10 * ureg.meter,
        velocidad_inicial=5 * ureg.meter / ureg.second,
        aceleracion_inicial=2 * ureg.meter / ureg.second**2
    )
    pos = mruv.posicion(2 * ureg.second)
    assert pos == (10 + 5*2 + 0.5*2*2**2) * ureg.meter # 10 + 10 + 4 = 24

def test_mruv_posicion_without_units():
    mruv = MovimientoRectilineoUniformementeVariado(
        posicion_inicial=10,
        velocidad_inicial=5,
        aceleracion_inicial=2
    )
    pos = mruv.posicion(2)
    assert pos == (10 + 5*2 + 0.5*2*2**2) * ureg.meter

def test_mruv_velocidad_with_units():
    mruv = MovimientoRectilineoUniformementeVariado(
        posicion_inicial=10 * ureg.meter,
        velocidad_inicial=5 * ureg.meter / ureg.second,
        aceleracion_inicial=2 * ureg.meter / ureg.second**2
    )
    vel = mruv.velocidad(2 * ureg.second)
    assert vel == (5 + 2*2) * ureg.meter / ureg.second # 5 + 4 = 9

def test_mruv_velocidad_without_units():
    mruv = MovimientoRectilineoUniformementeVariado(
        posicion_inicial=10,
        velocidad_inicial=5,
        aceleracion_inicial=2
    )
    vel = mruv.velocidad(2)
    assert vel == (5 + 2*2) * ureg.meter / ureg.second

def test_mruv_aceleracion_with_units():
    mruv = MovimientoRectilineoUniformementeVariado(aceleracion_inicial=2 * ureg.meter / ureg.second**2)
    acc = mruv.aceleracion()
    assert acc == 2 * ureg.meter / ureg.second**2

def test_mruv_aceleracion_without_units():
    mruv = MovimientoRectilineoUniformementeVariado(aceleracion_inicial=2)
    acc = mruv.aceleracion()
    assert acc == 2 * ureg.meter / ureg.second**2

def test_mruv_velocidad_sin_tiempo_with_units():
    mruv = MovimientoRectilineoUniformementeVariado(
        posicion_inicial=0 * ureg.meter,
        velocidad_inicial=0 * ureg.meter / ureg.second,
        aceleracion_inicial=2 * ureg.meter / ureg.second**2
    )
    vel_final = mruv.velocidad_sin_tiempo(16 * ureg.meter)
    assert vel_final == 8 * ureg.meter / ureg.second # v^2 = 0^2 + 2*2*16 = 64, v = 8

def test_mruv_velocidad_sin_tiempo_without_units():
    mruv = MovimientoRectilineoUniformementeVariado(
        posicion_inicial=0,
        velocidad_inicial=0,
        aceleracion_inicial=2
    )
    vel_final = mruv.velocidad_sin_tiempo(16)
    assert vel_final == 8 * ureg.meter / ureg.second
