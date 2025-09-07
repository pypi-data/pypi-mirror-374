import math
from typing import Union, Optional
import numpy as np
from ..base_movimiento import Movimiento
from ...units import ureg, Q_

class MovimientoCircularUniforme(Movimiento):
    """
    Clase para calcular y simular Movimiento Circular Uniforme (MCU).
    """

    def __init__(self, radio: Union[float, Q_], posicion_angular_inicial: Union[float, Q_] = 0.0 * ureg.radian, velocidad_angular_inicial: Union[float, Q_] = 0.0 * ureg.radian / ureg.second) -> None:
        """
        Inicializa el objeto MovimientoCircularUniforme con las condiciones iniciales.

        Args:
            radio (Q_): Radio de la trayectoria circular (m).
            posicion_angular_inicial (Q_): Posición angular inicial (radianes).
            velocidad_angular_inicial (Q_): Velocidad angular inicial (rad/s).
        
        Raises:
            ValueError: Si el radio es menor o igual a cero.
        """
        if not isinstance(radio, Q_):
            radio = Q_(radio, ureg.meter)
        if not isinstance(posicion_angular_inicial, Q_):
            posicion_angular_inicial = Q_(posicion_angular_inicial, ureg.radian)
        if not isinstance(velocidad_angular_inicial, Q_):
            velocidad_angular_inicial = Q_(velocidad_angular_inicial, ureg.radian / ureg.second)

        if radio.magnitude <= 0:
            raise ValueError("El radio debe ser un valor positivo.")

        self.radio = radio
        self.posicion_angular_inicial = posicion_angular_inicial
        self.velocidad_angular_inicial = velocidad_angular_inicial

    def posicion_angular(self, tiempo: Union[float, Q_]) -> Q_:
        """
        Calcula la posición angular en función del tiempo.
        θ = θ₀ + ω * t

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
        return self.posicion_angular_inicial + self.velocidad_angular_inicial * tiempo

    def velocidad_angular(self, tiempo: Optional[Union[float, Q_]] = None) -> Q_:
        """
        Obtiene la velocidad angular (constante en MCU).

        Args:
            tiempo (Q_, optional): Tiempo transcurrido (s). No afecta al resultado.

        Returns:
            Q_: Velocidad angular (rad/s).
        """
        return self.velocidad_angular_inicial

    def velocidad_tangencial(self, tiempo: Optional[Union[float, Q_]] = None) -> Q_:
        """
        Calcula la velocidad tangencial.
        v = ω * R

        Args:
            tiempo (Q_, optional): Tiempo transcurrido (s). No afecta al resultado.

        Returns:
            Q_: Velocidad tangencial (m/s).
        """
        return self.velocidad_angular_inicial * self.radio

    def aceleracion_centripeta(self, tiempo: Optional[Union[float, Q_]] = None) -> Q_:
        """
        Calcula la aceleración centrípeta.
        aₙ = ω² * R = v² / R

        Args:
            tiempo (Q_, optional): Tiempo transcurrido (s). No afecta al resultado.

        Returns:
            Q_: Aceleración centrípeta (m/s²).
        """
        return self.velocidad_angular_inicial**2 * self.radio

    def posicion(self, tiempo: Union[float, Q_]) -> np.ndarray:
        """
        Calcula la posición (x, y) del objeto en un tiempo dado.

        Args:
            tiempo (Q_): Tiempo transcurrido (s).

        Returns:
            np.ndarray: Vector de posición [x, y] (m).
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        if tiempo.magnitude < 0:
            raise ValueError("El tiempo no puede ser negativo.")
        theta = self.posicion_angular(tiempo).to(ureg.radian).magnitude
        x = self.radio * math.cos(theta)
        y = self.radio * math.sin(theta)
        return Q_(np.array([x.magnitude, y.magnitude]), ureg.meter)

    def velocidad(self, tiempo: Union[float, Q_]) -> Q_:
        """
        Calcula la velocidad (vx, vy) del objeto en un tiempo dado.

        Args:
            tiempo (Q_): Tiempo transcurrido (s).

        Returns:
            Q_: Vector de velocidad [vx, vy] (m/s).
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        if tiempo.magnitude < 0:
            raise ValueError("El tiempo no puede ser negativo.")
        omega = self.velocidad_angular_inicial.to(ureg.radian/ureg.second).magnitude
        theta = self.posicion_angular(tiempo).to(ureg.radian).magnitude
        vx = -omega * self.radio.to(ureg.meter).magnitude * math.sin(theta)
        vy = omega * self.radio.to(ureg.meter).magnitude * math.cos(theta)
        return Q_(np.array([vx, vy]), ureg.meter / ureg.second)

    def aceleracion(self, tiempo: Union[float, Q_]) -> Q_:
        """
        Calcula la aceleración (ax, ay) del objeto en un tiempo dado (aceleración centrípeta).

        Args:
            tiempo (Q_): Tiempo transcurrido (s).

        Returns:
            Q_: Vector de aceleración [ax, ay] (m/s^2).
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        if tiempo.magnitude < 0:
            raise ValueError("El tiempo no puede ser negativo.")
        omega = self.velocidad_angular_inicial.to(ureg.radian/ureg.second).magnitude
        theta = self.posicion_angular(tiempo).to(ureg.radian).magnitude
        ac = (omega ** 2) * self.radio.to(ureg.meter).magnitude
        ax = -ac * math.cos(theta)
        ay = -ac * math.sin(theta)
        return Q_(np.array([ax, ay]), ureg.meter / ureg.second**2)

    def velocidad_angular_constante(self) -> Q_:
        """
        Retorna la velocidad angular constante en MCU.
        """
        return self.velocidad_angular_inicial

    def aceleracion_centripeta_constante(self) -> Q_:
        """
        Retorna la magnitud de la aceleración centrípeta constante en MCU.
        """
        return (self.velocidad_angular_inicial ** 2) * self.radio

    def periodo(self) -> Q_:
        """
        Calcula el período en MCU.
        Ecuación: T = 2 * pi / omega

        Returns:
            Q_: Período (s).
        
        Notes:
            Retorna `math.inf * ureg.second` si la velocidad angular inicial es cero.
        """
        if self.velocidad_angular_inicial.magnitude == 0:
            return math.inf * ureg.second  # Período infinito si la velocidad angular es cero
        return (2 * math.pi * ureg.radian) / self.velocidad_angular_inicial

    def frecuencia(self) -> Q_:
        """
        Calcula la frecuencia en MCU.
        Ecuación: f = 1 / T = omega / (2 * pi)

        Returns:
            Q_: Frecuencia (Hz).
        
        Notes:
            Retorna `0.0 * ureg.hertz` si la velocidad angular inicial es cero.
        """
        if self.velocidad_angular_inicial.magnitude == 0:
            return 0.0 * ureg.hertz  # Frecuencia cero si la velocidad angular es cero
        return self.velocidad_angular_inicial / (2 * math.pi * ureg.radian)
