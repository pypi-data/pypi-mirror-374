from abc import ABC, abstractmethod
from typing import Union, Any
import numpy as np
from ..units import Q_


class Movimiento(ABC):
    """
    Clase base abstracta para diferentes tipos de movimiento.

    Esta clase define una interfaz común que debe ser implementada por todas
    las clases de movimiento específicas. Proporciona métodos abstractos para
    calcular posición, velocidad y aceleración en función del tiempo.

    Notes
    -----
    Esta es una clase abstracta que no puede ser instanciada directamente.
    Todas las subclases deben implementar los métodos abstractos definidos.

    See Also
    --------
    MovimientoRectilineoUniforme : Implementación para MRU
    MovimientoRectilineoUniformementeVariado : Implementación para MRUV
    MovimientoCircularUniforme : Implementación para MCU
    """

    @abstractmethod
    def posicion(self, tiempo: Union[float, Q_]) -> Union[float, Q_, np.ndarray]:
        """
        Calcula la posición del objeto en un tiempo dado.

        Este método debe ser implementado por todas las subclases para definir
        cómo se calcula la posición específica según el tipo de movimiento.

        Parameters
        ----------
        tiempo : float or pint.Quantity
            Tiempo transcurrido desde el inicio del movimiento, en segundos.
            Puede ser un valor numérico (float) o una cantidad con unidades (Quantity).

        Returns
        -------
        float or pint.Quantity or numpy.ndarray
            Posición del objeto en el tiempo especificado. El tipo de retorno
            depende de la implementación específica:
            - float: Para movimientos unidimensionales sin unidades
            - pint.Quantity: Para movimientos con unidades físicas
            - numpy.ndarray: Para movimientos multidimensionales

        Raises
        ------
        NotImplementedError
            Si el método no ha sido implementado en la subclase.
        """
        pass

    @abstractmethod
    def velocidad(self, tiempo: Union[float, Q_]) -> Union[float, Q_, np.ndarray]:
        """
        Calcula la velocidad del objeto en un tiempo dado.

        Este método debe ser implementado por todas las subclases para definir
        cómo se calcula la velocidad específica según el tipo de movimiento.

        Parameters
        ----------
        tiempo : float or pint.Quantity
            Tiempo transcurrido desde el inicio del movimiento, en segundos.
            Puede ser un valor numérico (float) o una cantidad con unidades (Quantity).

        Returns
        -------
        float or pint.Quantity or numpy.ndarray
            Velocidad del objeto en el tiempo especificado. El tipo de retorno
            depende de la implementación específica:
            - float: Para movimientos unidimensionales sin unidades
            - pint.Quantity: Para movimientos con unidades físicas
            - numpy.ndarray: Para movimientos multidimensionales

        Raises
        ------
        NotImplementedError
            Si el método no ha sido implementado en la subclase.
        """
        pass

    @abstractmethod
    def aceleracion(
        self, tiempo: Union[float, Q_, None] = None
    ) -> Union[float, Q_, np.ndarray]:
        """
        Calcula la aceleración del objeto en un tiempo dado.

        Este método debe ser implementado por todas las subclases para definir
        cómo se calcula la aceleración específica según el tipo de movimiento.

        Parameters
        ----------
        tiempo : float, pint.Quantity, or None, optional
            Tiempo transcurrido desde el inicio del movimiento, en segundos.
            Puede ser un valor numérico (float), una cantidad con unidades (Quantity),
            o None para movimientos con aceleración constante. Default es None.

        Returns
        -------
        float or pint.Quantity or numpy.ndarray
            Aceleración del objeto en el tiempo especificado. El tipo de retorno
            depende de la implementación específica:
            - float: Para movimientos unidimensionales sin unidades
            - pint.Quantity: Para movimientos con unidades físicas
            - numpy.ndarray: Para movimientos multidimensionales

        Raises
        ------
        NotImplementedError
            Si el método no ha sido implementado en la subclase.
        """
        pass
