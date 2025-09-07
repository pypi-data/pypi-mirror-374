"""
Módulo que implementa el Movimiento Rectilíneo Uniforme (MRU)
"""

from typing import Union, Optional
from ..base_movimiento import Movimiento
from ...units import ureg, Q_

class MovimientoRectilineoUniforme(Movimiento):
    """
    Clase para calcular posición y velocidad en Movimiento Rectilíneo Uniforme (MRU).
    """

    def __init__(self, posicion_inicial: Union[float, Q_] = 0.0 * ureg.meter, velocidad_inicial: Union[float, Q_] = 0.0 * ureg.meter / ureg.second) -> None:
        """
        Inicializa el objeto MovimientoRectilineoUniforme con condiciones iniciales.

        Args:
            posicion_inicial (Q_): Posición inicial del objeto (m).
            velocidad_inicial (Q_): Velocidad inicial del objeto (m/s).
        """
        if not isinstance(posicion_inicial, Q_):
            posicion_inicial = Q_(posicion_inicial, ureg.meter)
        if not isinstance(velocidad_inicial, Q_):
            velocidad_inicial = Q_(velocidad_inicial, ureg.meter / ureg.second)

        self.posicion_inicial = posicion_inicial
        self.velocidad_inicial = velocidad_inicial

    def posicion(self, tiempo: Union[float, Q_]) -> Q_:
        """
        Calcula la posición en MRU.
        Ecuación: x = x0 + v * t

        Args:
            tiempo (Q_): Tiempo transcurrido (s).

        Returns:
            Q_: Posición final (m).
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        return self.posicion_inicial + self.velocidad_inicial * tiempo

    def velocidad(self, tiempo: Optional[Union[float, Q_]] = None) -> Q_:
        """
        Obtiene la velocidad en MRU.
        En MRU la velocidad es constante.

        Args:
            tiempo (Q_, optional): Tiempo transcurrido (s). No afecta al resultado.

        Returns:
            Q_: Velocidad (m/s).
        """
        return self.velocidad_inicial

    def aceleracion(self, tiempo: Optional[Union[float, Q_]] = None) -> Q_:
        """
        Obtiene la aceleración en MRU.
        En MRU la aceleración es siempre 0.

        Args:
            tiempo (Q_, optional): Tiempo transcurrido (s). No afecta al resultado.

        Returns:
            Q_: Aceleración (m/s²).
        """
        return 0.0 * ureg.meter / ureg.second**2
