import pytest
import math
import numpy as np
from cinetica.cinematica.oscilatorio.movimiento_armonico_complejo import (
    MovimientoArmonicoComplejo,
)
from cinetica.units import ureg, Q_


def test_mac_init_with_units():
    components = [
        {
            "amplitud": 2.0 * ureg.meter,
            "frecuencia_angular": 3.0 * ureg.radian / ureg.second,
            "fase_inicial": 0.0 * ureg.radian,
        },
        {
            "amplitud": 1.5 * ureg.meter,
            "frecuencia_angular": 2.0 * ureg.radian / ureg.second,
            "fase_inicial": math.pi / 4 * ureg.radian,
        },
    ]

    mac = MovimientoArmonicoComplejo(components)

    assert len(mac.mas_components) == 2
    assert mac.mas_components[0]["amplitud"].magnitude == 2.0
    assert mac.mas_components[0]["amplitud"].units == ureg.meter
    assert mac.mas_components[1]["frecuencia_angular"].magnitude == 2.0
    assert (
        mac.mas_components[1]["frecuencia_angular"].units == ureg.radian / ureg.second
    )


def test_mac_init_without_units():
    components = [
        {"amplitud": 2.0, "frecuencia_angular": 3.0, "fase_inicial": 0.0},
        {"amplitud": 1.5, "frecuencia_angular": 2.0, "fase_inicial": math.pi / 4},
    ]

    mac = MovimientoArmonicoComplejo(components)

    assert len(mac.mas_components) == 2
    assert mac.mas_components[0]["amplitud"].units == ureg.meter
    assert (
        mac.mas_components[1]["frecuencia_angular"].units == ureg.radian / ureg.second
    )
    assert mac.mas_components[1]["fase_inicial"].units == ureg.radian


def test_mac_posicion_with_units():
    components = [
        {
            "amplitud": 2.0 * ureg.meter,
            "frecuencia_angular": math.pi * ureg.radian / ureg.second,
            "fase_inicial": 0.0 * ureg.radian,
        },
        {
            "amplitud": 1.0 * ureg.meter,
            "frecuencia_angular": 2.0 * math.pi * ureg.radian / ureg.second,
            "fase_inicial": 0.0 * ureg.radian,
        },
    ]

    mac = MovimientoArmonicoComplejo(components)
    pos = mac.posicion(0.0 * ureg.second)

    # At t=0: x1 = 2*cos(0) = 2, x2 = 1*cos(0) = 1, total = 3
    expected = 3.0

    assert abs(pos.magnitude - expected) < 1e-10
    assert pos.units == ureg.meter


def test_mac_velocidad_with_units():
    components = [
        {
            "amplitud": 2.0 * ureg.meter,
            "frecuencia_angular": math.pi * ureg.radian / ureg.second,
            "fase_inicial": 0.0 * ureg.radian,
        }
    ]

    mac = MovimientoArmonicoComplejo(components)
    vel = mac.velocidad(0.0 * ureg.second)

    # At t=0: v = -A*ω*sin(0) = 0
    expected = 0.0

    assert abs(vel.magnitude - expected) < 1e-10
    assert vel.units == ureg.meter / ureg.second


def test_mac_aceleracion_with_units():
    components = [
        {
            "amplitud": 2.0 * ureg.meter,
            "frecuencia_angular": math.pi * ureg.radian / ureg.second,
            "fase_inicial": 0.0 * ureg.radian,
        }
    ]

    mac = MovimientoArmonicoComplejo(components)
    acel = mac.aceleracion(0.0 * ureg.second)

    # At t=0: a = -A*ω²*cos(0) = -2*π²
    expected = -2.0 * (math.pi**2)

    assert abs(acel.magnitude - expected) < 1e-10
    assert acel.units == ureg.meter / ureg.second**2


def test_mac_amplitud_resultante_with_units():
    components = [
        {
            "amplitud": 3.0 * ureg.meter,
            "frecuencia_angular": 2.0 * ureg.radian / ureg.second,
            "fase_inicial": 0.0 * ureg.radian,
        },
        {
            "amplitud": 4.0 * ureg.meter,
            "frecuencia_angular": 2.0 * ureg.radian / ureg.second,
            "fase_inicial": math.pi / 2 * ureg.radian,
        },
    ]

    mac = MovimientoArmonicoComplejo(components)
    amp_result = mac.amplitud_resultante()

    # For same frequency with phase difference π/2: A_result = sqrt(3² + 4²) = 5
    expected = 5.0

    assert abs(amp_result.magnitude - expected) < 1e-10
    assert amp_result.units == ureg.meter


def test_mac_fase_resultante_with_units():
    components = [
        {
            "amplitud": 3.0 * ureg.meter,
            "frecuencia_angular": 2.0 * ureg.radian / ureg.second,
            "fase_inicial": 0.0 * ureg.radian,
        },
        {
            "amplitud": 4.0 * ureg.meter,
            "frecuencia_angular": 2.0 * ureg.radian / ureg.second,
            "fase_inicial": math.pi / 2 * ureg.radian,
        },
    ]

    mac = MovimientoArmonicoComplejo(components)
    fase_result = mac.fase_resultante()

    # For components (3,0) and (4,π/2): phase = arctan(4/3)
    expected = math.atan(4.0 / 3.0)

    assert abs(fase_result.magnitude - expected) < 1e-10
    assert fase_result.units == ureg.radian


def test_mac_init_empty_components():
    with pytest.raises(ValueError, match="mas_components debe ser una lista no vacía"):
        MovimientoArmonicoComplejo([])


def test_mac_init_invalid_component():
    components = [
        {
            "amplitud": 2.0 * ureg.meter,
            "frecuencia_angular": 3.0 * ureg.radian / ureg.second,
            # Missing 'fase_inicial'
        }
    ]

    with pytest.raises(ValueError, match="Cada componente MAS debe tener"):
        MovimientoArmonicoComplejo(components)


def test_mac_init_negative_amplitud():
    components = [
        {
            "amplitud": -2.0 * ureg.meter,
            "frecuencia_angular": 3.0 * ureg.radian / ureg.second,
            "fase_inicial": 0.0 * ureg.radian,
        }
    ]

    with pytest.raises(ValueError, match="La amplitud debe ser un valor positivo"):
        MovimientoArmonicoComplejo(components)


def test_mac_init_negative_frecuencia():
    components = [
        {
            "amplitud": 2.0 * ureg.meter,
            "frecuencia_angular": -3.0 * ureg.radian / ureg.second,
            "fase_inicial": 0.0 * ureg.radian,
        }
    ]

    with pytest.raises(
        ValueError, match="La frecuencia angular debe ser un valor positivo"
    ):
        MovimientoArmonicoComplejo(components)
