import pytest
import numpy as np
import math
from cinetica.cinematica.espacial.movimiento_espacial import MovimientoEspacial
from cinetica.units import ureg, Q_

def test_espacial_init_with_units():
    pos_inicial = Q_(np.array([1.0, 2.0, 3.0]), ureg.meter)
    vel_inicial = Q_(np.array([4.0, 5.0, 6.0]), ureg.meter / ureg.second)
    acel_constante = Q_(np.array([1.0, 0.0, -9.8]), ureg.meter / ureg.second**2)
    
    mov = MovimientoEspacial(pos_inicial, vel_inicial, acel_constante)
    
    assert np.allclose(mov.posicion_inicial.magnitude, [1.0, 2.0, 3.0])
    assert mov.posicion_inicial.units == ureg.meter
    assert np.allclose(mov.velocidad_inicial.magnitude, [4.0, 5.0, 6.0])
    assert mov.velocidad_inicial.units == ureg.meter / ureg.second
    assert np.allclose(mov.aceleracion_constante.magnitude, [1.0, 0.0, -9.8])
    assert mov.aceleracion_constante.units == ureg.meter / ureg.second**2

def test_espacial_init_without_units():
    pos_inicial = [1.0, 2.0, 3.0]
    vel_inicial = [4.0, 5.0, 6.0]
    acel_constante = [1.0, 0.0, -9.8]
    
    mov = MovimientoEspacial(pos_inicial, vel_inicial, acel_constante)
    
    assert np.allclose(mov.posicion_inicial.magnitude, [1.0, 2.0, 3.0])
    assert mov.posicion_inicial.units == ureg.meter
    assert np.allclose(mov.velocidad_inicial.magnitude, [4.0, 5.0, 6.0])
    assert mov.velocidad_inicial.units == ureg.meter / ureg.second
    assert np.allclose(mov.aceleracion_constante.magnitude, [1.0, 0.0, -9.8])
    assert mov.aceleracion_constante.units == ureg.meter / ureg.second**2

def test_espacial_posicion_with_units():
    mov = MovimientoEspacial(
        Q_(np.array([0.0, 0.0, 0.0]), ureg.meter),
        Q_(np.array([1.0, 2.0, 3.0]), ureg.meter / ureg.second),
        Q_(np.array([0.5, 0.0, -9.8]), ureg.meter / ureg.second**2)
    )
    
    pos = mov.posicion(2.0 * ureg.second)
    expected = np.array([3.0, 4.0, -13.6])  # x = 1*2 + 0.5*0.5*4, y = 2*2, z = 3*2 - 0.5*9.8*4
    
    assert np.allclose(pos.magnitude, expected)
    assert pos.units == ureg.meter

def test_espacial_velocidad_with_units():
    mov = MovimientoEspacial(
        Q_(np.array([0.0, 0.0, 0.0]), ureg.meter),
        Q_(np.array([1.0, 2.0, 3.0]), ureg.meter / ureg.second),
        Q_(np.array([0.5, 0.0, -9.8]), ureg.meter / ureg.second**2)
    )
    
    vel = mov.velocidad(2.0 * ureg.second)
    expected = np.array([2.0, 2.0, -16.6])  # vx = 1 + 0.5*2, vy = 2, vz = 3 - 9.8*2
    
    assert np.allclose(vel.magnitude, expected)
    assert vel.units == ureg.meter / ureg.second

def test_espacial_aceleracion_with_units():
    acel_constante = Q_(np.array([0.5, 0.0, -9.8]), ureg.meter / ureg.second**2)
    mov = MovimientoEspacial(
        Q_(np.array([0.0, 0.0, 0.0]), ureg.meter),
        Q_(np.array([1.0, 2.0, 3.0]), ureg.meter / ureg.second),
        acel_constante
    )
    
    acel = mov.aceleracion(2.0 * ureg.second)
    
    assert np.allclose(acel.magnitude, acel_constante.magnitude)
    assert acel.units == ureg.meter / ureg.second**2

def test_espacial_magnitud_velocidad_with_units():
    mov = MovimientoEspacial(
        Q_(np.array([0.0, 0.0, 0.0]), ureg.meter),
        Q_(np.array([3.0, 4.0, 0.0]), ureg.meter / ureg.second),
        Q_(np.array([0.0, 0.0, 0.0]), ureg.meter / ureg.second**2)
    )
    
    mag_vel = mov.magnitud_velocidad(1.0 * ureg.second)
    expected = 5.0  # sqrt(3^2 + 4^2)
    
    assert np.isclose(mag_vel.magnitude, expected)
    assert mag_vel.units == ureg.meter / ureg.second

def test_espacial_magnitud_aceleracion_with_units():
    acel_constante = Q_(np.array([3.0, 4.0, 0.0]), ureg.meter / ureg.second**2)
    mov = MovimientoEspacial(
        Q_(np.array([0.0, 0.0, 0.0]), ureg.meter),
        Q_(np.array([0.0, 0.0, 0.0]), ureg.meter / ureg.second),
        acel_constante
    )
    
    # For constant acceleration, magnitude is constant
    mag_acel = mov.magnitud_aceleracion()
    expected = 5.0  # sqrt(3^2 + 4^2)
    
    assert np.isclose(mag_acel.magnitude, expected)
    assert mag_acel.units == ureg.meter / ureg.second**2

def test_espacial_init_invalid_dimensions():
    with pytest.raises(ValueError, match="Todos los vectores .* deben ser de 3 dimensiones"):
        MovimientoEspacial(
            Q_(np.array([1.0, 2.0]), ureg.meter),  # Only 2D
            Q_(np.array([1.0, 2.0, 3.0]), ureg.meter / ureg.second),
            Q_(np.array([1.0, 2.0, 3.0]), ureg.meter / ureg.second**2)
        )

def test_espacial_posicion_invalid_tiempo():
    mov = MovimientoEspacial()
    
    with pytest.raises(ValueError, match="El tiempo no puede ser negativo"):
        mov.posicion(-1.0 * ureg.second)

def test_espacial_velocidad_invalid_tiempo():
    mov = MovimientoEspacial()
    
    with pytest.raises(ValueError, match="El tiempo no puede ser negativo"):
        mov.velocidad(-1.0 * ureg.second)
