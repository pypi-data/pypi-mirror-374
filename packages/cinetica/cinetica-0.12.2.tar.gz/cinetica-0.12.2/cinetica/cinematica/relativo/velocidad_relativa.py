from typing import Union, Optional
import numpy as np
from ...units import ureg, Q_

class MovimientoRelativo:
    """
    Clase para calcular velocidades relativas entre objetos.
    Permite trabajar con vectores de velocidad en 2D o 3D.
    """

    def __init__(self) -> None:
        """
        Inicializa la clase MovimientoRelativo.
        No requiere parámetros iniciales ya que los vectores de velocidad
        se pasan directamente a los métodos de cálculo.
        """
        pass

    def velocidad_relativa(self, velocidad_objeto_a: Union[np.ndarray, Q_], velocidad_objeto_b: Union[np.ndarray, Q_]) -> Q_:
        """
        Calcula la velocidad del objeto A con respecto al objeto B (V_A/B).
        V_A/B = V_A - V_B

        :param velocidad_objeto_a: Vector de velocidad del objeto A (Q_ con unidades de velocidad).
        :param velocidad_objeto_b: Vector de velocidad del objeto B (Q_ con unidades de velocidad).
        :return: Vector de velocidad relativa de A con respecto a B (Q_ con unidades de velocidad).
        :raises ValueError: Si los vectores de velocidad no tienen la misma dimensión o unidades incompatibles.
        """
        if not isinstance(velocidad_objeto_a, Q_):
            velocidad_objeto_a = Q_(velocidad_objeto_a, ureg.meter / ureg.second)
        if not isinstance(velocidad_objeto_b, Q_):
            velocidad_objeto_b = Q_(velocidad_objeto_b, ureg.meter / ureg.second)

        if velocidad_objeto_a.units != velocidad_objeto_b.units:
            raise ValueError("Las unidades de los vectores de velocidad deben ser compatibles.")

        return velocidad_objeto_a - velocidad_objeto_b

    def velocidad_absoluta_a(self, velocidad_relativa_ab: Union[np.ndarray, Q_], velocidad_objeto_b: Union[np.ndarray, Q_]) -> Q_:
        """
        Calcula la velocidad absoluta del objeto A (V_A) dado V_A/B y V_B.
        V_A = V_A/B + V_B

        :param velocidad_relativa_ab: Vector de velocidad de A con respecto a B (Q_ con unidades de velocidad).
        :param velocidad_objeto_b: Vector de velocidad del objeto B (Q_ con unidades de velocidad).
        :return: Vector de velocidad absoluta del objeto A (Q_ con unidades de velocidad).
        :raises ValueError: Si los vectores de velocidad no tienen la misma dimensión o unidades incompatibles.
        """
        if not isinstance(velocidad_relativa_ab, Q_):
            velocidad_relativa_ab = Q_(velocidad_relativa_ab, ureg.meter / ureg.second)
        if not isinstance(velocidad_objeto_b, Q_):
            velocidad_objeto_b = Q_(velocidad_objeto_b, ureg.meter / ureg.second)

        if velocidad_relativa_ab.units != velocidad_objeto_b.units:
            raise ValueError("Las unidades de los vectores de velocidad deben ser compatibles.")

        return velocidad_relativa_ab + velocidad_objeto_b

    def velocidad_absoluta_b(self, velocidad_objeto_a: Union[np.ndarray, Q_], velocidad_relativa_ab: Union[np.ndarray, Q_]) -> Q_:
        """
        Calcula la velocidad absoluta del objeto B (V_B) dado V_A y V_A/B.
        V_B = V_A - V_A/B

        :param velocidad_objeto_a: Vector de velocidad del objeto A (Q_ con unidades de velocidad).
        :param velocidad_relativa_ab: Vector de velocidad de A con respecto a B (Q_ con unidades de velocidad).
        :return: Vector de velocidad absoluta del objeto B (Q_ con unidades de velocidad).
        :raises ValueError: Si los vectores de velocidad no tienen la misma dimensión o unidades incompatibles.
        """
        if not isinstance(velocidad_objeto_a, Q_):
            velocidad_objeto_a = Q_(velocidad_objeto_a, ureg.meter / ureg.second)
        if not isinstance(velocidad_relativa_ab, Q_):
            velocidad_relativa_ab = Q_(velocidad_relativa_ab, ureg.meter / ureg.second)

        if velocidad_objeto_a.units != velocidad_relativa_ab.units:
            raise ValueError("Las unidades de los vectores de velocidad deben ser compatibles.")

        return velocidad_objeto_a - velocidad_relativa_ab

    def magnitud_velocidad(self, velocidad_vector: Union[np.ndarray, Q_]) -> Q_:
        """
        Calcula la magnitud de un vector de velocidad.

        :param velocidad_vector: Vector de velocidad (Q_ con unidades de velocidad).
        :return: Magnitud del vector de velocidad (Q_ con unidades de velocidad).
        """
        if not isinstance(velocidad_vector, Q_):
            velocidad_vector = Q_(velocidad_vector, ureg.meter / ureg.second)
        
        # Assuming velocidad_vector is a Quantity whose magnitude is a numpy array or list
        magnitude = np.linalg.norm(velocidad_vector.magnitude)
        return Q_(magnitude, velocidad_vector.units)

    def direccion_velocidad(self, velocidad_vector: Union[np.ndarray, Q_]) -> Union[Q_, np.ndarray]:
        """
        Calcula la dirección de un vector de velocidad en 2D (ángulo en radianes).
        Para 3D, devuelve el vector unitario.

        :param velocidad_vector: Vector de velocidad (Q_ con unidades de velocidad).
        :return: Ángulo en radianes (Q_) para 2D, o vector unitario (np.ndarray) para 3D.
        :raises ValueError: Si el vector es de dimensión 0.
        """
        if not isinstance(velocidad_vector, Q_):
            velocidad_vector = Q_(velocidad_vector, ureg.meter / ureg.second)

        v_magnitude = velocidad_vector.magnitude
        norm = np.linalg.norm(v_magnitude)

        if norm == 0:
            if len(v_magnitude) == 2:
                return 0.0 * ureg.radian
            else:
                return np.zeros_like(v_magnitude)

        if len(v_magnitude) == 2:
            return Q_(np.arctan2(v_magnitude[1], v_magnitude[0]), ureg.radian)
        else:
            return v_magnitude / norm
