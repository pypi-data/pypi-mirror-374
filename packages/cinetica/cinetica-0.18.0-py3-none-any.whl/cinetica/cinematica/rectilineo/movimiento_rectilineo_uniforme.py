"""
Módulo que implementa el Movimiento Rectilíneo Uniforme (MRU)
"""

from typing import Union, Optional
from ..base_movimiento import Movimiento
from ...units import ureg, Q_


class MovimientoRectilineoUniforme(Movimiento):
    """
    Movimiento Rectilíneo Uniforme (MRU).

    Implementa los cálculos para un objeto que se mueve en línea recta
    con velocidad constante. En este tipo de movimiento, la aceleración
    es siempre cero y la posición varía linealmente con el tiempo.

    Parameters
    ----------
    posicion_inicial : float or pint.Quantity, optional
        Posición inicial del objeto en metros. Default es 0.0 m.
    velocidad_inicial : float or pint.Quantity, optional
        Velocidad constante del objeto en m/s. Default es 0.0 m/s.

    Attributes
    ----------
    posicion_inicial : pint.Quantity
        Posición inicial del objeto con unidades de longitud.
    velocidad_inicial : pint.Quantity
        Velocidad constante del objeto con unidades de velocidad.

    Examples
    --------
    >>> from cinetica.cinematica.rectilineo import MovimientoRectilineoUniforme
    >>> mru = MovimientoRectilineoUniforme(posicion_inicial=10, velocidad_inicial=5)
    >>> posicion_final = mru.posicion(tiempo=3)
    >>> print(f"Posición a los 3s: {posicion_final}")
    Posición a los 3s: 25.0 meter

    Notes
    -----
    Las ecuaciones fundamentales del MRU son:
    - Posición: x(t) = x₀ + v·t
    - Velocidad: v(t) = v₀ (constante)
    - Aceleración: a(t) = 0
    """

    def __init__(
        self,
        posicion_inicial: Union[float, Q_] = 0.0 * ureg.meter,
        velocidad_inicial: Union[float, Q_] = 0.0 * ureg.meter / ureg.second,
    ) -> None:
        """
        Inicializa una instancia de Movimiento Rectilíneo Uniforme.

        Parameters
        ----------
        posicion_inicial : float or pint.Quantity, optional
            Posición inicial del objeto en metros. Si se proporciona un float,
            se asume que está en metros. Default es 0.0 m.
        velocidad_inicial : float or pint.Quantity, optional
            Velocidad constante del objeto en m/s. Si se proporciona un float,
            se asume que está en m/s. Default es 0.0 m/s.

        Examples
        --------
        >>> mru = MovimientoRectilineoUniforme()
        >>> mru = MovimientoRectilineoUniforme(posicion_inicial=10, velocidad_inicial=5)
        >>> from cinetica.units import ureg
        >>> mru = MovimientoRectilineoUniforme(
        ...     posicion_inicial=10 * ureg.meter,
        ...     velocidad_inicial=5 * ureg.meter / ureg.second
        ... )
        """
        if not isinstance(posicion_inicial, Q_):
            posicion_inicial = Q_(posicion_inicial, ureg.meter)
        if not isinstance(velocidad_inicial, Q_):
            velocidad_inicial = Q_(velocidad_inicial, ureg.meter / ureg.second)

        self.posicion_inicial = posicion_inicial
        self.velocidad_inicial = velocidad_inicial

    def posicion(self, tiempo: Union[float, Q_]) -> Q_:
        """
        Calcula la posición del objeto en un tiempo dado.

        Utiliza la ecuación fundamental del MRU: x(t) = x₀ + v·t

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
        >>> mru = MovimientoRectilineoUniforme(posicion_inicial=10, velocidad_inicial=5)
        >>> pos = mru.posicion(tiempo=3)
        >>> print(f"Posición: {pos}")
        Posición: 25.0 meter
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        return self.posicion_inicial + self.velocidad_inicial * tiempo

    def velocidad(self, tiempo: Optional[Union[float, Q_]] = None) -> Q_:
        """
        Obtiene la velocidad del objeto en cualquier momento.

        En el MRU, la velocidad es constante e independiente del tiempo.

        Parameters
        ----------
        tiempo : float, pint.Quantity, or None, optional
            Tiempo transcurrido en segundos. Este parámetro no afecta el resultado
            ya que la velocidad es constante en MRU. Default es None.

        Returns
        -------
        pint.Quantity
            Velocidad constante del objeto, con unidades de velocidad.

        Examples
        --------
        >>> mru = MovimientoRectilineoUniforme(velocidad_inicial=5)
        >>> vel = mru.velocidad()
        >>> print(f"Velocidad: {vel}")
        Velocidad: 5.0 meter / second
        """
        return self.velocidad_inicial

    def aceleracion(self, tiempo: Optional[Union[float, Q_]] = None) -> Q_:
        """
        Obtiene la aceleración del objeto en cualquier momento.

        En el MRU, la aceleración es siempre cero ya que la velocidad es constante.

        Parameters
        ----------
        tiempo : float, pint.Quantity, or None, optional
            Tiempo transcurrido en segundos. Este parámetro no afecta el resultado
            ya que la aceleración es siempre cero en MRU. Default es None.

        Returns
        -------
        pint.Quantity
            Aceleración del objeto (siempre 0), con unidades de aceleración.

        Examples
        --------
        >>> mru = MovimientoRectilineoUniforme()
        >>> acel = mru.aceleracion()
        >>> print(f"Aceleración: {acel}")
        Aceleración: 0.0 meter / second ** 2
        """
        return 0.0 * ureg.meter / ureg.second**2
