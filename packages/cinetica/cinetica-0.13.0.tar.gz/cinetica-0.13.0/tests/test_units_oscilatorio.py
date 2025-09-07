import pytest
import math
from cinetica.cinematica.oscilatorio.movimiento_armonico_simple import (
    MovimientoArmonicoSimple,
)
from cinetica.units import ureg, Q_


def test_mas_init_with_units():
    amplitud = 2.0 * ureg.meter
    frecuencia_angular = 3.0 * ureg.radian / ureg.second
    fase_inicial = math.pi / 4 * ureg.radian

    mas = MovimientoArmonicoSimple(amplitud, frecuencia_angular, fase_inicial)

    assert mas.amplitud.magnitude == 2.0
    assert mas.amplitud.units == ureg.meter
    assert mas.frecuencia_angular.magnitude == 3.0
    assert mas.frecuencia_angular.units == ureg.radian / ureg.second
    assert mas.fase_inicial.magnitude == math.pi / 4
    assert mas.fase_inicial.units == ureg.radian


def test_mas_init_without_units():
    amplitud = 2.0
    frecuencia_angular = 3.0
    fase_inicial = math.pi / 4

    mas = MovimientoArmonicoSimple(amplitud, frecuencia_angular, fase_inicial)

    assert mas.amplitud.magnitude == 2.0
    assert mas.amplitud.units == ureg.meter
    assert mas.frecuencia_angular.magnitude == 3.0
    assert mas.frecuencia_angular.units == ureg.radian / ureg.second
    assert mas.fase_inicial.magnitude == math.pi / 4
    assert mas.fase_inicial.units == ureg.radian


def test_mas_posicion_with_units():
    mas = MovimientoArmonicoSimple(
        2.0 * ureg.meter, math.pi * ureg.radian / ureg.second, 0 * ureg.radian
    )

    pos = mas.posicion(0.5 * ureg.second)
    expected = 2.0 * math.cos(math.pi * 0.5)  # 2 * cos(π/2) = 0

    assert abs(pos.magnitude - expected) < 1e-10
    assert pos.units == ureg.meter


def test_mas_velocidad_with_units():
    mas = MovimientoArmonicoSimple(
        2.0 * ureg.meter, math.pi * ureg.radian / ureg.second, 0 * ureg.radian
    )

    vel = mas.velocidad(0.0 * ureg.second)
    expected = -2.0 * math.pi * math.sin(0)  # -A*ω*sin(0) = 0

    assert abs(vel.magnitude - expected) < 1e-10
    # The units will be meter * radian / second due to ω having radian units
    assert vel.units == ureg.meter * ureg.radian / ureg.second


def test_mas_aceleracion_with_units():
    mas = MovimientoArmonicoSimple(
        2.0 * ureg.meter, math.pi * ureg.radian / ureg.second, 0 * ureg.radian
    )

    acel = mas.aceleracion(0.0 * ureg.second)
    expected = -2.0 * (math.pi**2) * math.cos(0)  # -A*ω²*cos(0) = -2π²

    assert abs(acel.magnitude - expected) < 1e-10
    # The units will be meter * radian² / second² due to ω² having radian² units
    assert acel.units == ureg.meter * ureg.radian**2 / ureg.second**2


def test_mas_periodo_with_units():
    mas = MovimientoArmonicoSimple(
        1.0 * ureg.meter, 2.0 * ureg.radian / ureg.second, 0 * ureg.radian
    )

    periodo = mas.periodo()
    expected = 2 * math.pi / 2.0  # T = 2π/ω

    assert abs(periodo.magnitude - expected) < 1e-10
    assert periodo.units == ureg.second


def test_mas_frecuencia_with_units():
    mas = MovimientoArmonicoSimple(
        1.0 * ureg.meter, 2.0 * ureg.radian / ureg.second, 0 * ureg.radian
    )

    frecuencia = mas.frecuencia()
    expected = 2.0 / (2 * math.pi)  # f = ω/(2π)

    assert abs(frecuencia.magnitude - expected) < 1e-10
    # The units will be 1/second which is equivalent to hertz
    assert frecuencia.units == ureg.second**-1


def test_mas_energia_cinetica_with_units():
    mas = MovimientoArmonicoSimple(
        2.0 * ureg.meter, math.pi * ureg.radian / ureg.second, 0 * ureg.radian
    )

    masa = 1.0 * ureg.kilogram
    ec = mas.energia_cinetica(0.5 * ureg.second, masa)

    # At t=0.5s, v = -A*ω*sin(π*0.5) = -2π*sin(π/2) = -2π
    # Ec = 0.5*m*v² = 0.5*1*(2π)²
    expected = 0.5 * 1.0 * (2 * math.pi) ** 2

    assert abs(ec.magnitude - expected) < 1e-10
    # The units will include radian² from velocity squared
    assert ec.units == ureg.kilogram * ureg.meter**2 * ureg.radian**2 / ureg.second**2


def test_mas_energia_potencial_with_units():
    mas = MovimientoArmonicoSimple(
        2.0 * ureg.meter, math.pi * ureg.radian / ureg.second, 0 * ureg.radian
    )

    # k = m*ω² for harmonic oscillator
    masa = 1.0 * ureg.kilogram
    k = masa * (math.pi * ureg.radian / ureg.second) ** 2
    ep = mas.energia_potencial(0.0 * ureg.second, k)

    # At t=0, x = A*cos(0) = 2
    # Ep = 0.5*k*x² = 0.5*m*ω²*x² = 0.5*1*π²*4
    expected = 0.5 * 1.0 * (math.pi**2) * (2.0**2)

    assert abs(ep.magnitude - expected) < 1e-10
    # The units will include radian² from k having radian² units
    assert ep.units == ureg.kilogram * ureg.radian**2 * ureg.meter**2 / ureg.second**2


def test_mas_energia_total_with_units():
    mas = MovimientoArmonicoSimple(
        2.0 * ureg.meter, math.pi * ureg.radian / ureg.second, 0 * ureg.radian
    )

    masa = 1.0 * ureg.kilogram
    k = masa * (math.pi * ureg.radian / ureg.second) ** 2
    et = mas.energia_total(masa, k)

    # Et = 0.5*k*A² = 0.5*m*ω²*A² = 0.5*1*π²*4
    expected = 0.5 * 1.0 * (math.pi**2) * (2.0**2)

    assert abs(et.magnitude - expected) < 1e-10
    # The units will include radian² from k having radian² units
    assert et.units == ureg.kilogram * ureg.radian**2 * ureg.meter**2 / ureg.second**2


def test_mas_init_invalid_amplitud():
    with pytest.raises(ValueError, match="La amplitud debe ser un valor positivo"):
        MovimientoArmonicoSimple(-1.0 * ureg.meter, 1.0 * ureg.radian / ureg.second)


def test_mas_init_invalid_frecuencia():
    with pytest.raises(
        ValueError, match="La frecuencia angular debe ser un valor positivo"
    ):
        MovimientoArmonicoSimple(1.0 * ureg.meter, -1.0 * ureg.radian / ureg.second)
