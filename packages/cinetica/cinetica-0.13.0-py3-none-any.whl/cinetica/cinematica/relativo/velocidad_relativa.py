from typing import Union, Optional
import numpy as np
from ...units import ureg, Q_


class MovimientoRelativo:
    """
    Clase para calcular velocidades relativas entre objetos en movimiento.

    Esta clase proporciona métodos para analizar el movimiento relativo
    entre dos objetos, permitiendo calcular velocidades relativas y
    absolutas en sistemas de referencia bidimensionales o tridimensionales.

    Examples
    --------
    >>> mr = MovimientoRelativo()
    >>> v_a = [10, 5]  # velocidad del objeto A
    >>> v_b = [3, 2]   # velocidad del objeto B
    >>> v_rel = mr.velocidad_relativa(v_a, v_b)
    >>> print(f"Velocidad relativa: {v_rel}")

    Notes
    -----
    El movimiento relativo es fundamental para:
    - Análisis de colisiones
    - Navegación y sistemas de referencia móviles
    - Mecánica de fluidos (velocidad relativa de partículas)
    - Cinemática de mecanismos
    """

    def __init__(self) -> None:
        """
        Inicializa una instancia de MovimientoRelativo.

        Esta clase no requiere parámetros de inicialización ya que
        los vectores de velocidad se proporcionan directamente a
        los métodos de cálculo.

        Examples
        --------
        >>> mr = MovimientoRelativo()
        """
        pass

    def velocidad_relativa(
        self,
        velocidad_objeto_a: Union[np.ndarray, Q_],
        velocidad_objeto_b: Union[np.ndarray, Q_],
    ) -> Q_:
        """
        Calcula la velocidad del objeto A con respecto al objeto B.

        La velocidad relativa se define como la diferencia vectorial:
        V⃗_{A/B} = V⃗_A - V⃗_B

        Parameters
        ----------
        velocidad_objeto_a : numpy.ndarray or pint.Quantity
            Vector de velocidad del objeto A, en m/s.
            Si se proporciona un array, se asume que está en m/s.
        velocidad_objeto_b : numpy.ndarray or pint.Quantity
            Vector de velocidad del objeto B, en m/s.
            Si se proporciona un array, se asume que está en m/s.

        Returns
        -------
        pint.Quantity
            Vector de velocidad relativa de A con respecto a B,
            con unidades de velocidad.

        Raises
        ------
        ValueError
            Si los vectores tienen unidades incompatibles.

        Examples
        --------
        >>> mr = MovimientoRelativo()
        >>> v_a = [10, 5]  # objeto A se mueve a 10 m/s en x, 5 m/s en y
        >>> v_b = [3, 2]   # objeto B se mueve a 3 m/s en x, 2 m/s en y
        >>> v_rel = mr.velocidad_relativa(v_a, v_b)
        >>> print(f"Velocidad relativa: {v_rel}")
        Velocidad relativa: [7 3] meter / second

        Notes
        -----
        La velocidad relativa indica cómo se mueve A según un observador
        que se mueve con B. Es independiente del sistema de referencia inercial.
        """
        if not isinstance(velocidad_objeto_a, Q_):
            velocidad_objeto_a = Q_(velocidad_objeto_a, ureg.meter / ureg.second)
        if not isinstance(velocidad_objeto_b, Q_):
            velocidad_objeto_b = Q_(velocidad_objeto_b, ureg.meter / ureg.second)

        if velocidad_objeto_a.units != velocidad_objeto_b.units:
            raise ValueError(
                "Las unidades de los vectores de velocidad deben ser compatibles."
            )

        return velocidad_objeto_a - velocidad_objeto_b

    def velocidad_absoluta_a(
        self,
        velocidad_relativa_ab: Union[np.ndarray, Q_],
        velocidad_objeto_b: Union[np.ndarray, Q_],
    ) -> Q_:
        """
        Calcula la velocidad absoluta del objeto A.

        Dada la velocidad relativa de A respecto a B y la velocidad de B,
        calcula la velocidad absoluta de A:
        V⃗_A = V⃗_{A/B} + V⃗_B

        Parameters
        ----------
        velocidad_relativa_ab : numpy.ndarray or pint.Quantity
            Vector de velocidad de A con respecto a B, en m/s.
            Si se proporciona un array, se asume que está en m/s.
        velocidad_objeto_b : numpy.ndarray or pint.Quantity
            Vector de velocidad del objeto B, en m/s.
            Si se proporciona un array, se asume que está en m/s.

        Returns
        -------
        pint.Quantity
            Vector de velocidad absoluta del objeto A,
            con unidades de velocidad.

        Raises
        ------
        ValueError
            Si los vectores tienen unidades incompatibles.

        Examples
        --------
        >>> mr = MovimientoRelativo()
        >>> v_rel_ab = [7, 3]  # A se mueve a 7,3 m/s relativo a B
        >>> v_b = [3, 2]       # B se mueve a 3,2 m/s absoluto
        >>> v_a = mr.velocidad_absoluta_a(v_rel_ab, v_b)
        >>> print(f"Velocidad absoluta de A: {v_a}")
        Velocidad absoluta de A: [10 5] meter / second

        Notes
        -----
        Este método es útil cuando se conoce el movimiento relativo
        y se quiere encontrar el movimiento absoluto.
        """
        if not isinstance(velocidad_relativa_ab, Q_):
            velocidad_relativa_ab = Q_(velocidad_relativa_ab, ureg.meter / ureg.second)
        if not isinstance(velocidad_objeto_b, Q_):
            velocidad_objeto_b = Q_(velocidad_objeto_b, ureg.meter / ureg.second)

        if velocidad_relativa_ab.units != velocidad_objeto_b.units:
            raise ValueError(
                "Las unidades de los vectores de velocidad deben ser compatibles."
            )

        return velocidad_relativa_ab + velocidad_objeto_b

    def velocidad_absoluta_b(
        self,
        velocidad_objeto_a: Union[np.ndarray, Q_],
        velocidad_relativa_ab: Union[np.ndarray, Q_],
    ) -> Q_:
        """
        Calcula la velocidad absoluta del objeto B.

        Dada la velocidad absoluta de A y la velocidad relativa de A respecto a B,
        calcula la velocidad absoluta de B:
        V⃗_B = V⃗_A - V⃗_{A/B}

        Parameters
        ----------
        velocidad_objeto_a : numpy.ndarray or pint.Quantity
            Vector de velocidad del objeto A, en m/s.
            Si se proporciona un array, se asume que está en m/s.
        velocidad_relativa_ab : numpy.ndarray or pint.Quantity
            Vector de velocidad de A con respecto a B, en m/s.
            Si se proporciona un array, se asume que está en m/s.

        Returns
        -------
        pint.Quantity
            Vector de velocidad absoluta del objeto B,
            con unidades de velocidad.

        Raises
        ------
        ValueError
            Si los vectores tienen unidades incompatibles.

        Examples
        --------
        >>> mr = MovimientoRelativo()
        >>> v_a = [10, 5]      # A se mueve a 10,5 m/s absoluto
        >>> v_rel_ab = [7, 3]  # A se mueve a 7,3 m/s relativo a B
        >>> v_b = mr.velocidad_absoluta_b(v_a, v_rel_ab)
        >>> print(f"Velocidad absoluta de B: {v_b}")
        Velocidad absoluta de B: [3 2] meter / second

        Notes
        -----
        Este método es útil cuando se conocen las velocidades absolutas
        y relativas y se quiere encontrar la velocidad del sistema de referencia.
        """
        if not isinstance(velocidad_objeto_a, Q_):
            velocidad_objeto_a = Q_(velocidad_objeto_a, ureg.meter / ureg.second)
        if not isinstance(velocidad_relativa_ab, Q_):
            velocidad_relativa_ab = Q_(velocidad_relativa_ab, ureg.meter / ureg.second)

        if velocidad_objeto_a.units != velocidad_relativa_ab.units:
            raise ValueError(
                "Las unidades de los vectores de velocidad deben ser compatibles."
            )

        return velocidad_objeto_a - velocidad_relativa_ab

    def magnitud_velocidad(self, velocidad_vector: Union[np.ndarray, Q_]) -> Q_:
        """
        Calcula la magnitud (módulo) de un vector de velocidad.

        La magnitud se calcula como la norma euclidiana del vector:
        |V⃗| = √(V_x² + V_y² + V_z²)

        Parameters
        ----------
        velocidad_vector : numpy.ndarray or pint.Quantity
            Vector de velocidad, en m/s.
            Si se proporciona un array, se asume que está en m/s.

        Returns
        -------
        pint.Quantity
            Magnitud escalar del vector de velocidad,
            con unidades de velocidad.

        Examples
        --------
        >>> mr = MovimientoRelativo()
        >>> v = [3, 4]  # vector velocidad
        >>> mag = mr.magnitud_velocidad(v)
        >>> print(f"Magnitud: {mag}")
        Magnitud: 5.0 meter / second

        Notes
        -----
        La magnitud representa la rapidez del objeto,
        independientemente de su dirección.
        """
        if not isinstance(velocidad_vector, Q_):
            velocidad_vector = Q_(velocidad_vector, ureg.meter / ureg.second)

        # Assuming velocidad_vector is a Quantity whose magnitude is a numpy array or list
        magnitude = np.linalg.norm(velocidad_vector.magnitude)
        return Q_(magnitude, velocidad_vector.units)

    def direccion_velocidad(
        self, velocidad_vector: Union[np.ndarray, Q_]
    ) -> Union[Q_, np.ndarray]:
        """
        Calcula la dirección de un vector de velocidad.

        Para vectores 2D, devuelve el ángulo en radianes medido desde el eje x positivo.
        Para vectores 3D, devuelve el vector unitario normalizado.

        Parameters
        ----------
        velocidad_vector : numpy.ndarray or pint.Quantity
            Vector de velocidad, en m/s.
            Si se proporciona un array, se asume que está en m/s.

        Returns
        -------
        pint.Quantity or numpy.ndarray
            Para vectores 2D: ángulo en radianes (pint.Quantity).
            Para vectores 3D: vector unitario (numpy.ndarray).
            Para vectores nulos: 0 radianes (2D) o vector cero (3D).

        Examples
        --------
        >>> mr = MovimientoRelativo()
        >>> v_2d = [3, 3]  # vector 2D
        >>> angulo = mr.direccion_velocidad(v_2d)
        >>> print(f"Ángulo: {angulo}")
        Ángulo: 0.7854 radian  # π/4 radianes = 45°

        >>> v_3d = [1, 0, 0]  # vector 3D
        >>> unitario = mr.direccion_velocidad(v_3d)
        >>> print(f"Vector unitario: {unitario}")
        Vector unitario: [1. 0. 0.]

        Notes
        -----
        La dirección es independiente de la magnitud del vector.
        Para vectores 2D, el ángulo está en el rango [-π, π].
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
