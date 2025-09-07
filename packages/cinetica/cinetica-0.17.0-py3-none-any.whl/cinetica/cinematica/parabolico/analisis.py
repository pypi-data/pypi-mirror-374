import math
from .base import MovimientoParabolicoBase
from ...units import ureg, Q_


class MovimientoParabolicoAnalisis:
    """
    Clase para calcular propiedades de análisis en Movimiento Parabólico.

    Esta clase proporciona métodos para calcular características importantes
    del movimiento parabólico como tiempo de vuelo, altura máxima y alcance máximo.

    Parameters
    ----------
    base_movimiento : MovimientoParabolicoBase
        Instancia de la clase base de movimiento parabólico que contiene
        los parámetros iniciales del lanzamiento.

    Attributes
    ----------
    base_movimiento : MovimientoParabolicoBase
        Referencia al objeto de movimiento parabólico base.

    Examples
    --------
    >>> mp = MovimientoParabolicoBase(velocidad_inicial=20, angulo_grados=45)
    >>> analisis = MovimientoParabolicoAnalisis(mp)
    >>> tiempo_total = analisis.tiempo_vuelo()
    >>> altura_max = analisis.altura_maxima()
    >>> alcance_max = analisis.alcance_maximo()
    """

    def __init__(self, base_movimiento: MovimientoParabolicoBase):
        """
        Inicializa una instancia de análisis de movimiento parabólico.

        Parameters
        ----------
        base_movimiento : MovimientoParabolicoBase
            Instancia de la clase base de movimiento parabólico que contiene
            los parámetros iniciales del lanzamiento (velocidad, ángulo, gravedad).

        Examples
        --------
        >>> mp = MovimientoParabolicoBase(velocidad_inicial=20, angulo_grados=45)
        >>> analisis = MovimientoParabolicoAnalisis(mp)
        """
        self.base_movimiento = base_movimiento

    def tiempo_vuelo(self) -> Q_:
        """
        Calcula el tiempo total de vuelo del proyectil.

        El tiempo de vuelo es el tiempo que tarda el proyectil en regresar
        a la altura inicial (y=0). Se calcula como t = 2·v₀ᵧ/g

        Returns
        -------
        pint.Quantity
            Tiempo total de vuelo del proyectil, con unidades de tiempo.

        Examples
        --------
        >>> mp = MovimientoParabolicoBase(velocidad_inicial=20, angulo_grados=45)
        >>> analisis = MovimientoParabolicoAnalisis(mp)
        >>> t_vuelo = analisis.tiempo_vuelo()
        >>> print(f"Tiempo de vuelo: {t_vuelo:.2f}")
        Tiempo de vuelo: 2.89 second

        Notes
        -----
        Retorna 0.0 segundos si el ángulo de lanzamiento es 0 grados
        (lanzamiento horizontal desde altura cero).
        """
        if (
            self.base_movimiento.angulo_radianes.magnitude == 0
        ):  # Si el ángulo es 0, no hay tiempo de vuelo vertical
            return 0.0 * ureg.second
        return (
            2 * self.base_movimiento.velocidad_inicial_y
        ) / self.base_movimiento.gravedad

    def altura_maxima(self) -> Q_:
        """
        Calcula la altura máxima alcanzada por el proyectil.

        La altura máxima se alcanza cuando la componente vertical de velocidad
        se hace cero. Se calcula como h_max = v₀ᵧ²/(2·g)

        Returns
        -------
        pint.Quantity
            Altura máxima alcanzada por el proyectil, con unidades de longitud.

        Examples
        --------
        >>> mp = MovimientoParabolicoBase(velocidad_inicial=20, angulo_grados=45)
        >>> analisis = MovimientoParabolicoAnalisis(mp)
        >>> h_max = analisis.altura_maxima()
        >>> print(f"Altura máxima: {h_max:.2f}")
        Altura máxima: 10.19 meter

        Notes
        -----
        Retorna 0.0 metros si el ángulo de lanzamiento es 0 grados
        (lanzamiento completamente horizontal).
        """
        if (
            self.base_movimiento.angulo_radianes.magnitude == 0
        ):  # Si el ángulo es 0, la altura máxima es 0
            return 0.0 * ureg.meter
        return (self.base_movimiento.velocidad_inicial_y**2) / (
            2 * self.base_movimiento.gravedad
        )

    def alcance_maximo(self) -> Q_:
        """
        Calcula el alcance horizontal máximo del proyectil.

        El alcance máximo es la distancia horizontal recorrida cuando el proyectil
        regresa a la altura inicial (y=0). Se calcula como R = v₀ₓ · t_vuelo

        Returns
        -------
        pint.Quantity
            Alcance horizontal máximo del proyectil, con unidades de longitud.

        Examples
        --------
        >>> mp = MovimientoParabolicoBase(velocidad_inicial=20, angulo_grados=45)
        >>> analisis = MovimientoParabolicoAnalisis(mp)
        >>> alcance = analisis.alcance_maximo()
        >>> print(f"Alcance máximo: {alcance:.2f}")
        Alcance máximo: 40.78 meter

        Notes
        -----
        El alcance máximo teórico para un ángulo dado se obtiene con ángulos
        de 45 grados (sin considerar resistencia del aire).
        """
        tiempo_total = self.tiempo_vuelo()
        return self.base_movimiento.velocidad_inicial_x * tiempo_total
