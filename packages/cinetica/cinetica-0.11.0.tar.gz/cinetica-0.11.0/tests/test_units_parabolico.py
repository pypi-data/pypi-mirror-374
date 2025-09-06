import pytest
from cinetica.cinematica.parabolico.base import MovimientoParabolicoBase
from cinetica.cinematica.parabolico.analisis import MovimientoParabolicoAnalisis
from cinetica.units import ureg, Q_

def test_parabolico_base_init_with_units():
    mp_base = MovimientoParabolicoBase(
        velocidad_inicial=30 * ureg.meter / ureg.second,
        angulo_grados=45 * ureg.degree,
        gravedad=9.81 * ureg.meter / ureg.second**2
    )
    assert mp_base.velocidad_inicial == 30 * ureg.meter / ureg.second
    assert mp_base.angulo_radianes.to(ureg.degree) == 45 * ureg.degree
    assert mp_base.gravedad == 9.81 * ureg.meter / ureg.second**2

def test_parabolico_base_init_without_units():
    mp_base = MovimientoParabolicoBase(
        velocidad_inicial=30,
        angulo_grados=45,
        gravedad=9.81
    )
    assert mp_base.velocidad_inicial == 30 * ureg.meter / ureg.second
    assert mp_base.angulo_radianes.to(ureg.degree) == 45 * ureg.degree
    assert mp_base.gravedad == 9.81 * ureg.meter / ureg.second**2

def test_parabolico_posicion_with_units():
    mp_base = MovimientoParabolicoBase(30 * ureg.meter / ureg.second, 45 * ureg.degree)
    pos_x, pos_y = mp_base.posicion(2 * ureg.second)
    assert pos_x.units == ureg.meter
    assert pos_y.units == ureg.meter
    # Approximate values for 30 m/s at 45 deg after 2s
    # vx = 30 * cos(45) = 21.21
    # vy0 = 30 * sin(45) = 21.21
    # x = 21.21 * 2 = 42.42
    # y = 21.21 * 2 - 0.5 * 9.81 * 2^2 = 42.42 - 19.62 = 22.8
    assert abs(pos_x.magnitude - 42.42) < 0.01
    assert abs(pos_y.magnitude - 22.8) < 0.01

def test_parabolico_velocidad_with_units():
    mp_base = MovimientoParabolicoBase(30 * ureg.meter / ureg.second, 45 * ureg.degree)
    vel_x, vel_y = mp_base.velocidad(2 * ureg.second)
    assert vel_x.units == ureg.meter / ureg.second
    assert vel_y.units == ureg.meter / ureg.second
    # Approximate values for 30 m/s at 45 deg after 2s
    # vx = 21.21
    # vy = 21.21 - 9.81 * 2 = 21.21 - 19.62 = 1.59
    assert abs(vel_x.magnitude - 21.21) < 0.01
    assert abs(vel_y.magnitude - 1.59) < 0.01

def test_parabolico_aceleracion_with_units():
    mp_base = MovimientoParabolicoBase(30 * ureg.meter / ureg.second, 45 * ureg.degree)
    acc_x, acc_y = mp_base.aceleracion()
    assert acc_x == 0.0 * ureg.meter / ureg.second**2
    assert acc_y == -9.81 * ureg.meter / ureg.second**2

def test_parabolico_analisis_tiempo_vuelo_with_units():
    mp_base = MovimientoParabolicoBase(30 * ureg.meter / ureg.second, 45 * ureg.degree)
    mp_analisis = MovimientoParabolicoAnalisis(mp_base)
    tiempo_vuelo = mp_analisis.tiempo_vuelo()
    assert tiempo_vuelo.units == ureg.second
    # T = 2 * vy0 / g = 2 * (30 * sin(45)) / 9.81 = 2 * 21.21 / 9.81 = 4.32
    assert abs(tiempo_vuelo.magnitude - 4.32) < 0.01

def test_parabolico_analisis_altura_maxima_with_units():
    mp_base = MovimientoParabolicoBase(30 * ureg.meter / ureg.second, 45 * ureg.degree)
    mp_analisis = MovimientoParabolicoAnalisis(mp_base)
    altura_maxima = mp_analisis.altura_maxima()
    assert altura_maxima.units == ureg.meter
    # H = vy0^2 / (2g) = (30 * sin(45))^2 / (2 * 9.81) = 21.21^2 / 19.62 = 449.86 / 19.62 = 22.93577981651376
    assert abs(altura_maxima.magnitude - 22.93577981651376) < 1e-9

def test_parabolico_analisis_alcance_maximo_with_units():
    mp_base = MovimientoParabolicoBase(30 * ureg.meter / ureg.second, 45 * ureg.degree)
    mp_analisis = MovimientoParabolicoAnalisis(mp_base)
    alcance_maximo = mp_analisis.alcance_maximo()
    assert alcance_maximo.units == ureg.meter
    # R = vx0 * T = (30 * cos(45)) * 4.32504628951733 = 21.213203435596424 * 4.32504628951733 = 91.74311926605505
    assert abs(alcance_maximo.magnitude - 91.74311926605505) < 1e-9
