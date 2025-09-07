"""
Módulo de trabajo y energía para análisis dinámico.

Este módulo implementa los conceptos fundamentales de trabajo, energía cinética,
energía potencial y el teorema trabajo-energía para el análisis de sistemas
mecánicos.
"""

import math
from typing import Union, List, Optional, Tuple
import numpy as np
from ..units import ureg, Q_


class TrabajoEnergia:
    """
    Análisis de trabajo y energía en sistemas mecánicos.

    Esta clase proporciona métodos para calcular trabajo, energías cinética
    y potencial, y aplicar el teorema trabajo-energía en problemas de mecánica.

    Examples
    --------
    >>> from cinetica.dinamica import TrabajoEnergia
    >>> te = TrabajoEnergia()
    >>> trabajo = te.trabajo_fuerza_constante(fuerza=50, desplazamiento=10)
    >>> print(f"Trabajo: {trabajo}")
    Trabajo: 500.0 joule
    """

    def __init__(self) -> None:
        """Inicializa una instancia de TrabajoEnergia."""
        pass

    def trabajo_fuerza_constante(
        self,
        fuerza: Union[float, Q_],
        desplazamiento: Union[float, Q_],
        angulo: Union[float, Q_] = 0
    ) -> Q_:
        """
        Calcula el trabajo realizado por una fuerza constante.

        Parameters
        ----------
        fuerza : float or pint.Quantity
            Magnitud de la fuerza en N.
        desplazamiento : float or pint.Quantity
            Magnitud del desplazamiento en m.
        angulo : float or pint.Quantity, optional
            Ángulo entre la fuerza y el desplazamiento en radianes. Default 0.

        Returns
        -------
        pint.Quantity
            Trabajo realizado en J.

        Examples
        --------
        >>> te = TrabajoEnergia()
        >>> W = te.trabajo_fuerza_constante(fuerza=100, desplazamiento=5)
        >>> print(f"Trabajo: {W}")
        Trabajo: 500.0 joule

        >>> # Fuerza a 60 grados del desplazamiento
        >>> W_angulo = te.trabajo_fuerza_constante(fuerza=100, desplazamiento=5,
        ...                                        angulo=math.pi/3)
        >>> print(f"Trabajo con ángulo: {W_angulo}")

        Notes
        -----
        El trabajo se calcula como: W = F · d = F * d * cos(θ)
        donde θ es el ángulo entre la fuerza y el desplazamiento.
        """
        if not isinstance(fuerza, Q_):
            fuerza = Q_(fuerza, ureg.newton)
        if not isinstance(desplazamiento, Q_):
            desplazamiento = Q_(desplazamiento, ureg.meter)
        if not isinstance(angulo, Q_):
            angulo = Q_(angulo, ureg.radian)

        if fuerza.magnitude < 0:
            raise ValueError("La magnitud de la fuerza debe ser no negativa")
        if desplazamiento.magnitude < 0:
            raise ValueError("La magnitud del desplazamiento debe ser no negativa")

        angulo_rad = angulo.to(ureg.radian).magnitude
        trabajo = fuerza * desplazamiento * math.cos(angulo_rad)

        return trabajo.to(ureg.joule)

    def trabajo_vectorial(
        self,
        fuerza: Union[List[float], np.ndarray, Q_],
        desplazamiento: Union[List[float], np.ndarray, Q_]
    ) -> Q_:
        """
        Calcula el trabajo usando el producto punto de vectores.

        Parameters
        ----------
        fuerza : list, numpy.ndarray, or pint.Quantity
            Vector fuerza en N.
        desplazamiento : list, numpy.ndarray, or pint.Quantity
            Vector desplazamiento en m.

        Returns
        -------
        pint.Quantity
            Trabajo realizado en J.

        Examples
        --------
        >>> te = TrabajoEnergia()
        >>> F = [10, 20, 0]  # Fuerza en 3D
        >>> d = [5, 0, 0]    # Desplazamiento en 3D
        >>> W = te.trabajo_vectorial(fuerza=F, desplazamiento=d)
        >>> print(f"Trabajo vectorial: {W}")
        """
        if not isinstance(fuerza, Q_):
            fuerza = Q_(np.array(fuerza), ureg.newton)
        if not isinstance(desplazamiento, Q_):
            desplazamiento = Q_(np.array(desplazamiento), ureg.meter)

        # Verificar que ambos vectores tengan la misma dimensión
        if len(fuerza.magnitude) != len(desplazamiento.magnitude):
            raise ValueError("Los vectores fuerza y desplazamiento deben tener la misma dimensión")

        trabajo = np.dot(fuerza.magnitude, desplazamiento.magnitude)
        return Q_(trabajo, ureg.joule)

    def energia_cinetica(self, masa: Union[float, Q_], velocidad: Union[float, Q_]) -> Q_:
        """
        Calcula la energía cinética de un objeto.

        Parameters
        ----------
        masa : float or pint.Quantity
            Masa del objeto en kg.
        velocidad : float or pint.Quantity
            Velocidad del objeto en m/s.

        Returns
        -------
        pint.Quantity
            Energía cinética en J.

        Examples
        --------
        >>> te = TrabajoEnergia()
        >>> Ec = te.energia_cinetica(masa=10, velocidad=5)
        >>> print(f"Energía cinética: {Ec}")
        Energía cinética: 125.0 joule

        Notes
        -----
        La energía cinética se calcula como: Ec = (1/2) * m * v²
        """
        if not isinstance(masa, Q_):
            masa = Q_(masa, ureg.kilogram)
        if not isinstance(velocidad, Q_):
            velocidad = Q_(velocidad, ureg.meter / ureg.second)

        if masa.magnitude <= 0:
            raise ValueError("La masa debe ser positiva")
        if velocidad.magnitude < 0:
            raise ValueError("La velocidad debe ser no negativa")

        energia = 0.5 * masa * velocidad**2
        return energia.to(ureg.joule)

    def energia_potencial_gravitacional(
        self,
        masa: Union[float, Q_],
        altura: Union[float, Q_],
        gravedad: Union[float, Q_] = 9.81
    ) -> Q_:
        """
        Calcula la energía potencial gravitacional.

        Parameters
        ----------
        masa : float or pint.Quantity
            Masa del objeto en kg.
        altura : float or pint.Quantity
            Altura sobre el nivel de referencia en m.
        gravedad : float or pint.Quantity, optional
            Aceleración gravitacional en m/s². Default 9.81.

        Returns
        -------
        pint.Quantity
            Energía potencial gravitacional en J.

        Examples
        --------
        >>> te = TrabajoEnergia()
        >>> Ep = te.energia_potencial_gravitacional(masa=5, altura=10)
        >>> print(f"Energía potencial: {Ep}")
        Energía potencial: 490.5 joule

        Notes
        -----
        La energía potencial gravitacional: Ep = m * g * h
        """
        if not isinstance(masa, Q_):
            masa = Q_(masa, ureg.kilogram)
        if not isinstance(altura, Q_):
            altura = Q_(altura, ureg.meter)
        if not isinstance(gravedad, Q_):
            gravedad = Q_(gravedad, ureg.meter / ureg.second**2)

        if masa.magnitude <= 0:
            raise ValueError("La masa debe ser positiva")

        energia = masa * gravedad * altura
        return energia.to(ureg.joule)

    def energia_potencial_elastica(
        self,
        constante: Union[float, Q_],
        deformacion: Union[float, Q_]
    ) -> Q_:
        """
        Calcula la energía potencial elástica de un resorte.

        Parameters
        ----------
        constante : float or pint.Quantity
            Constante elástica del resorte en N/m.
        deformacion : float or pint.Quantity
            Deformación del resorte en m.

        Returns
        -------
        pint.Quantity
            Energía potencial elástica en J.

        Examples
        --------
        >>> te = TrabajoEnergia()
        >>> Ep_elastica = te.energia_potencial_elastica(constante=200, deformacion=0.1)
        >>> print(f"Energía potencial elástica: {Ep_elastica}")
        Energía potencial elástica: 1.0 joule

        Notes
        -----
        La energía potencial elástica: Ep = (1/2) * k * x²
        """
        if not isinstance(constante, Q_):
            constante = Q_(constante, ureg.newton / ureg.meter)
        if not isinstance(deformacion, Q_):
            deformacion = Q_(deformacion, ureg.meter)

        if constante.magnitude < 0:
            raise ValueError("La constante elástica debe ser no negativa")

        energia = 0.5 * constante * deformacion**2
        return energia.to(ureg.joule)

    def energia_mecanica_total(
        self,
        energia_cinetica: Union[float, Q_],
        energia_potencial: Union[float, Q_]
    ) -> Q_:
        """
        Calcula la energía mecánica total del sistema.

        Parameters
        ----------
        energia_cinetica : float or pint.Quantity
            Energía cinética en J.
        energia_potencial : float or pint.Quantity
            Energía potencial en J.

        Returns
        -------
        pint.Quantity
            Energía mecánica total en J.

        Examples
        --------
        >>> te = TrabajoEnergia()
        >>> Em = te.energia_mecanica_total(energia_cinetica=100, energia_potencial=50)
        >>> print(f"Energía mecánica total: {Em}")
        Energía mecánica total: 150.0 joule

        Notes
        -----
        La energía mecánica total: Em = Ec + Ep
        En sistemas conservativos, la energía mecánica se conserva.
        """
        if not isinstance(energia_cinetica, Q_):
            energia_cinetica = Q_(energia_cinetica, ureg.joule)
        if not isinstance(energia_potencial, Q_):
            energia_potencial = Q_(energia_potencial, ureg.joule)

        return energia_cinetica + energia_potencial

    def teorema_trabajo_energia(
        self,
        masa: Union[float, Q_],
        velocidad_inicial: Union[float, Q_],
        velocidad_final: Union[float, Q_]
    ) -> Q_:
        """
        Aplica el teorema trabajo-energía para calcular el trabajo neto.

        Parameters
        ----------
        masa : float or pint.Quantity
            Masa del objeto en kg.
        velocidad_inicial : float or pint.Quantity
            Velocidad inicial en m/s.
        velocidad_final : float or pint.Quantity
            Velocidad final en m/s.

        Returns
        -------
        pint.Quantity
            Trabajo neto realizado en J.

        Examples
        --------
        >>> te = TrabajoEnergia()
        >>> W_neto = te.teorema_trabajo_energia(masa=10, velocidad_inicial=0,
        ...                                    velocidad_final=5)
        >>> print(f"Trabajo neto: {W_neto}")
        Trabajo neto: 125.0 joule

        Notes
        -----
        El teorema trabajo-energía: W_neto = ΔEc = Ec_final - Ec_inicial
        """
        if not isinstance(masa, Q_):
            masa = Q_(masa, ureg.kilogram)
        if not isinstance(velocidad_inicial, Q_):
            velocidad_inicial = Q_(velocidad_inicial, ureg.meter / ureg.second)
        if not isinstance(velocidad_final, Q_):
            velocidad_final = Q_(velocidad_final, ureg.meter / ureg.second)

        if masa.magnitude <= 0:
            raise ValueError("La masa debe ser positiva")

        Ec_inicial = self.energia_cinetica(masa, velocidad_inicial)
        Ec_final = self.energia_cinetica(masa, velocidad_final)

        return Ec_final - Ec_inicial

    def potencia(
        self,
        trabajo: Union[float, Q_],
        tiempo: Union[float, Q_]
    ) -> Q_:
        """
        Calcula la potencia como trabajo por unidad de tiempo.

        Parameters
        ----------
        trabajo : float or pint.Quantity
            Trabajo realizado en J.
        tiempo : float or pint.Quantity
            Tiempo transcurrido en s.

        Returns
        -------
        pint.Quantity
            Potencia en W.

        Examples
        --------
        >>> te = TrabajoEnergia()
        >>> P = te.potencia(trabajo=1000, tiempo=10)
        >>> print(f"Potencia: {P}")
        Potencia: 100.0 watt

        Notes
        -----
        La potencia se define como: P = W / t
        También puede expresarse como: P = F · v (fuerza por velocidad)
        """
        if not isinstance(trabajo, Q_):
            trabajo = Q_(trabajo, ureg.joule)
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)

        if tiempo.magnitude <= 0:
            raise ValueError("El tiempo debe ser positivo")

        potencia = trabajo / tiempo
        return potencia.to(ureg.watt)

    def potencia_instantanea(
        self,
        fuerza: Union[float, Q_],
        velocidad: Union[float, Q_]
    ) -> Q_:
        """
        Calcula la potencia instantánea.

        Parameters
        ----------
        fuerza : float or pint.Quantity
            Fuerza aplicada en N.
        velocidad : float or pint.Quantity
            Velocidad instantánea en m/s.

        Returns
        -------
        pint.Quantity
            Potencia instantánea en W.

        Examples
        --------
        >>> te = TrabajoEnergia()
        >>> P_inst = te.potencia_instantanea(fuerza=50, velocidad=10)
        >>> print(f"Potencia instantánea: {P_inst}")
        Potencia instantánea: 500.0 watt

        Notes
        -----
        La potencia instantánea: P = F · v
        """
        if not isinstance(fuerza, Q_):
            fuerza = Q_(fuerza, ureg.newton)
        if not isinstance(velocidad, Q_):
            velocidad = Q_(velocidad, ureg.meter / ureg.second)

        potencia = fuerza * velocidad
        return potencia.to(ureg.watt)
