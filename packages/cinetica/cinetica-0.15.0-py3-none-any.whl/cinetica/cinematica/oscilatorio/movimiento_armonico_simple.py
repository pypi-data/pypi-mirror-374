import math
from typing import Union, Optional
from ..base_movimiento import Movimiento
from ...units import ureg, Q_


class MovimientoArmonicoSimple(Movimiento):
    """
    Clase para simular Movimiento Armónico Simple (M.A.S.).

    El Movimiento Armónico Simple es un tipo de movimiento periódico donde
    la fuerza restauradora es proporcional al desplazamiento y actúa en
    dirección opuesta al mismo. La ecuación característica es x(t) = A·cos(ωt + φ)

    Parameters
    ----------
    amplitud : float or pint.Quantity
        Amplitud máxima del movimiento oscilatorio.
    frecuencia_angular : float or pint.Quantity
        Frecuencia angular del movimiento en rad/s.
    fase_inicial : float or pint.Quantity, optional
        Fase inicial del movimiento en radianes. Default es 0.

    Attributes
    ----------
    amplitud : pint.Quantity
        Amplitud máxima del desplazamiento.
    frecuencia_angular : pint.Quantity
        Frecuencia angular en rad/s.
    fase_inicial : pint.Quantity
        Fase inicial en radianes.

    Examples
    --------
    >>> mas = MovimientoArmonicoSimple(
    ...     amplitud=0.1, frecuencia_angular=2*math.pi
    ... )
    >>> pos = mas.posicion(tiempo=0.25)
    >>> print(f"Posición: {pos}")

    Notes
    -----
    El M.A.S. es fundamental en física y aparece en sistemas como:
    - Péndulos simples (para pequeños ángulos)
    - Resortes con masa
    - Circuitos LC
    - Vibraciones moleculares
    """

    def __init__(
        self,
        amplitud: Union[float, Q_],
        frecuencia_angular: Union[float, Q_],
        fase_inicial: Union[float, Q_] = 0 * ureg.radian,
    ) -> None:
        """
        Inicializa una instancia de Movimiento Armónico Simple.

        Parameters
        ----------
        amplitud : float or pint.Quantity
            Amplitud máxima del movimiento oscilatorio, en metros.
            Si se proporciona un float, se asume que está en metros.
            Debe ser un valor positivo.
        frecuencia_angular : float or pint.Quantity
            Frecuencia angular del movimiento, en rad/s.
            Si se proporciona un float, se asume que está en rad/s.
            Debe ser un valor positivo.
        fase_inicial : float or pint.Quantity, optional
            Fase inicial del movimiento, en radianes.
            Si se proporciona un float, se asume que está en radianes.
            Default es 0 rad.

        Raises
        ------
        ValueError
            Si la amplitud o la frecuencia angular son menores o iguales a cero.

        Examples
        --------
        >>> mas = MovimientoArmonicoSimple(amplitud=0.1, frecuencia_angular=2*math.pi)
        >>> from cinetica.units import ureg
        >>> mas = MovimientoArmonicoSimple(
        ...     amplitud=0.1 * ureg.meter,
        ...     frecuencia_angular=2*math.pi * ureg.radian / ureg.second,
        ...     fase_inicial=math.pi/4 * ureg.radian
        ... )
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
        Calcula la posición del objeto en un tiempo dado.

        Utiliza la ecuación fundamental del M.A.S.:
        x(t) = A·cos(ωt + φ)

        Parameters
        ----------
        tiempo : float or pint.Quantity
            Tiempo transcurrido desde el inicio del movimiento, en segundos.
            Si se proporciona un float, se asume que está en segundos.

        Returns
        -------
        pint.Quantity
            Posición del objeto en el tiempo especificado, con unidades de longitud.

        Examples
        --------
        >>> mas = MovimientoArmonicoSimple(
        ...     amplitud=0.1, frecuencia_angular=2*math.pi
        ... )
        >>> pos = mas.posicion(tiempo=0.25)
        >>> print(f"Posición: {pos:.3f}")
        Posición: -0.100 meter

        Notes
        -----
        La posición varía sinusoidalmente entre -A y +A.
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        return self.amplitud * math.cos(
            (self.frecuencia_angular * tiempo + self.fase_inicial)
            .to(ureg.radian)
            .magnitude
        )

    def velocidad(self, tiempo: Union[float, Q_]) -> Q_:
        """
        Calcula la velocidad del objeto en un tiempo dado.

        Utiliza la derivada de la posición respecto al tiempo:
        v(t) = -A·ω·sin(ωt + φ)

        Parameters
        ----------
        tiempo : float or pint.Quantity
            Tiempo transcurrido desde el inicio del movimiento, en segundos.
            Si se proporciona un float, se asume que está en segundos.

        Returns
        -------
        pint.Quantity
            Velocidad del objeto en el tiempo especificado, con unidades de velocidad.

        Examples
        --------
        >>> mas = MovimientoArmonicoSimple(
        ...     amplitud=0.1, frecuencia_angular=2*math.pi
        ... )
        >>> vel = mas.velocidad(tiempo=0)
        >>> print(f"Velocidad: {vel:.3f}")
        Velocidad: 0.000 meter / second

        Notes
        -----
        La velocidad es máxima cuando el objeto pasa por la posición de equilibrio
        y es cero en los puntos de máximo desplazamiento.
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        return (
            -self.amplitud
            * self.frecuencia_angular
            * math.sin(
                (self.frecuencia_angular * tiempo + self.fase_inicial)
                .to(ureg.radian)
                .magnitude
            )
        )

    def aceleracion(self, tiempo: Union[float, Q_]) -> Q_:
        """
        Calcula la aceleración del objeto en un tiempo dado.

        Utiliza la segunda derivada de la posición respecto al tiempo:
        a(t) = -A·ω²·cos(ωt + φ) = -ω²·x(t)

        Parameters
        ----------
        tiempo : float or pint.Quantity
            Tiempo transcurrido desde el inicio del movimiento, en segundos.
            Si se proporciona un float, se asume que está en segundos.

        Returns
        -------
        pint.Quantity
            Aceleración del objeto en el tiempo especificado, con unidades de aceleración.

        Examples
        --------
        >>> mas = MovimientoArmonicoSimple(
        ...     amplitud=0.1, frecuencia_angular=2*math.pi
        ... )
        >>> acel = mas.aceleracion(tiempo=0)
        >>> print(f"Aceleración: {acel:.3f}")
        Aceleración: -3.948 meter / second ** 2

        Notes
        -----
        La aceleración es proporcional al desplazamiento pero en dirección opuesta,
        lo que constituye la fuerza restauradora característica del M.A.S.
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        return (
            -self.amplitud
            * (self.frecuencia_angular**2)
            * math.cos(
                (self.frecuencia_angular * tiempo + self.fase_inicial)
                .to(ureg.radian)
                .magnitude
            )
        )

    def periodo(self) -> Q_:
        """
        Calcula el período del movimiento oscilatorio.

        El período es el tiempo necesario para completar una oscilación completa.
        Se calcula como T = 2π/ω

        Returns
        -------
        pint.Quantity
            Período del movimiento, con unidades de tiempo.

        Examples
        --------
        >>> mas = MovimientoArmonicoSimple(
        ...     amplitud=0.1, frecuencia_angular=2*math.pi
        ... )
        >>> T = mas.periodo()
        >>> print(f"Período: {T:.2f}")
        Período: 1.00 second

        Notes
        -----
        El período es independiente de la amplitud en el M.A.S. ideal.
        """
        return (2 * math.pi * ureg.radian) / self.frecuencia_angular

    def frecuencia(self) -> Q_:
        """
        Calcula la frecuencia del movimiento oscilatorio.

        La frecuencia es el número de oscilaciones completadas por unidad de tiempo.
        Se calcula como f = 1/T = ω/(2π)

        Returns
        -------
        pint.Quantity
            Frecuencia del movimiento, con unidades de frecuencia (Hz).

        Examples
        --------
        >>> mas = MovimientoArmonicoSimple(
        ...     amplitud=0.1, frecuencia_angular=2*math.pi
        ... )
        >>> f = mas.frecuencia()
        >>> print(f"Frecuencia: {f:.2f}")
        Frecuencia: 1.00 hertz

        Notes
        -----
        La frecuencia es el inverso del período: f = 1/T
        """
        return self.frecuencia_angular / (2 * math.pi * ureg.radian)

    def energia_cinetica(self, tiempo: Union[float, Q_], masa: Union[float, Q_]) -> Q_:
        """
        Calcula la energía cinética del objeto en un tiempo dado.

        La energía cinética en M.A.S. varía con el tiempo según:
        Eᶜ = ½·m·v(t)²

        Parameters
        ----------
        tiempo : float or pint.Quantity
            Tiempo transcurrido desde el inicio del movimiento, en segundos.
            Si se proporciona un float, se asume que está en segundos.
        masa : float or pint.Quantity
            Masa del objeto oscilante, en kg.
            Si se proporciona un float, se asume que está en kg.
            Debe ser un valor positivo.

        Returns
        -------
        pint.Quantity
            Energía cinética en el tiempo especificado, con unidades de energía.

        Raises
        ------
        ValueError
            Si la masa es menor o igual a cero.

        Examples
        --------
        >>> mas = MovimientoArmonicoSimple(
        ...     amplitud=0.1, frecuencia_angular=2*math.pi
        ... )
        >>> Ec = mas.energia_cinetica(tiempo=0.25, masa=1)
        >>> print(f"Energía cinética: {Ec:.4f}")

        Notes
        -----
        La energía cinética es máxima en la posición de equilibrio
        y cero en los puntos de máximo desplazamiento.
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        if not isinstance(masa, Q_):
            masa = Q_(masa, ureg.kilogram)

        if masa.magnitude <= 0:
            raise ValueError("La masa debe ser un valor positivo.")
        return 0.5 * masa * (self.velocidad(tiempo) ** 2)

    def energia_potencial(
        self, tiempo: Union[float, Q_], constante_elastica: Union[float, Q_]
    ) -> Q_:
        """
        Calcula la energía potencial elástica del objeto en un tiempo dado.

        La energía potencial elástica en M.A.S. varía con el tiempo según:
        Eₚ = ½·k·x(t)²

        Parameters
        ----------
        tiempo : float or pint.Quantity
            Tiempo transcurrido desde el inicio del movimiento, en segundos.
            Si se proporciona un float, se asume que está en segundos.
        constante_elastica : float or pint.Quantity
            Constante elástica del resorte, en N/m.
            Si se proporciona un float, se asume que está en N/m.
            Debe ser un valor positivo.

        Returns
        -------
        pint.Quantity
            Energía potencial en el tiempo especificado, con unidades de energía.

        Raises
        ------
        ValueError
            Si la constante elástica es menor o igual a cero.

        Examples
        --------
        >>> mas = MovimientoArmonicoSimple(
        ...     amplitud=0.1, frecuencia_angular=2*math.pi
        ... )
        >>> Ep = mas.energia_potencial(tiempo=0, constante_elastica=10)
        >>> print(f"Energía potencial: {Ep:.4f}")

        Notes
        -----
        La energía potencial es máxima en los puntos de máximo desplazamiento
        y cero en la posición de equilibrio.
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        if not isinstance(constante_elastica, Q_):
            constante_elastica = Q_(constante_elastica, ureg.newton / ureg.meter)

        if constante_elastica.magnitude <= 0:
            raise ValueError("La constante elástica debe ser un valor positivo.")
        return 0.5 * constante_elastica * (self.posicion(tiempo) ** 2)

    def energia_total(
        self, masa: Union[float, Q_], constante_elastica: Union[float, Q_]
    ) -> Q_:
        """
        Calcula la energía mecánica total del sistema oscilante.

        En M.A.S., la energía total se conserva y es constante:
        E = ½·k·A² = ½·m·A²·ω²

        Parameters
        ----------
        masa : float or pint.Quantity
            Masa del objeto oscilante, en kg.
            Si se proporciona un float, se asume que está en kg.
            Debe ser un valor positivo.
        constante_elastica : float or pint.Quantity
            Constante elástica del resorte, en N/m.
            Si se proporciona un float, se asume que está en N/m.
            Debe ser un valor positivo.

        Returns
        -------
        pint.Quantity
            Energía mecánica total del sistema, con unidades de energía.

        Raises
        ------
        ValueError
            Si la masa o la constante elástica son menores o iguales a cero.

        Examples
        --------
        >>> mas = MovimientoArmonicoSimple(
        ...     amplitud=0.1, frecuencia_angular=2*math.pi
        ... )
        >>> E_total = mas.energia_total(masa=1, constante_elastica=10)
        >>> print(f"Energía total: {E_total:.4f}")

        Notes
        -----
        La energía total es la suma de las energías cinética y potencial,
        y permanece constante durante todo el movimiento (conservación de energía).
        """
        if not isinstance(masa, Q_):
            masa = Q_(masa, ureg.kilogram)
        if not isinstance(constante_elastica, Q_):
            constante_elastica = Q_(constante_elastica, ureg.newton / ureg.meter)

        if masa.magnitude <= 0 or constante_elastica.magnitude <= 0:
            raise ValueError(
                "La masa y la constante elástica deben ser valores positivos."
            )
        return 0.5 * constante_elastica * (self.amplitud**2)
