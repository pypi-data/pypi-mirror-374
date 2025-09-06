import pytest
import math
import numpy as np
from cinetica.cinematica.circular.movimiento_circular_uniforme import MovimientoCircularUniforme
from cinetica.cinematica.circular.movimiento_circular_uniformemente_variado import MovimientoCircularUniformementeVariado
from cinetica.units import ureg, Q_

# --- MovimientoCircularUniforme Tests ---
def test_mcu_init_with_units():
    mcu = MovimientoCircularUniforme(
        radio=10 * ureg.meter,
        posicion_angular_inicial=0.5 * ureg.radian,
        velocidad_angular_inicial=2 * ureg.radian / ureg.second
    )
    assert mcu.radio == 10 * ureg.meter
    assert mcu.posicion_angular_inicial == 0.5 * ureg.radian
    assert mcu.velocidad_angular_inicial == 2 * ureg.radian / ureg.second

def test_mcu_init_without_units():
    mcu = MovimientoCircularUniforme(
        radio=10,
        posicion_angular_inicial=0.5,
        velocidad_angular_inicial=2
    )
    assert mcu.radio == 10 * ureg.meter
    assert mcu.posicion_angular_inicial == 0.5 * ureg.radian
    assert mcu.velocidad_angular_inicial == 2 * ureg.radian / ureg.second

def test_mcu_posicion_angular_with_units():
    mcu = MovimientoCircularUniforme(10 * ureg.meter, 0 * ureg.radian, 2 * ureg.radian / ureg.second)
    pos_ang = mcu.posicion_angular(1 * ureg.second)
    assert pos_ang == 2 * ureg.radian

def test_mcu_velocidad_angular_with_units():
    mcu = MovimientoCircularUniforme(10 * ureg.meter, 0 * ureg.radian, 2 * ureg.radian / ureg.second)
    vel_ang = mcu.velocidad_angular()
    assert vel_ang == 2 * ureg.radian / ureg.second

def test_mcu_velocidad_tangencial_with_units():
    mcu = MovimientoCircularUniforme(10 * ureg.meter, 0 * ureg.radian, 2 * ureg.radian / ureg.second)
    vel_tan = mcu.velocidad_tangencial()
    assert vel_tan == 20 * ureg.meter / ureg.second

def test_mcu_aceleracion_centripeta_with_units():
    mcu = MovimientoCircularUniforme(10 * ureg.meter, 0 * ureg.radian, 2 * ureg.radian / ureg.second)
    acc_cent = mcu.aceleracion_centripeta()
    assert acc_cent == 40 * ureg.meter / ureg.second**2 # (2 rad/s)^2 * 10 m = 40 m/s^2

def test_mcu_periodo_with_units():
    mcu = MovimientoCircularUniforme(10 * ureg.meter, 0 * ureg.radian, 2 * ureg.radian / ureg.second)
    period = mcu.periodo()
    assert period == (2 * math.pi / 2) * ureg.second

def test_mcu_frecuencia_with_units():
    mcu = MovimientoCircularUniforme(10 * ureg.meter, 0 * ureg.radian, 2 * ureg.radian / ureg.second)
    freq = mcu.frecuencia()
    assert freq == (2 / (2 * math.pi)) * ureg.hertz

def test_mcu_posicion_vector_with_units():
    mcu = MovimientoCircularUniforme(1 * ureg.meter, 0 * ureg.radian, math.pi/2 * ureg.radian / ureg.second)
    pos_vec = mcu.posicion(1 * ureg.second) # At t=1s, theta = pi/2, so x=0, y=1
    assert np.allclose(pos_vec.magnitude, np.array([0.0, 1.0]))
    assert pos_vec.units == ureg.meter

