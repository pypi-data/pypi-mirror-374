import math
from typing import Union, Optional
import numpy as np
from ..base_movimiento import Movimiento
from ...units import ureg, Q_


class MovimientoCircularUniformementeVariado(Movimiento):
    """
    Clase para calcular y simular Movimiento Circular Uniformemente Variado (MCUV).
    """

    def __init__(
        self,
        radio: Union[float, Q_],
        posicion_angular_inicial: Union[float, Q_] = 0.0 * ureg.radian,
        velocidad_angular_inicial: Union[float, Q_] = 0.0 * ureg.radian / ureg.second,
        aceleracion_angular_inicial: Union[float, Q_] = 0.0
        * ureg.radian
        / ureg.second**2,
    ) -> None:
        """
        Inicializa el objeto MovimientoCircularUniformementeVariado con las condiciones iniciales.

        Args:
            radio (Q_): Radio de la trayectoria circular (m).
            posicion_angular_inicial (Q_): Posición angular inicial (radianes).
            velocidad_angular_inicial (Q_): Velocidad angular inicial (rad/s).
            aceleracion_angular_inicial (Q_): Aceleración angular inicial (rad/s^2).

        Raises:
            ValueError: Si el radio es menor o igual a cero.
        """
        if not isinstance(radio, Q_):
            radio = Q_(radio, ureg.meter)
        if not isinstance(posicion_angular_inicial, Q_):
            posicion_angular_inicial = Q_(posicion_angular_inicial, ureg.radian)
        if not isinstance(velocidad_angular_inicial, Q_):
            velocidad_angular_inicial = Q_(
                velocidad_angular_inicial, ureg.radian / ureg.second
            )
        if not isinstance(aceleracion_angular_inicial, Q_):
            aceleracion_angular_inicial = Q_(
                aceleracion_angular_inicial, ureg.radian / ureg.second**2
            )

        if radio.magnitude <= 0:
            raise ValueError("El radio debe ser un valor positivo.")

        self.radio = radio
        self.posicion_angular_inicial = posicion_angular_inicial
        self.velocidad_angular_inicial = velocidad_angular_inicial
        self.aceleracion_angular_inicial = aceleracion_angular_inicial

    def posicion_angular(self, tiempo: Union[float, Q_]) -> Q_:
        """
        Calcula la posición angular en función del tiempo.
        θ = θ₀ + ω₀ * t + (1/2) * α * t²

        Args:
            tiempo (Q_): Tiempo transcurrido (s).

        Returns:
            Q_: Posición angular (rad).

        Raises:
            ValueError: Si el tiempo es negativo.
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        if tiempo.magnitude < 0:
            raise ValueError("El tiempo no puede ser negativo.")
        return (
            self.posicion_angular_inicial
            + self.velocidad_angular_inicial * tiempo
            + 0.5 * self.aceleracion_angular_inicial * tiempo**2
        )

    def velocidad_angular(self, tiempo: Q_) -> Q_:
        """
        Calcula la velocidad angular en función del tiempo.
        ω = ω₀ + α * t

        Args:
            tiempo (Q_): Tiempo transcurrido (s).

        Returns:
            Q_: Velocidad angular (rad/s).

        Raises:
            ValueError: Si el tiempo es negativo.
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        if tiempo.magnitude < 0:
            raise ValueError("El tiempo no puede ser negativo.")
        return (
            self.velocidad_angular_inicial + self.aceleracion_angular_inicial * tiempo
        )

    def aceleracion_angular(self, tiempo: Q_ = None) -> Q_:
        """
        Obtiene la aceleración angular (constante en MCUV).

        Args:
            tiempo (Q_, optional): Tiempo transcurrido (s). No afecta al resultado.

        Returns:
            Q_: Aceleración angular (rad/s²).
        """
        return self.aceleracion_angular_inicial

    def velocidad_tangencial(self, tiempo: Q_) -> Q_:
        """
        Calcula la velocidad tangencial.
        v = ω * R

        Args:
            tiempo (Q_): Tiempo transcurrido (s).

        Returns:
            Q_: Velocidad tangencial (m/s).
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        return self.velocidad_angular(tiempo) * self.radio

    def aceleracion_tangencial(self, tiempo: Q_ = None) -> Q_:
        """
        Calcula la aceleración tangencial.
        aₜ = α * R

        Args:
            tiempo (Q_, optional): Tiempo transcurrido (s). No afecta al resultado.

        Returns:
            Q_: Aceleración tangencial (m/s²).
        """
        return self.aceleracion_angular_inicial * self.radio

    def aceleracion_centripeta(self, tiempo: Q_) -> Q_:
        """
        Calcula la aceleración centrípeta.
        aₙ = ω² * R

        Args:
            tiempo (Q_): Tiempo transcurrido (s).

        Returns:
            Q_: Aceleración centrípeta (m/s²).
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        return self.velocidad_angular(tiempo) ** 2 * self.radio

    def aceleracion_total(self, tiempo: Q_) -> Q_:
        """
        Calcula la magnitud de la aceleración total.
        a = √(aₜ² + aₙ²)

        Args:
            tiempo (Q_): Tiempo transcurrido (s).

        Returns:
            Q_: Aceleración total (m/s²).
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        at = self.aceleracion_tangencial()
        an = self.aceleracion_centripeta(tiempo)
        return (at**2 + an**2) ** 0.5

    def posicion(self, tiempo: Q_) -> np.ndarray:
        """
        Calcula la posición cartesiana en función del tiempo.

        Args:
            tiempo (Q_): Tiempo transcurrido (s).

        Returns:
            np.ndarray: Vector de posición [x, y] (m).
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        theta = self.posicion_angular(tiempo).to(ureg.radian).magnitude
        x = self.radio * math.cos(theta)
        y = self.radio * math.sin(theta)
        return np.array([x.magnitude, y.magnitude]) * ureg.meter

    def velocidad(self, tiempo: Q_) -> np.ndarray:
        """
        Calcula el vector velocidad en función del tiempo.

        Args:
            tiempo (Q_): Tiempo transcurrido (s).

        Returns:
            np.ndarray: Vector velocidad [vx, vy] (m/s).
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        theta = self.posicion_angular(tiempo).to(ureg.radian).magnitude
        v = self.velocidad_tangencial(tiempo).to(ureg.meter / ureg.second).magnitude
        vx = -v * math.sin(theta)
        vy = v * math.cos(theta)
        return np.array([vx, vy]) * ureg.meter / ureg.second

    def aceleracion(self, tiempo: Q_) -> np.ndarray:
        """
        Calcula el vector aceleración en función del tiempo.

        Args:
            tiempo (Q_): Tiempo transcurrido (s).

        Returns:
            np.ndarray: Vector aceleración [ax, ay] (m/s²).
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)

        omega = self.velocidad_angular(tiempo).to(ureg.radian / ureg.second).magnitude
        alpha = self.aceleracion_angular_inicial.to(
            ureg.radian / ureg.second**2
        ).magnitude
        theta = self.posicion_angular(tiempo).to(ureg.radian).magnitude
        radio_magnitude = self.radio.to(ureg.meter).magnitude

        # Aceleración tangencial
        at_x = -alpha * radio_magnitude * math.sin(theta)
        at_y = alpha * radio_magnitude * math.cos(theta)

        # Aceleración centrípeta
        ac_x = -(omega**2) * radio_magnitude * math.cos(theta)
        ac_y = -(omega**2) * radio_magnitude * math.sin(theta)

        ax = at_x + ac_x
        ay = at_y + ac_y
        return np.array([ax, ay]) * ureg.meter / ureg.second**2

    def aceleracion_angular_constante(self) -> Q_:
        """
        Retorna la aceleración angular constante en MCUV.
        """
        return self.aceleracion_angular_inicial
