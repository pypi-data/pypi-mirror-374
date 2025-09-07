"""
Módulo de Leyes de Newton para análisis dinámico.

Este módulo implementa las tres leyes fundamentales de Newton para el análisis
de sistemas dinámicos, incluyendo cálculos de fuerza, masa, aceleración y
aplicaciones de las leyes del movimiento.
"""

import math
from typing import Union, List, Optional, Tuple
import numpy as np
from ..units import ureg, Q_


class LeyesNewton:
    """
    Implementación de las tres leyes de Newton para análisis dinámico.

    Esta clase proporciona métodos para aplicar las leyes fundamentales del
    movimiento de Newton en sistemas físicos, incluyendo cálculos de fuerza,
    masa, aceleración y análisis de equilibrio.

    Examples
    --------
    >>> from cinetica.dinamica import LeyesNewton
    >>> newton = LeyesNewton()
    >>> fuerza = newton.segunda_ley(masa=10, aceleracion=5)
    >>> print(f"Fuerza: {fuerza}")
    Fuerza: 50.0 newton

    Notes
    -----
    Las tres leyes de Newton son:
    1. Primera Ley (Inercia): Un objeto en reposo permanece en reposo, y un
       objeto en movimiento permanece en movimiento a velocidad constante,
       a menos que actúe sobre él una fuerza neta.
    2. Segunda Ley: F = ma, la fuerza neta es igual al producto de la masa
       por la aceleración.
    3. Tercera Ley (Acción-Reacción): Para cada acción hay una reacción
       igual y opuesta.
    """

    def __init__(self) -> None:
        """Inicializa una instancia de LeyesNewton."""
        pass

    def segunda_ley(
        self,
        masa: Optional[Union[float, Q_]] = None,
        aceleracion: Optional[Union[float, Q_, np.ndarray]] = None,
        fuerza: Optional[Union[float, Q_, np.ndarray]] = None
    ) -> Union[Q_, np.ndarray]:
        """
        Aplica la segunda ley de Newton: F = ma.

        Calcula la fuerza, masa o aceleración dados los otros dos parámetros.
        Puede trabajar con vectores para análisis en múltiples dimensiones.

        Parameters
        ----------
        masa : float, pint.Quantity, or None
            Masa del objeto en kg. Si se proporciona un float, se asume kg.
        aceleracion : float, pint.Quantity, numpy.ndarray, or None
            Aceleración del objeto en m/s². Puede ser escalar o vectorial.
        fuerza : float, pint.Quantity, numpy.ndarray, or None
            Fuerza aplicada en N. Puede ser escalar o vectorial.

        Returns
        -------
        pint.Quantity or numpy.ndarray
            El parámetro faltante calculado con las unidades apropiadas.

        Raises
        ------
        ValueError
            Si no se proporcionan exactamente dos de los tres parámetros.
            Si la masa es menor o igual a cero.

        Examples
        --------
        >>> newton = LeyesNewton()
        >>> # Calcular fuerza
        >>> F = newton.segunda_ley(masa=10, aceleracion=5)
        >>> print(f"Fuerza: {F}")
        Fuerza: 50.0 newton

        >>> # Calcular masa
        >>> m = newton.segunda_ley(fuerza=100, aceleracion=10)
        >>> print(f"Masa: {m}")
        Masa: 10.0 kilogram

        >>> # Análisis vectorial
        >>> a_vec = newton.segunda_ley(masa=5, fuerza=np.array([10, 20, 0]))
        >>> print(f"Aceleración vectorial: {a_vec}")
        """
        # Contar parámetros no nulos
        params_provided = sum(x is not None for x in [masa, aceleracion, fuerza])

        if params_provided != 2:
            raise ValueError("Debe proporcionar exactamente dos de los tres parámetros: masa, aceleración, fuerza")

        # Convertir a cantidades con unidades si es necesario
        if masa is not None:
            if not isinstance(masa, Q_):
                masa = Q_(masa, ureg.kilogram)
            if masa.magnitude <= 0:
                raise ValueError("La masa debe ser un valor positivo")

        if aceleracion is not None and not isinstance(aceleracion, Q_):
            if isinstance(aceleracion, np.ndarray):
                aceleracion = Q_(aceleracion, ureg.meter / ureg.second**2)
            else:
                aceleracion = Q_(aceleracion, ureg.meter / ureg.second**2)

        if fuerza is not None and not isinstance(fuerza, Q_):
            if isinstance(fuerza, np.ndarray):
                fuerza = Q_(fuerza, ureg.newton)
            else:
                fuerza = Q_(fuerza, ureg.newton)

        # Calcular el parámetro faltante
        if masa is None:
            # m = F / a
            return fuerza / aceleracion
        elif aceleracion is None:
            # a = F / m
            return fuerza / masa
        else:
            # F = m * a
            return masa * aceleracion

    def fuerza_neta(self, fuerzas: List[Union[float, Q_, np.ndarray]]) -> Union[Q_, np.ndarray]:
        """
        Calcula la fuerza neta como suma vectorial de todas las fuerzas.

        Parameters
        ----------
        fuerzas : list of float, pint.Quantity, or numpy.ndarray
            Lista de fuerzas a sumar. Pueden ser escalares o vectoriales.

        Returns
        -------
        pint.Quantity or numpy.ndarray
            Fuerza neta resultante con unidades apropiadas.

        Examples
        --------
        >>> newton = LeyesNewton()
        >>> fuerzas = [10, -5, 8]  # Fuerzas en 1D
        >>> F_neta = newton.fuerza_neta(fuerzas)
        >>> print(f"Fuerza neta: {F_neta}")
        Fuerza neta: 13.0 newton

        >>> # Fuerzas vectoriales en 2D
        >>> fuerzas_2d = [np.array([10, 0]), np.array([0, 15]), np.array([-5, -3])]
        >>> F_neta_2d = newton.fuerza_neta(fuerzas_2d)
        """
        if not fuerzas:
            raise ValueError("Debe proporcionar al menos una fuerza")

        # Convertir todas las fuerzas a cantidades con unidades
        fuerzas_convertidas = []
        for fuerza in fuerzas:
            if not isinstance(fuerza, Q_):
                if isinstance(fuerza, np.ndarray):
                    fuerzas_convertidas.append(Q_(fuerza, ureg.newton))
                else:
                    fuerzas_convertidas.append(Q_(fuerza, ureg.newton))
            else:
                fuerzas_convertidas.append(fuerza)

        # Sumar todas las fuerzas
        fuerza_neta = fuerzas_convertidas[0]
        for fuerza in fuerzas_convertidas[1:]:
            fuerza_neta = fuerza_neta + fuerza

        return fuerza_neta

    def equilibrio(
        self,
        fuerzas: List[Union[float, Q_, np.ndarray]],
        tolerancia: float = 1e-10
    ) -> bool:
        """
        Verifica si un sistema está en equilibrio (fuerza neta ≈ 0).

        Parameters
        ----------
        fuerzas : list of float, pint.Quantity, or numpy.ndarray
            Lista de fuerzas actuando sobre el sistema.
        tolerancia : float, optional
            Tolerancia para considerar la fuerza neta como cero. Default 1e-10.

        Returns
        -------
        bool
            True si el sistema está en equilibrio, False en caso contrario.

        Examples
        --------
        >>> newton = LeyesNewton()
        >>> fuerzas_equilibrio = [10, -10]
        >>> en_equilibrio = newton.equilibrio(fuerzas_equilibrio)
        >>> print(f"¿En equilibrio?: {en_equilibrio}")
        ¿En equilibrio?: True
        """
        fuerza_neta = self.fuerza_neta(fuerzas)

        if isinstance(fuerza_neta.magnitude, np.ndarray):
            magnitud_neta = np.linalg.norm(fuerza_neta.magnitude)
        else:
            magnitud_neta = abs(fuerza_neta.magnitude)

        return magnitud_neta < tolerancia

    def aceleracion_desde_fuerzas(
        self,
        masa: Union[float, Q_],
        fuerzas: List[Union[float, Q_, np.ndarray]]
    ) -> Union[Q_, np.ndarray]:
        """
        Calcula la aceleración resultante de múltiples fuerzas aplicadas.

        Parameters
        ----------
        masa : float or pint.Quantity
            Masa del objeto en kg.
        fuerzas : list of float, pint.Quantity, or numpy.ndarray
            Lista de fuerzas aplicadas al objeto.

        Returns
        -------
        pint.Quantity or numpy.ndarray
            Aceleración resultante con unidades apropiadas.

        Examples
        --------
        >>> newton = LeyesNewton()
        >>> fuerzas = [20, -5, 10]
        >>> a = newton.aceleracion_desde_fuerzas(masa=5, fuerzas=fuerzas)
        >>> print(f"Aceleración: {a}")
        Aceleración: 5.0 meter / second ** 2
        """
        fuerza_neta = self.fuerza_neta(fuerzas)
        return self.segunda_ley(masa=masa, fuerza=fuerza_neta)

    def peso(self, masa: Union[float, Q_], gravedad: Union[float, Q_] = 9.81) -> Q_:
        """
        Calcula el peso de un objeto bajo la influencia gravitacional.

        Parameters
        ----------
        masa : float or pint.Quantity
            Masa del objeto en kg.
        gravedad : float or pint.Quantity, optional
            Aceleración gravitacional en m/s². Default 9.81 m/s² (Tierra).

        Returns
        -------
        pint.Quantity
            Peso del objeto en N.

        Examples
        --------
        >>> newton = LeyesNewton()
        >>> W = newton.peso(masa=10)
        >>> print(f"Peso: {W}")
        Peso: 98.1 newton

        >>> # En la Luna (g ≈ 1.62 m/s²)
        >>> W_luna = newton.peso(masa=10, gravedad=1.62)
        >>> print(f"Peso en la Luna: {W_luna}")
        Peso en la Luna: 16.2 newton
        """
        if not isinstance(masa, Q_):
            masa = Q_(masa, ureg.kilogram)
        if not isinstance(gravedad, Q_):
            gravedad = Q_(gravedad, ureg.meter / ureg.second**2)

        return masa * gravedad

    def fuerza_centripeta(
        self,
        masa: Union[float, Q_],
        velocidad: Union[float, Q_],
        radio: Union[float, Q_]
    ) -> Q_:
        """
        Calcula la fuerza centrípeta necesaria para movimiento circular.

        Parameters
        ----------
        masa : float or pint.Quantity
            Masa del objeto en kg.
        velocidad : float or pint.Quantity
            Velocidad tangencial en m/s.
        radio : float or pint.Quantity
            Radio de la trayectoria circular en m.

        Returns
        -------
        pint.Quantity
            Fuerza centrípeta en N.

        Examples
        --------
        >>> newton = LeyesNewton()
        >>> F_c = newton.fuerza_centripeta(masa=2, velocidad=10, radio=5)
        >>> print(f"Fuerza centrípeta: {F_c}")
        Fuerza centrípeta: 40.0 newton

        Notes
        -----
        La fuerza centrípeta se calcula como: F_c = mv²/r
        Esta fuerza siempre apunta hacia el centro de la trayectoria circular.
        """
        if not isinstance(masa, Q_):
            masa = Q_(masa, ureg.kilogram)
        if not isinstance(velocidad, Q_):
            velocidad = Q_(velocidad, ureg.meter / ureg.second)
        if not isinstance(radio, Q_):
            radio = Q_(radio, ureg.meter)

        if radio.magnitude <= 0:
            raise ValueError("El radio debe ser un valor positivo")

        return masa * velocidad**2 / radio
