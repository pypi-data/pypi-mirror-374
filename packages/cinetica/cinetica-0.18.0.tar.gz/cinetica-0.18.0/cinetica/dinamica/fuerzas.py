"""
Módulo de análisis de fuerzas para sistemas dinámicos.

Este módulo proporciona herramientas para el análisis de diferentes tipos de
fuerzas que actúan en sistemas físicos, incluyendo fuerzas de fricción,
fuerzas elásticas, fuerzas gravitacionales y análisis de diagramas de cuerpo libre.
"""

import math
from typing import Union, List, Optional, Tuple, Dict
import numpy as np
from ..units import ureg, Q_


class AnalisisFuerzas:
    """
    Herramientas para análisis de fuerzas en sistemas físicos.

    Esta clase proporciona métodos para calcular y analizar diferentes tipos
    de fuerzas, crear diagramas de cuerpo libre y resolver problemas de
    estática y dinámica.

    Examples
    --------
    >>> from cinetica.dinamica import AnalisisFuerzas
    >>> fuerzas = AnalisisFuerzas()
    >>> f_friccion = fuerzas.friccion_estatica(normal=100, coeficiente=0.3)
    >>> print(f"Fricción estática máxima: {f_friccion}")
    Fricción estática máxima: 30.0 newton
    """

    def __init__(self) -> None:
        """Inicializa una instancia de AnalisisFuerzas."""
        pass

    def friccion_estatica(
        self,
        normal: Union[float, Q_],
        coeficiente: float
    ) -> Q_:
        """
        Calcula la fuerza de fricción estática máxima.

        Parameters
        ----------
        normal : float or pint.Quantity
            Fuerza normal en N.
        coeficiente : float
            Coeficiente de fricción estática (adimensional).

        Returns
        -------
        pint.Quantity
            Fuerza de fricción estática máxima en N.

        Examples
        --------
        >>> fuerzas = AnalisisFuerzas()
        >>> f_s = fuerzas.friccion_estatica(normal=200, coeficiente=0.4)
        >>> print(f"Fricción estática: {f_s}")
        Fricción estática: 80.0 newton

        Notes
        -----
        La fricción estática máxima se calcula como: f_s = μ_s * N
        donde μ_s es el coeficiente de fricción estática y N la fuerza normal.
        """
        if not isinstance(normal, Q_):
            normal = Q_(normal, ureg.newton)

        if coeficiente < 0:
            raise ValueError("El coeficiente de fricción debe ser no negativo")

        return coeficiente * normal

    def friccion_cinetica(
        self,
        normal: Union[float, Q_],
        coeficiente: float
    ) -> Q_:
        """
        Calcula la fuerza de fricción cinética.

        Parameters
        ----------
        normal : float or pint.Quantity
            Fuerza normal en N.
        coeficiente : float
            Coeficiente de fricción cinética (adimensional).

        Returns
        -------
        pint.Quantity
            Fuerza de fricción cinética en N.

        Examples
        --------
        >>> fuerzas = AnalisisFuerzas()
        >>> f_k = fuerzas.friccion_cinetica(normal=150, coeficiente=0.25)
        >>> print(f"Fricción cinética: {f_k}")
        Fricción cinética: 37.5 newton

        Notes
        -----
        La fricción cinética se calcula como: f_k = μ_k * N
        donde μ_k es el coeficiente de fricción cinética y N la fuerza normal.
        """
        if not isinstance(normal, Q_):
            normal = Q_(normal, ureg.newton)

        if coeficiente < 0:
            raise ValueError("El coeficiente de fricción debe ser no negativo")

        return coeficiente * normal

    def fuerza_elastica(
        self,
        constante: Union[float, Q_],
        deformacion: Union[float, Q_]
    ) -> Q_:
        """
        Calcula la fuerza elástica según la ley de Hooke.

        Parameters
        ----------
        constante : float or pint.Quantity
            Constante elástica del resorte en N/m.
        deformacion : float or pint.Quantity
            Deformación del resorte en m.

        Returns
        -------
        pint.Quantity
            Fuerza elástica en N.

        Examples
        --------
        >>> fuerzas = AnalisisFuerzas()
        >>> F_elastica = fuerzas.fuerza_elastica(constante=500, deformacion=0.1)
        >>> print(f"Fuerza elástica: {F_elastica}")
        Fuerza elástica: 50.0 newton

        Notes
        -----
        La ley de Hooke establece que: F = -k * x
        donde k es la constante elástica y x la deformación.
        El signo negativo indica que la fuerza se opone a la deformación.
        """
        if not isinstance(constante, Q_):
            constante = Q_(constante, ureg.newton / ureg.meter)
        if not isinstance(deformacion, Q_):
            deformacion = Q_(deformacion, ureg.meter)

        if constante.magnitude < 0:
            raise ValueError("La constante elástica debe ser positiva")

        return constante * deformacion

    def fuerza_gravitacional(
        self,
        masa1: Union[float, Q_],
        masa2: Union[float, Q_],
        distancia: Union[float, Q_],
        G: Union[float, Q_] = 6.67430e-11
    ) -> Q_:
        """
        Calcula la fuerza gravitacional entre dos masas.

        Parameters
        ----------
        masa1 : float or pint.Quantity
            Primera masa en kg.
        masa2 : float or pint.Quantity
            Segunda masa en kg.
        distancia : float or pint.Quantity
            Distancia entre las masas en m.
        G : float or pint.Quantity, optional
            Constante gravitacional. Default 6.67430e-11 m³/(kg⋅s²).

        Returns
        -------
        pint.Quantity
            Fuerza gravitacional en N.

        Examples
        --------
        >>> fuerzas = AnalisisFuerzas()
        >>> F_grav = fuerzas.fuerza_gravitacional(masa1=100, masa2=200, distancia=10)
        >>> print(f"Fuerza gravitacional: {F_grav}")

        Notes
        -----
        La ley de gravitación universal de Newton: F = G * m1 * m2 / r²
        donde G es la constante gravitacional universal.
        """
        if not isinstance(masa1, Q_):
            masa1 = Q_(masa1, ureg.kilogram)
        if not isinstance(masa2, Q_):
            masa2 = Q_(masa2, ureg.kilogram)
        if not isinstance(distancia, Q_):
            distancia = Q_(distancia, ureg.meter)
        if not isinstance(G, Q_):
            G = Q_(G, ureg.meter**3 / (ureg.kilogram * ureg.second**2))

        if distancia.magnitude <= 0:
            raise ValueError("La distancia debe ser positiva")
        if masa1.magnitude <= 0 or masa2.magnitude <= 0:
            raise ValueError("Las masas deben ser positivas")

        return G * masa1 * masa2 / (distancia**2)

    def descomponer_fuerza(
        self,
        magnitud: Union[float, Q_],
        angulo: Union[float, Q_]
    ) -> Tuple[Q_, Q_]:
        """
        Descompone una fuerza en sus componentes rectangulares.

        Parameters
        ----------
        magnitud : float or pint.Quantity
            Magnitud de la fuerza en N.
        angulo : float or pint.Quantity
            Ángulo con respecto al eje x positivo en radianes.

        Returns
        -------
        tuple of pint.Quantity
            Componentes (Fx, Fy) de la fuerza en N.

        Examples
        --------
        >>> fuerzas = AnalisisFuerzas()
        >>> Fx, Fy = fuerzas.descomponer_fuerza(magnitud=100, angulo=math.pi/4)
        >>> print(f"Fx: {Fx:.2f}, Fy: {Fy:.2f}")
        """
        if not isinstance(magnitud, Q_):
            magnitud = Q_(magnitud, ureg.newton)
        if not isinstance(angulo, Q_):
            angulo = Q_(angulo, ureg.radian)

        if magnitud.magnitude < 0:
            raise ValueError("La magnitud de la fuerza debe ser no negativa")

        Fx = magnitud * math.cos(angulo.to(ureg.radian).magnitude)
        Fy = magnitud * math.sin(angulo.to(ureg.radian).magnitude)

        return Fx, Fy

    def magnitud_y_direccion(
        self,
        Fx: Union[float, Q_],
        Fy: Union[float, Q_]
    ) -> Tuple[Q_, Q_]:
        """
        Calcula la magnitud y dirección de una fuerza a partir de sus componentes.

        Parameters
        ----------
        Fx : float or pint.Quantity
            Componente x de la fuerza en N.
        Fy : float or pint.Quantity
            Componente y de la fuerza en N.

        Returns
        -------
        tuple of pint.Quantity
            Magnitud de la fuerza en N y ángulo en radianes.

        Examples
        --------
        >>> fuerzas = AnalisisFuerzas()
        >>> mag, ang = fuerzas.magnitud_y_direccion(Fx=30, Fy=40)
        >>> print(f"Magnitud: {mag}, Ángulo: {ang}")
        """
        if not isinstance(Fx, Q_):
            Fx = Q_(Fx, ureg.newton)
        if not isinstance(Fy, Q_):
            Fy = Q_(Fy, ureg.newton)

        magnitud = (Fx**2 + Fy**2)**0.5
        angulo = Q_(math.atan2(Fy.magnitude, Fx.magnitude), ureg.radian)

        return magnitud, angulo

    def plano_inclinado(
        self,
        peso: Union[float, Q_],
        angulo: Union[float, Q_]
    ) -> Tuple[Q_, Q_]:
        """
        Descompone el peso en un plano inclinado.

        Parameters
        ----------
        peso : float or pint.Quantity
            Peso del objeto en N.
        angulo : float or pint.Quantity
            Ángulo de inclinación del plano en radianes.

        Returns
        -------
        tuple of pint.Quantity
            Componentes (paralela, perpendicular) al plano en N.

        Examples
        --------
        >>> fuerzas = AnalisisFuerzas()
        >>> F_par, F_perp = fuerzas.plano_inclinado(peso=100, angulo=math.pi/6)
        >>> print(f"Paralela: {F_par:.2f}, Perpendicular: {F_perp:.2f}")

        Notes
        -----
        En un plano inclinado:
        - Componente paralela: W * sin(θ) (hacia abajo del plano)
        - Componente perpendicular: W * cos(θ) (hacia el plano)
        """
        if not isinstance(peso, Q_):
            peso = Q_(peso, ureg.newton)
        if not isinstance(angulo, Q_):
            angulo = Q_(angulo, ureg.radian)

        if peso.magnitude < 0:
            raise ValueError("El peso debe ser positivo")

        angulo_rad = angulo.to(ureg.radian).magnitude

        F_paralela = peso * math.sin(angulo_rad)
        F_perpendicular = peso * math.cos(angulo_rad)

        return F_paralela, F_perpendicular

    def tension_cuerda(
        self,
        masa: Union[float, Q_],
        aceleracion: Union[float, Q_] = 0,
        angulo: Union[float, Q_] = 0,
        gravedad: Union[float, Q_] = 9.81
    ) -> Q_:
        """
        Calcula la tensión en una cuerda.

        Parameters
        ----------
        masa : float or pint.Quantity
            Masa del objeto suspendido en kg.
        aceleracion : float or pint.Quantity, optional
            Aceleración del sistema en m/s². Default 0 (equilibrio).
        angulo : float or pint.Quantity, optional
            Ángulo de la cuerda con la vertical en radianes. Default 0.
        gravedad : float or pint.Quantity, optional
            Aceleración gravitacional en m/s². Default 9.81.

        Returns
        -------
        pint.Quantity
            Tensión en la cuerda en N.

        Examples
        --------
        >>> fuerzas = AnalisisFuerzas()
        >>> T = fuerzas.tension_cuerda(masa=10)  # Objeto colgando en equilibrio
        >>> print(f"Tensión: {T}")
        Tensión: 98.1 newton

        >>> # Con aceleración hacia arriba
        >>> T_acel = fuerzas.tension_cuerda(masa=10, aceleracion=2)
        >>> print(f"Tensión con aceleración: {T_acel}")
        """
        if not isinstance(masa, Q_):
            masa = Q_(masa, ureg.kilogram)
        if not isinstance(aceleracion, Q_):
            aceleracion = Q_(aceleracion, ureg.meter / ureg.second**2)
        if not isinstance(angulo, Q_):
            angulo = Q_(angulo, ureg.radian)
        if not isinstance(gravedad, Q_):
            gravedad = Q_(gravedad, ureg.meter / ureg.second**2)

        if masa.magnitude <= 0:
            raise ValueError("La masa debe ser positiva")

        # Para cuerda vertical: T = m(g + a)
        # Para cuerda inclinada: T = m(g + a) / cos(θ)
        angulo_rad = angulo.to(ureg.radian).magnitude

        if abs(angulo_rad) > math.pi/2 - 1e-10:
            raise ValueError("El ángulo debe ser menor a 90 grados")

        tension = masa * (gravedad + aceleracion)

        if abs(angulo_rad) > 1e-10:  # Si hay ángulo
            tension = tension / math.cos(angulo_rad)

        return tension
