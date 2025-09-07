import math
from typing import Union, Optional
from ..base_movimiento import Movimiento
from ...units import ureg, Q_

class MovimientoArmonicoSimple(Movimiento):
    """
    Clase para calcular la posición, velocidad y aceleración en un Movimiento Armónico Simple (M.A.S.).
    """

    def __init__(self, amplitud: Union[float, Q_], frecuencia_angular: Union[float, Q_], fase_inicial: Union[float, Q_] = 0 * ureg.radian) -> None:
        """
        Inicializa el objeto de Movimiento Armónico Simple.

        :param amplitud: Amplitud del movimiento (A).
        :param frecuencia_angular: Frecuencia angular (ω) en radianes/segundo.
        :param fase_inicial: Fase inicial (φ) en radianes. Por defecto es 0.
        """
        if not isinstance(amplitud, Q_):
            amplitud = Q_(amplitud, ureg.meter)
        if not isinstance(frecuencia_angular, Q_):
            frecuencia_angular = Q_(frecuencia_angular, ureg.radian / ureg.second)
        if not isinstance(fase_inicial, Q_):
            fase_inicial = Q_(fase_inicial, ureg.radian)

        if amplitud.magnitude <= 0:
            raise ValueError("La amplitud debe ser un valor positivo.")
        if frecuencia_angular.magnitude <= 0:
            raise ValueError("La frecuencia angular debe ser un valor positivo.")

        self.amplitud = amplitud
        self.frecuencia_angular = frecuencia_angular
        self.fase_inicial = fase_inicial

    def posicion(self, tiempo: Union[float, Q_]) -> Q_:
        """
        Calcula la posición (x) en un tiempo dado.

        x(t) = A * cos(ωt + φ)

        :param tiempo: Tiempo (t) en segundos.
        :return: Posición en el tiempo dado.
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        return self.amplitud * math.cos((self.frecuencia_angular * tiempo + self.fase_inicial).to(ureg.radian).magnitude)

    def velocidad(self, tiempo: Union[float, Q_]) -> Q_:
        """
        Calcula la velocidad (v) en un tiempo dado.

        v(t) = -A * ω * sen(ωt + φ)

        :param tiempo: Tiempo (t) en segundos.
        :return: Velocidad en el tiempo dado.
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        return -self.amplitud * self.frecuencia_angular * math.sin((self.frecuencia_angular * tiempo + self.fase_inicial).to(ureg.radian).magnitude)

    def aceleracion(self, tiempo: Union[float, Q_]) -> Q_:
        """
        Calcula la aceleración (a) en un tiempo dado.

        a(t) = -A * ω^2 * cos(ωt + φ) = -ω^2 * x(t)

        :param tiempo: Tiempo (t) en segundos.
        :return: Aceleración en el tiempo dado.
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        return -self.amplitud * (self.frecuencia_angular ** 2) * math.cos((self.frecuencia_angular * tiempo + self.fase_inicial).to(ureg.radian).magnitude)

    def periodo(self) -> Q_:
        """
        Calcula el período (T) del movimiento.

        T = 2π / ω

        :return: Período del movimiento en segundos.
        """
        return (2 * math.pi * ureg.radian) / self.frecuencia_angular

    def frecuencia(self) -> Q_:
        """
        Calcula la frecuencia (f) del movimiento.

        f = 1 / T = ω / (2π)

        :return: Frecuencia del movimiento en Hertz.
        """
        return self.frecuencia_angular / (2 * math.pi * ureg.radian)

    def energia_cinetica(self, tiempo: Union[float, Q_], masa: Union[float, Q_]) -> Q_:
        """
        Calcula la energía cinética (Ec) en un tiempo dado.

        Ec = 0.5 * m * v(t)^2

        :param tiempo: Tiempo (t) en segundos.
        :param masa: Masa del objeto en kg.
        :return: Energía cinética en Joules.
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        if not isinstance(masa, Q_):
            masa = Q_(masa, ureg.kilogram)

        if masa.magnitude <= 0:
            raise ValueError("La masa debe ser un valor positivo.")
        return 0.5 * masa * (self.velocidad(tiempo) ** 2)

    def energia_potencial(self, tiempo: Union[float, Q_], constante_elastica: Union[float, Q_]) -> Q_:
        """
        Calcula la energía potencial elástica (Ep) en un tiempo dado.

        Ep = 0.5 * k * x(t)^2

        :param tiempo: Tiempo (t) en segundos.
        :param constante_elastica: Constante elástica (k) en N/m.
        :return: Energía potencial en Joules.
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        if not isinstance(constante_elastica, Q_):
            constante_elastica = Q_(constante_elastica, ureg.newton / ureg.meter)

        if constante_elastica.magnitude <= 0:
            raise ValueError("La constante elástica debe ser un valor positivo.")
        return 0.5 * constante_elastica * (self.posicion(tiempo) ** 2)

    def energia_total(self, masa: Union[float, Q_], constante_elastica: Union[float, Q_]) -> Q_:
        """
        Calcula la energía mecánica total (E) del sistema.

        E = 0.5 * k * A^2 = 0.5 * m * A^2 * ω^2

        :param masa: Masa del objeto en kg.
        :param constante_elastica: Constante elástica (k) en N/m.
        :return: Energía total en Joules.
        """
        if not isinstance(masa, Q_):
            masa = Q_(masa, ureg.kilogram)
        if not isinstance(constante_elastica, Q_):
            constante_elastica = Q_(constante_elastica, ureg.newton / ureg.meter)

        if masa.magnitude <= 0 or constante_elastica.magnitude <= 0:
            raise ValueError("La masa y la constante elástica deben ser valores positivos.")
        return 0.5 * constante_elastica * (self.amplitud ** 2)