def test_mcu_velocidad_vector_with_units():
    mcu = MovimientoCircularUniforme(1 * ureg.meter, 0 * ureg.radian, math.pi/2 * ureg.radian / ureg.second)
    vel_vec = mcu.velocidad(1 * ureg.second) # At t=1s, theta = pi/2, v_tan = pi/2, vx = -pi/2, vy = 0
    assert np.allclose(vel_vec.magnitude, np.array([-math.pi/2, 0.0]))
    assert vel_vec.units == ureg.meter / ureg.second

def test_mcu_aceleracion_vector_with_units():
    mcu = MovimientoCircularUniforme(1 * ureg.meter, 0 * ureg.radian, math.pi/2 * ureg.radian / ureg.second)
    acc_vec = mcu.aceleracion(1 * ureg.second) # At t=1s, theta = pi/2, ac = (pi/2)^2 * 1 = pi^2/4, ax = 0, ay = -ac
    assert np.allclose(acc_vec.magnitude, np.array([0.0, -(math.pi**2)/4]), atol=1e-8)
    assert acc_vec.units == ureg.meter / ureg.second**2

# --- MovimientoCircularUniformementeVariado Tests ---
def test_mcuv_init_with_units():
    mcuv = MovimientoCircularUniformementeVariado(
        radio=5 * ureg.meter,
        posicion_angular_inicial=0 * ureg.radian,
        velocidad_angular_inicial=1 * ureg.radian / ureg.second,
        aceleracion_angular_inicial=0.5 * ureg.radian / ureg.second**2
    )
    assert mcuv.radio == 5 * ureg.meter
    assert mcuv.posicion_angular_inicial == 0 * ureg.radian
    assert mcuv.velocidad_angular_inicial == 1 * ureg.radian / ureg.second
    assert mcuv.aceleracion_angular_inicial == 0.5 * ureg.radian / ureg.second**2

def test_mcuv_posicion_angular_with_units():
    mcuv = MovimientoCircularUniformementeVariado(5 * ureg.meter, 0 * ureg.radian, 1 * ureg.radian / ureg.second, 0.5 * ureg.radian / ureg.second**2)
    pos_ang = mcuv.posicion_angular(2 * ureg.second)
    assert pos_ang == (0 + 1*2 + 0.5*0.5*2**2) * ureg.radian # 2 + 1 = 3 rad

def test_mcuv_velocidad_angular_with_units():
    mcuv = MovimientoCircularUniformementeVariado(5 * ureg.meter, 0 * ureg.radian, 1 * ureg.radian / ureg.second, 0.5 * ureg.radian / ureg.second**2)
    vel_ang = mcuv.velocidad_angular(2 * ureg.second)
    assert vel_ang == (1 + 0.5*2) * ureg.radian / ureg.second # 1 + 1 = 2 rad/s

def test_mcuv_aceleracion_angular_with_units():
    mcuv = MovimientoCircularUniformementeVariado(5 * ureg.meter, aceleracion_angular_inicial=0.5 * ureg.radian / ureg.second**2)
    acc_ang = mcuv.aceleracion_angular()
    assert acc_ang == 0.5 * ureg.radian / ureg.second**2

def test_mcuv_velocidad_tangencial_with_units():
    mcuv = MovimientoCircularUniformementeVariado(5 * ureg.meter, 0 * ureg.radian, 1 * ureg.radian / ureg.second, 0.5 * ureg.radian / ureg.second**2)
    vel_tan = mcuv.velocidad_tangencial(2 * ureg.second)
    assert vel_tan == (2 * 5) * ureg.meter / ureg.second # 10 m/s

def test_mcuv_aceleracion_tangencial_with_units():
    mcuv = MovimientoCircularUniformementeVariado(5 * ureg.meter, aceleracion_angular_inicial=0.5 * ureg.radian / ureg.second**2)
    acc_tan = mcuv.aceleracion_tangencial()
    assert acc_tan == (0.5 * 5) * ureg.meter / ureg.second**2 # 2.5 m/s^2

