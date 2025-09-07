from abc import ABC, abstractmethod
from typing import Union, Any
import numpy as np
from ..units import Q_

class Movimiento(ABC):
    """
    Clase base abstracta para diferentes tipos de movimiento.
    Define una interfaz común para la posición, velocidad y aceleración.
    """

    @abstractmethod
    def posicion(self, tiempo: Union[float, Q_]) -> Union[float, Q_, np.ndarray]:
        """
        Calcula la posición del objeto en un tiempo dado.
        Debe ser implementado por las subclases.
        
        Args:
            tiempo: Tiempo en segundos (puede ser float o Quantity)
            
        Returns:
            Posición del objeto (puede ser float, Quantity o array)
        """
        pass

    @abstractmethod
    def velocidad(self, tiempo: Union[float, Q_]) -> Union[float, Q_, np.ndarray]:
        """
        Calcula la velocidad del objeto en un tiempo dado.
        Debe ser implementado por las subclases.
        
        Args:
            tiempo: Tiempo en segundos (puede ser float o Quantity)
            
        Returns:
            Velocidad del objeto (puede ser float, Quantity o array)
        """
        pass

    @abstractmethod
    def aceleracion(self, tiempo: Union[float, Q_, None] = None) -> Union[float, Q_, np.ndarray]:
        """
        Calcula la aceleración del objeto en un tiempo dado.
        Debe ser implementado por las subclases.
        
        Args:
            tiempo: Tiempo en segundos (puede ser float, Quantity o None)
            
        Returns:
            Aceleración del objeto (puede ser float, Quantity o array)
        """
        pass
