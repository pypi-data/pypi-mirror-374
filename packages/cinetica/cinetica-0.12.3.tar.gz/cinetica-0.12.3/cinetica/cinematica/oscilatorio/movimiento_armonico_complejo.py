"""
Módulo para el Movimiento Armónico Complejo (MAC).

Este módulo define clases y funciones para simular y analizar el movimiento
armónico complejo, que es la superposición de varios movimientos armónicos simples.
"""

from typing import List, Dict, Union, Optional, Any
import numpy as np
from ..base_movimiento import Movimiento
from ...units import ureg, Q_

class MovimientoArmonicoComplejo(Movimiento):
    """
    Representa un Movimiento Armónico Complejo (MAC) como la superposición
    de múltiples Movimientos Armónicos Simples (MAS).
    """
    def __init__(self, mas_components: List[Dict[str, Union[float, Q_]]]) -> None:
        """
        Inicializa un objeto de Movimiento Armónico Complejo.

        Args:
            mas_components (list): Una lista de diccionarios, donde cada diccionario
                                   representa un MAS con las siguientes claves:
                                   - 'amplitud' (Q_): Amplitud del MAS (m).
                                   - 'frecuencia_angular' (Q_): Frecuencia angular (omega) del MAS (rad/s).
                                   - 'fase_inicial' (Q_): Fase inicial (phi) del MAS en radianes.
        """
        if not isinstance(mas_components, list) or not mas_components:
            raise ValueError("mas_components debe ser una lista no vacía de diccionarios.")
        
        processed_components = []
        for comp in mas_components:
            if not all(k in comp for k in ['amplitud', 'frecuencia_angular', 'fase_inicial']):
                raise ValueError("Cada componente MAS debe tener 'amplitud', 'frecuencia_angular' y 'fase_inicial'.")
            
            amplitud = comp['amplitud']
            frecuencia_angular = comp['frecuencia_angular']
            fase_inicial = comp['fase_inicial']

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

            processed_components.append({
                'amplitud': amplitud,
                'frecuencia_angular': frecuencia_angular,
                'fase_inicial': fase_inicial
            })

        self.mas_components = processed_components

    def posicion(self, tiempo: Union[float, Q_]) -> Q_:
        """
        Calcula la posición del objeto en un tiempo dado para el MAC.

        Args:
            tiempo (Q_): El tiempo o array de tiempos en segundos.

        Returns:
            Q_: La posición total en el tiempo especificado.
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)

        posicion_total = 0.0 * ureg.meter
        for comp in self.mas_components:
            A = comp['amplitud']
            omega = comp['frecuencia_angular']
            phi = comp['fase_inicial']
            posicion_total += A * np.cos((omega * tiempo + phi).to(ureg.radian).magnitude)
        return posicion_total

    def velocidad(self, tiempo: Union[float, Q_]) -> Q_:
        """
        Calcula la velocidad del objeto en un tiempo dado para el MAC.

        Args:
            tiempo (Q_): El tiempo en segundos.

        Returns:
            Q_: La velocidad total en el tiempo especificado.
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)

        velocidad_total = 0.0 * ureg.meter / ureg.second
        for comp in self.mas_components:
            A = comp['amplitud']
            omega = comp['frecuencia_angular']
            phi = comp['fase_inicial']
            velocidad_total += -A * omega * np.sin((omega * tiempo + phi).to(ureg.radian).magnitude)
        return velocidad_total

    def aceleracion(self, tiempo: Union[float, Q_]) -> Q_:
        """
        Calcula la aceleración del objeto en un tiempo dado para el MAC.

        Args:
            tiempo (Q_): El tiempo en segundos.

        Returns:
            Q_: La aceleración total en el tiempo especificado.
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)

        aceleracion_total = 0.0 * ureg.meter / ureg.second**2
        for comp in self.mas_components:
            A = comp['amplitud']
            omega = comp['frecuencia_angular']
            phi = comp['fase_inicial']
            aceleracion_total += -A * (omega**2) * np.cos((omega * tiempo + phi).to(ureg.radian).magnitude)
        return aceleracion_total

    def amplitud_resultante(self) -> Q_:
        """
        Calcula la amplitud resultante para componentes de la misma frecuencia.
        Solo funciona si todos los componentes tienen la misma frecuencia angular.
        
        Returns:
            Q_: Amplitud resultante en metros.
        """
        if len(self.mas_components) == 0:
            return Q_(0.0, ureg.meter)
        
        # Check if all components have the same frequency
        freq_ref = self.mas_components[0]['frecuencia_angular']
        if not all(comp['frecuencia_angular'].magnitude == freq_ref.magnitude for comp in self.mas_components):
            raise ValueError("Todos los componentes deben tener la misma frecuencia angular para calcular amplitud resultante.")
        
        # Calculate resultant amplitude using phasor addition
        suma_x = 0.0 * ureg.meter
        suma_y = 0.0 * ureg.meter
        
        for comp in self.mas_components:
            A = comp['amplitud']
            phi = comp['fase_inicial']
            suma_x += A * np.cos(phi.to(ureg.radian).magnitude)
            suma_y += A * np.sin(phi.to(ureg.radian).magnitude)
        
        return ((suma_x ** 2) + (suma_y ** 2)) ** 0.5
    
    def fase_resultante(self) -> Q_:
        """
        Calcula la fase resultante para componentes de la misma frecuencia.
        Solo funciona si todos los componentes tienen la misma frecuencia angular.
        
        Returns:
            Q_: Fase resultante en radianes.
        """
        if len(self.mas_components) == 0:
            return Q_(0.0, ureg.radian)
        
        # Check if all components have the same frequency
        freq_ref = self.mas_components[0]['frecuencia_angular']
        if not all(comp['frecuencia_angular'].magnitude == freq_ref.magnitude for comp in self.mas_components):
            raise ValueError("Todos los componentes deben tener la misma frecuencia angular para calcular fase resultante.")
        
        # Calculate resultant phase using phasor addition
        suma_x = 0.0
        suma_y = 0.0
        
        for comp in self.mas_components:
            A = comp['amplitud'].magnitude
            phi = comp['fase_inicial'].to(ureg.radian).magnitude
            suma_x += A * np.cos(phi)
            suma_y += A * np.sin(phi)
        
        return Q_(np.arctan2(suma_y, suma_x), ureg.radian)
