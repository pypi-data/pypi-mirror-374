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
    Representa un Movimiento Armónico Complejo (MAC).

    El Movimiento Armónico Complejo es la superposición de múltiples
    Movimientos Armónicos Simples (MAS) con diferentes amplitudes,
    frecuencias y fases iniciales. Permite modelar oscilaciones complejas
    que resultan de la combinación de varios movimientos periódicos.

    Parameters
    ----------
    mas_components : list of dict
        Lista de diccionarios que definen los componentes MAS.
        Cada diccionario debe contener las claves:
        - 'amplitud': Amplitud del componente
        - 'frecuencia_angular': Frecuencia angular del componente
        - 'fase_inicial': Fase inicial del componente

    Attributes
    ----------
    mas_components : list of dict
        Lista procesada de componentes MAS con unidades apropiadas.

    Examples
    --------
    >>> componentes = [
    ...     {'amplitud': 0.1, 'frecuencia_angular': 2*math.pi, 'fase_inicial': 0},
    ...     {'amplitud': 0.05, 'frecuencia_angular': 4*math.pi, 'fase_inicial': math.pi/2}
    ... ]
    >>> mac = MovimientoArmonicoComplejo(componentes)
    >>> pos = mac.posicion(tiempo=0.5)

    Notes
    -----
    El MAC es útil para modelar:
    - Ondas complejas (suma de armónicos)
    - Vibraciones en sistemas con múltiples grados de libertad
    - Señales periódicas complejas
    - Interferencia de ondas
    """

    def __init__(self, mas_components: List[Dict[str, Union[float, Q_]]]) -> None:
        """
        Inicializa una instancia de Movimiento Armónico Complejo.

        Parameters
        ----------
        mas_components : list of dict
            Lista de diccionarios que definen los componentes MAS.
            Cada diccionario debe contener exactamente las siguientes claves:
            - 'amplitud' : float or pint.Quantity
                Amplitud del componente MAS, en metros.
            - 'frecuencia_angular' : float or pint.Quantity
                Frecuencia angular del componente, en rad/s.
            - 'fase_inicial' : float or pint.Quantity
                Fase inicial del componente, en radianes.

        Raises
        ------
        ValueError
            Si mas_components no es una lista no vacía, si algún componente
            no tiene las claves requeridas, o si alguna amplitud o frecuencia
            angular es menor o igual a cero.

        Examples
        --------
        >>> componentes = [
        ...     {'amplitud': 0.1, 'frecuencia_angular': 2*math.pi, 'fase_inicial': 0},
        ...     {'amplitud': 0.05, 'frecuencia_angular': 4*math.pi, 'fase_inicial': math.pi/2}
        ... ]
        >>> mac = MovimientoArmonicoComplejo(componentes)
        >>> from cinetica.units import ureg
        >>> componentes_con_unidades = [
        ...     {
        ...         'amplitud': 0.1 * ureg.meter,
        ...         'frecuencia_angular': 2*math.pi * ureg.radian / ureg.second,
        ...         'fase_inicial': 0 * ureg.radian
        ...     }
        ... ]
        >>> mac = MovimientoArmonicoComplejo(componentes_con_unidades)
        """
        if not isinstance(mas_components, list) or not mas_components:
            raise ValueError(
                "mas_components debe ser una lista no vacía de diccionarios."
            )

        processed_components = []
        for comp in mas_components:
            if not all(
                k in comp for k in ["amplitud", "frecuencia_angular", "fase_inicial"]
            ):
                raise ValueError(
                    "Cada componente MAS debe tener 'amplitud', 'frecuencia_angular' y 'fase_inicial'."
                )

            amplitud = comp["amplitud"]
            frecuencia_angular = comp["frecuencia_angular"]
            fase_inicial = comp["fase_inicial"]

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

            processed_components.append(
                {
                    "amplitud": amplitud,
                    "frecuencia_angular": frecuencia_angular,
                    "fase_inicial": fase_inicial,
                }
            )

        self.mas_components = processed_components

    def posicion(self, tiempo: Union[float, Q_]) -> Q_:
        """
        Calcula la posición resultante del objeto en un tiempo dado.

        La posición total es la superposición de todos los componentes MAS:
        x(t) = Σ Aᵢ · cos(ωᵢ t + φᵢ)

        Parameters
        ----------
        tiempo : float or pint.Quantity
            Tiempo transcurrido desde el inicio del movimiento, en segundos.
            Si se proporciona un float, se asume que está en segundos.

        Returns
        -------
        pint.Quantity
            Posición total resultante de la superposición de todos los componentes,
            con unidades de longitud.

        Examples
        --------
        >>> componentes = [
        ...     {'amplitud': 0.1, 'frecuencia_angular': 2*math.pi, 'fase_inicial': 0},
        ...     {'amplitud': 0.05, 'frecuencia_angular': 4*math.pi, 'fase_inicial': 0}
        ... ]
        >>> mac = MovimientoArmonicoComplejo(componentes)
        >>> pos = mac.posicion(tiempo=0.25)
        >>> print(f"Posición: {pos:.4f}")

        Notes
        -----
        La posición resultante puede ser compleja y no necesariamente periódica
        si las frecuencias de los componentes no son conmensurables.
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)

        posicion_total = 0.0 * ureg.meter
        for comp in self.mas_components:
            A = comp["amplitud"]
            omega = comp["frecuencia_angular"]
            phi = comp["fase_inicial"]
            posicion_total += A * np.cos(
                (omega * tiempo + phi).to(ureg.radian).magnitude
            )
        return posicion_total

    def velocidad(self, tiempo: Union[float, Q_]) -> Q_:
        """
        Calcula la velocidad resultante del objeto en un tiempo dado.

        La velocidad total es la superposición de las velocidades de todos los componentes:
        v(t) = Σ (-Aᵢ · ωᵢ) · sin(ωᵢ t + φᵢ)

        Parameters
        ----------
        tiempo : float or pint.Quantity
            Tiempo transcurrido desde el inicio del movimiento, en segundos.
            Si se proporciona un float, se asume que está en segundos.

        Returns
        -------
        pint.Quantity
            Velocidad total resultante de la superposición de todos los componentes,
            con unidades de velocidad.

        Examples
        --------
        >>> componentes = [
        ...     {'amplitud': 0.1, 'frecuencia_angular': 2*math.pi, 'fase_inicial': 0},
        ...     {'amplitud': 0.05, 'frecuencia_angular': 4*math.pi, 'fase_inicial': 0}
        ... ]
        >>> mac = MovimientoArmonicoComplejo(componentes)
        >>> vel = mac.velocidad(tiempo=0.25)
        >>> print(f"Velocidad: {vel:.4f}")

        Notes
        -----
        La velocidad se obtiene derivando la posición respecto al tiempo.
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)

        velocidad_total = 0.0 * ureg.meter / ureg.second
        for comp in self.mas_components:
            A = comp["amplitud"]
            omega = comp["frecuencia_angular"]
            phi = comp["fase_inicial"]
            velocidad_total += (
                -A * omega * np.sin((omega * tiempo + phi).to(ureg.radian).magnitude)
            )
        return velocidad_total

    def aceleracion(self, tiempo: Union[float, Q_]) -> Q_:
        """
        Calcula la aceleración resultante del objeto en un tiempo dado.

        La aceleración total es la superposición de las aceleraciones de todos los componentes:
        a(t) = Σ (-Aᵢ · ωᵢ²) · cos(ωᵢ t + φᵢ)

        Parameters
        ----------
        tiempo : float or pint.Quantity
            Tiempo transcurrido desde el inicio del movimiento, en segundos.
            Si se proporciona un float, se asume que está en segundos.

        Returns
        -------
        pint.Quantity
            Aceleración total resultante de la superposición de todos los componentes,
            con unidades de aceleración.

        Examples
        --------
        >>> componentes = [
        ...     {'amplitud': 0.1, 'frecuencia_angular': 2*math.pi, 'fase_inicial': 0},
        ...     {'amplitud': 0.05, 'frecuencia_angular': 4*math.pi, 'fase_inicial': 0}
        ... ]
        >>> mac = MovimientoArmonicoComplejo(componentes)
        >>> acel = mac.aceleracion(tiempo=0.25)
        >>> print(f"Aceleración: {acel:.4f}")

        Notes
        -----
        La aceleración se obtiene derivando la velocidad respecto al tiempo.
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)

        aceleracion_total = 0.0 * ureg.meter / ureg.second**2
        for comp in self.mas_components:
            A = comp["amplitud"]
            omega = comp["frecuencia_angular"]
            phi = comp["fase_inicial"]
            aceleracion_total += (
                -A
                * (omega**2)
                * np.cos((omega * tiempo + phi).to(ureg.radian).magnitude)
            )
        return aceleracion_total

    def amplitud_resultante(self) -> Q_:
        """
        Calcula la amplitud resultante para componentes de la misma frecuencia.

        Utiliza la suma fasorial para calcular la amplitud resultante cuando
        todos los componentes tienen la misma frecuencia angular.
        A_resultante = √[(A₁cosφ₁ + A₂cosφ₂ + ...)² + (A₁sinφ₁ + A₂sinφ₂ + ...)²]

        Returns
        -------
        pint.Quantity
            Amplitud resultante del movimiento complejo, con unidades de longitud.

        Raises
        ------
        ValueError
            Si los componentes no tienen todos la misma frecuencia angular.

        Examples
        --------
        >>> componentes = [
        ...     {'amplitud': 0.1, 'frecuencia_angular': 2*math.pi, 'fase_inicial': 0},
        ...     {'amplitud': 0.05, 'frecuencia_angular': 2*math.pi, 'fase_inicial': math.pi/2}
        ... ]
        >>> mac = MovimientoArmonicoComplejo(componentes)
        >>> A_res = mac.amplitud_resultante()
        >>> print(f"Amplitud resultante: {A_res:.4f}")

        Notes
        -----
        Este método solo es aplicable cuando todos los componentes oscilan
        con la misma frecuencia pero diferentes amplitudes y fases.
        """
        if len(self.mas_components) == 0:
            return Q_(0.0, ureg.meter)

        # Check if all components have the same frequency
        freq_ref = self.mas_components[0]["frecuencia_angular"]
        if not all(
            comp["frecuencia_angular"].magnitude == freq_ref.magnitude
            for comp in self.mas_components
        ):
            raise ValueError(
                "Todos los componentes deben tener la misma frecuencia angular para calcular amplitud resultante."
            )

        # Calculate resultant amplitude using phasor addition
        suma_x = 0.0 * ureg.meter
        suma_y = 0.0 * ureg.meter

        for comp in self.mas_components:
            A = comp["amplitud"]
            phi = comp["fase_inicial"]
            suma_x += A * np.cos(phi.to(ureg.radian).magnitude)
            suma_y += A * np.sin(phi.to(ureg.radian).magnitude)

        return ((suma_x**2) + (suma_y**2)) ** 0.5

    def fase_resultante(self) -> Q_:
        """
        Calcula la fase resultante para componentes de la misma frecuencia.

        Utiliza la suma fasorial para calcular la fase resultante cuando
        todos los componentes tienen la misma frecuencia angular.
        φ_resultante = arctan2(ΣAᵢsinφᵢ, ΣAᵢcosφᵢ)

        Returns
        -------
        pint.Quantity
            Fase resultante del movimiento complejo, con unidades de ángulo.

        Raises
        ------
        ValueError
            Si los componentes no tienen todos la misma frecuencia angular.

        Examples
        --------
        >>> componentes = [
        ...     {'amplitud': 0.1, 'frecuencia_angular': 2*math.pi, 'fase_inicial': 0},
        ...     {'amplitud': 0.05, 'frecuencia_angular': 2*math.pi, 'fase_inicial': math.pi/2}
        ... ]
        >>> mac = MovimientoArmonicoComplejo(componentes)
        >>> phi_res = mac.fase_resultante()
        >>> print(f"Fase resultante: {phi_res:.4f}")

        Notes
        -----
        Este método solo es aplicable cuando todos los componentes oscilan
        con la misma frecuencia pero diferentes amplitudes y fases.
        La fase resultante está en el rango [-π, π].
        """
        if len(self.mas_components) == 0:
            return Q_(0.0, ureg.radian)

        # Check if all components have the same frequency
        freq_ref = self.mas_components[0]["frecuencia_angular"]
        if not all(
            comp["frecuencia_angular"].magnitude == freq_ref.magnitude
            for comp in self.mas_components
        ):
            raise ValueError(
                "Todos los componentes deben tener la misma frecuencia angular para calcular fase resultante."
            )

        # Calculate resultant phase using phasor addition
        suma_x = 0.0
        suma_y = 0.0

        for comp in self.mas_components:
            A = comp["amplitud"].magnitude
            phi = comp["fase_inicial"].to(ureg.radian).magnitude
            suma_x += A * np.cos(phi)
            suma_y += A * np.sin(phi)

        return Q_(np.arctan2(suma_y, suma_x), ureg.radian)