def test_mcuv_aceleracion_centripeta_with_units():
    mcuv = MovimientoCircularUniformementeVariado(5 * ureg.meter, 0 * ureg.radian, 1 * ureg.radian / ureg.second, 0.5 * ureg.radian / ureg.second**2)
    acc_cent = mcuv.aceleracion_centripeta(2 * ureg.second)
    assert acc_cent == (2**2 * 5) * ureg.meter / ureg.second**2 # (2 rad/s)^2 * 5 m = 20 m/s^2

def test_mcuv_aceleracion_total_with_units():
    mcuv = MovimientoCircularUniformementeVariado(5 * ureg.meter, 0 * ureg.radian, 1 * ureg.radian / ureg.second, 0.5 * ureg.radian / ureg.second**2)
    acc_total = mcuv.aceleracion_total(2 * ureg.second)
    at = mcuv.aceleracion_tangencial().magnitude # 2.5
    an = mcuv.aceleracion_centripeta(2 * ureg.second).magnitude # 20
    assert acc_total == math.sqrt(at**2 + an**2) * ureg.meter / ureg.second**2

def test_mcuv_posicion_vector_with_units():
    mcuv = MovimientoCircularUniformementeVariado(1 * ureg.meter, 0 * ureg.radian, 0 * ureg.radian / ureg.second, math.pi/2 * ureg.radian / ureg.second**2)
    pos_vec = mcuv.posicion(1 * ureg.second) # At t=1s, theta = 0.5 * pi/2 * 1^2 = pi/4, x = cos(pi/4), y = sin(pi/4)
    assert np.allclose(pos_vec.magnitude, np.array([math.cos(math.pi/4), math.sin(math.pi/4)]))
    assert pos_vec.units == ureg.meter

def test_mcuv_velocidad_vector_with_units():
    mcuv = MovimientoCircularUniformementeVariado(1 * ureg.meter, 0 * ureg.radian, 0 * ureg.radian / ureg.second, math.pi/2 * ureg.radian / ureg.second**2)
    vel_vec = mcuv.velocidad(1 * ureg.second) # At t=1s, omega = pi/2, theta = pi/4, v_tan = omega * R = pi/2
    # vx = -v_tan * sin(theta) = -pi/2 * sin(pi/4)
    # vy = v_tan * cos(theta) = pi/2 * cos(pi/4)
    expected_vx = -(math.pi/2) * math.sin(math.pi/4)
    expected_vy = (math.pi/2) * math.cos(math.pi/4)
    assert np.allclose(vel_vec.magnitude, np.array([expected_vx, expected_vy]))
    assert vel_vec.units == ureg.meter / ureg.second

def test_mcuv_aceleracion_vector_with_units():
    mcuv = MovimientoCircularUniformementeVariado(1 * ureg.meter, 0 * ureg.radian, 0 * ureg.radian / ureg.second, math.pi/2 * ureg.radian / ureg.second**2)
    acc_vec = mcuv.aceleracion(1 * ureg.second)
    # At t=1s, omega = pi/2, alpha = pi/2, theta = pi/4, R = 1
    # at = alpha * R = pi/2 * 1 = pi/2
    # an = omega^2 * R = (pi/2)^2 * 1 = pi^2/4
    # ax = -an * cos(theta) - at * sin(theta) = -pi^2/4 * cos(pi/4) - pi/2 * sin(pi/4)
    # ay = -an * sin(theta) + at * cos(theta) = -pi^2/4 * sin(pi/4) + pi/2 * cos(pi/4)
    expected_ax = -(math.pi**2/4) * math.cos(math.pi/4) - (math.pi/2) * math.sin(math.pi/4)
    expected_ay = -(math.pi**2/4) * math.sin(math.pi/4) + (math.pi/2) * math.cos(math.pi/4)
    assert np.allclose(acc_vec.magnitude, np.array([expected_ax, expected_ay]))
    assert acc_vec.units == ureg.meter / ureg.second**2
