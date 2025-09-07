import pytest
import numpy as np
import math
from cinetica.cinematica.relativo.velocidad_relativa import MovimientoRelativo
from cinetica.units import ureg, Q_


def test_relativo_init():
    mov_rel = MovimientoRelativo()
    assert mov_rel is not None


def test_velocidad_relativa_2d_with_units():
    mov_rel = MovimientoRelativo()

    vel_a = Q_(np.array([5.0, 3.0]), ureg.meter / ureg.second)
    vel_b = Q_(np.array([2.0, 1.0]), ureg.meter / ureg.second)

    vel_rel = mov_rel.velocidad_relativa(vel_a, vel_b)
    expected = np.array([3.0, 2.0])

    assert np.allclose(vel_rel.magnitude, expected)
    assert vel_rel.units == ureg.meter / ureg.second


def test_velocidad_relativa_3d_with_units():
    mov_rel = MovimientoRelativo()

    vel_a = Q_(np.array([10.0, 5.0, 2.0]), ureg.meter / ureg.second)
    vel_b = Q_(np.array([3.0, 2.0, 1.0]), ureg.meter / ureg.second)

    vel_rel = mov_rel.velocidad_relativa(vel_a, vel_b)
    expected = np.array([7.0, 3.0, 1.0])

    assert np.allclose(vel_rel.magnitude, expected)
    assert vel_rel.units == ureg.meter / ureg.second


def test_velocidad_relativa_without_units():
    mov_rel = MovimientoRelativo()

    vel_a = np.array([5.0, 3.0])
    vel_b = np.array([2.0, 1.0])

    vel_rel = mov_rel.velocidad_relativa(vel_a, vel_b)
    expected = np.array([3.0, 2.0])

    assert np.allclose(vel_rel.magnitude, expected)
    assert vel_rel.units == ureg.meter / ureg.second


def test_velocidad_absoluta_a_with_units():
    mov_rel = MovimientoRelativo()

    vel_rel_ab = Q_(np.array([3.0, 2.0]), ureg.meter / ureg.second)
    vel_b = Q_(np.array([2.0, 1.0]), ureg.meter / ureg.second)

    vel_a = mov_rel.velocidad_absoluta_a(vel_rel_ab, vel_b)
    expected = np.array([5.0, 3.0])

    assert np.allclose(vel_a.magnitude, expected)
    assert vel_a.units == ureg.meter / ureg.second


def test_velocidad_absoluta_b_with_units():
    mov_rel = MovimientoRelativo()

    vel_rel_ab = Q_(np.array([3.0, 2.0]), ureg.meter / ureg.second)
    vel_a = Q_(np.array([5.0, 3.0]), ureg.meter / ureg.second)

    vel_b = mov_rel.velocidad_absoluta_b(vel_a, vel_rel_ab)
    expected = np.array([2.0, 1.0])

    assert np.allclose(vel_b.magnitude, expected)
    assert vel_b.units == ureg.meter / ureg.second


def test_magnitud_velocidad_with_units():
    mov_rel = MovimientoRelativo()

    velocidad = Q_(np.array([3.0, 4.0]), ureg.meter / ureg.second)

    magnitud = mov_rel.magnitud_velocidad(velocidad)
    expected = 5.0  # sqrt(3² + 4²)

    assert abs(magnitud.magnitude - expected) < 1e-10
    assert magnitud.units == ureg.meter / ureg.second


def test_direccion_velocidad_2d_with_units():
    mov_rel = MovimientoRelativo()

    velocidad = Q_(np.array([1.0, 1.0]), ureg.meter / ureg.second)

    direccion = mov_rel.direccion_velocidad(velocidad)
    expected = math.pi / 4  # 45 degrees in radians

    assert abs(direccion.magnitude - expected) < 1e-10
    assert direccion.units == ureg.radian


def test_direccion_velocidad_3d_with_units():
    mov_rel = MovimientoRelativo()

    velocidad = Q_(np.array([1.0, 1.0, 1.0]), ureg.meter / ureg.second)

    direccion = mov_rel.direccion_velocidad(velocidad)
    expected = np.array([1.0, 1.0, 1.0]) / np.sqrt(3)  # Unit vector

    assert np.allclose(direccion, expected)
    assert isinstance(direccion, np.ndarray)


def test_velocidad_relativa_incompatible_units():
    mov_rel = MovimientoRelativo()

    vel_a = Q_(np.array([5.0, 3.0]), ureg.meter / ureg.second)
    vel_b = Q_(np.array([2.0, 1.0]), ureg.kilometer / ureg.hour)  # Different units

    # This should raise ValueError because the implementation checks for exact unit equality
    with pytest.raises(
        ValueError,
        match="Las unidades de los vectores de velocidad deben ser compatibles",
    ):
        mov_rel.velocidad_relativa(vel_a, vel_b)


def test_velocidad_relativa_dimension_mismatch():
    mov_rel = MovimientoRelativo()

    vel_a = Q_(np.array([5.0, 3.0]), ureg.meter / ureg.second)
    vel_b = Q_(
        np.array([2.0, 1.0, 0.0]), ureg.meter / ureg.second
    )  # Different dimensions

    with pytest.raises((ValueError, TypeError)):
        mov_rel.velocidad_relativa(vel_a, vel_b)


def test_magnitud_velocidad_zero_vector():
    mov_rel = MovimientoRelativo()

    velocidad = Q_(np.array([0.0, 0.0]), ureg.meter / ureg.second)

    magnitud = mov_rel.magnitud_velocidad(velocidad)
    expected = 0.0

    assert abs(magnitud.magnitude - expected) < 1e-10
    assert magnitud.units == ureg.meter / ureg.second


def test_direccion_velocidad_zero_vector():
    mov_rel = MovimientoRelativo()

    velocidad = Q_(np.array([0.0, 0.0]), ureg.meter / ureg.second)

    # The implementation returns 0.0 * ureg.radian for 2D zero vectors
    direccion = mov_rel.direccion_velocidad(velocidad)
    assert direccion.magnitude == 0.0
    assert direccion.units == ureg.radian
