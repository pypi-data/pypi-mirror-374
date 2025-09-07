import numpy as np
import pytest
import matplotlib.pyplot as plt  # Importar matplotlib
from cinetica.cinematica.espacial.movimiento_espacial import MovimientoEspacial
from cinetica.units import ureg


def test_movimiento_espacial_init():
    """
    Testea la inicialización de la clase MovimientoEspacial.
    """
    me = MovimientoEspacial()
    assert np.allclose(me.posicion_inicial.magnitude, np.array([0.0, 0.0, 0.0]))
    assert np.allclose(me.velocidad_inicial.magnitude, np.array([0.0, 0.0, 0.0]))
    assert np.allclose(me.aceleracion_constante.magnitude, np.array([0.0, 0.0, 0.0]))

    me2 = MovimientoEspacial(
        posicion_inicial=np.array([1, 2, 3]),
        velocidad_inicial=np.array([4, 5, 6]),
        aceleracion_constante=np.array([7, 8, 9]),
    )
    assert np.allclose(me2.posicion_inicial.magnitude, np.array([1.0, 2.0, 3.0]))
    assert np.allclose(me2.velocidad_inicial.magnitude, np.array([4.0, 5.0, 6.0]))
    assert np.allclose(me2.aceleracion_constante.magnitude, np.array([7.0, 8.0, 9.0]))

    with pytest.raises(ValueError):
        MovimientoEspacial(posicion_inicial=np.array([1, 2]))  # Dimensión incorrecta


def test_movimiento_espacial_posicion():
    """
    Testea el cálculo de la posición en MovimientoEspacial.
    """
    me = MovimientoEspacial(
        posicion_inicial=np.array([0, 0, 0]),
        velocidad_inicial=np.array([1, 0, 0]),
        aceleracion_constante=np.array([0, 0, 0]),
    )
    assert np.allclose(me.posicion(tiempo=5).magnitude, np.array([5.0, 0.0, 0.0]))

    me2 = MovimientoEspacial(
        posicion_inicial=np.array([0, 0, 0]),
        velocidad_inicial=np.array([0, 0, 0]),
        aceleracion_constante=np.array([0, 0, -9.81]),
    )
    # y = 0.5 * a * t^2
    assert np.allclose(
        me2.posicion(tiempo=2).magnitude, np.array([0.0, 0.0, 0.5 * -9.81 * (2**2)])
    )

    me3 = MovimientoEspacial(
        posicion_inicial=np.array([1, 1, 1]),
        velocidad_inicial=np.array([2, 3, 4]),
        aceleracion_constante=np.array([0.1, 0.2, 0.3]),
    )
    # r = r0 + v0 * t + 0.5 * a * t^2
    t = 3
    expected_pos = (
        np.array([1, 1, 1])
        + np.array([2, 3, 4]) * t
        + 0.5 * np.array([0.1, 0.2, 0.3]) * (t**2)
    )
    assert np.allclose(me3.posicion(tiempo=t).magnitude, expected_pos)

    with pytest.raises(ValueError):
        me.posicion(tiempo=-1)


def test_movimiento_espacial_velocidad():
    """
    Testea el cálculo de la velocidad en MovimientoEspacial.
    """
    me = MovimientoEspacial(
        velocidad_inicial=np.array([10, 0, 0]),
        aceleracion_constante=np.array([2, 0, 0]),
    )
    # v = v0 + a * t
    assert np.allclose(
        me.velocidad(tiempo=5).magnitude, np.array([10 + 2 * 5, 0.0, 0.0])
    )

    me2 = MovimientoEspacial(
        velocidad_inicial=np.array([0, 0, 10]),
        aceleracion_constante=np.array([0, 0, -9.81]),
    )
    assert np.allclose(
        me2.velocidad(tiempo=1).magnitude, np.array([0.0, 0.0, 10 - 9.81 * 1])
    )

    with pytest.raises(ValueError):
        me.velocidad(tiempo=-1)


def test_movimiento_espacial_aceleracion():
    """
    Testea la obtención de la aceleración en MovimientoEspacial.
    """
    me = MovimientoEspacial(aceleracion_constante=np.array([1, 2, 3]))
    assert np.allclose(me.aceleracion().magnitude, np.array([1.0, 2.0, 3.0]))


def test_movimiento_espacial_magnitud_velocidad():
    """
    Testea el cálculo de la magnitud de la velocidad.
    """
    me = MovimientoEspacial(
        velocidad_inicial=np.array([3, 0, 0]), aceleracion_constante=np.array([1, 0, 0])
    )
    # v(t=1) = [3 + 1*1, 0, 0] = [4, 0, 0]
    assert me.magnitud_velocidad(tiempo=1).magnitude == 4.0

    me2 = MovimientoEspacial(
        velocidad_inicial=np.array([0, 0, 0]), aceleracion_constante=np.array([3, 4, 0])
    )
    # v(t=1) = [3, 4, 0]
    assert me2.magnitud_velocidad(tiempo=1).magnitude == 5.0


def test_movimiento_espacial_magnitud_aceleracion():
    """
    Testea el cálculo de la magnitud de la aceleración.
    """
    me = MovimientoEspacial(aceleracion_constante=np.array([3, 4, 0]))
    assert me.magnitud_aceleracion().magnitude == 5.0

    me2 = MovimientoEspacial(aceleracion_constante=np.array([0, 0, -9.81]))
    assert np.isclose(me2.magnitud_aceleracion().magnitude, 9.81)


def test_movimiento_espacial_graficar(mocker):
    """
    Testea el método graficar de MovimientoEspacial.
    Se mockea plt.show() para evitar que se abran ventanas de gráficos durante el test.
    """
    mocker.patch("matplotlib.pyplot.show")
    me = MovimientoEspacial(
        posicion_inicial=np.array([0, 0, 0]),
        velocidad_inicial=np.array([1, 1, 1]),
        aceleracion_constante=np.array([0, 0, -9.81]),
    )

    me.graficar(t_max=1.0, num_points=10)

    # Verificar que plt.show() fue llamado
    assert plt.show.called

    with pytest.raises(ValueError):
        me.graficar(t_max=-1.0)
