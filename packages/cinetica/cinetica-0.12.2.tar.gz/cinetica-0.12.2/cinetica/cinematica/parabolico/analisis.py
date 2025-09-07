import math
from .base import MovimientoParabolicoBase
from ...units import ureg, Q_

class MovimientoParabolicoAnalisis:
    """
    Clase para calcular propiedades de análisis en Movimiento Parabólico,
    como tiempo de vuelo, altura máxima y alcance máximo.
    """

    def __init__(self, base_movimiento: MovimientoParabolicoBase):
        """
        Inicializa el objeto MovimientoParabolicoAnalisis con una instancia de MovimientoParabolicoBase.

        Args:
            base_movimiento (MovimientoParabolicoBase): Instancia de la clase base de movimiento parabólico.
        """
        self.base_movimiento = base_movimiento

    def tiempo_vuelo(self) -> Q_:
        """
        Calcula el tiempo total de vuelo del proyectil hasta que regresa a la altura inicial (y=0).

        Returns:
            Q_: Tiempo total de vuelo (s).
        
        Notes:
            Retorna `0.0 * ureg.second` si el ángulo de lanzamiento es 0 grados.
        """
        if self.base_movimiento.angulo_radianes.magnitude == 0: # Si el ángulo es 0, no hay tiempo de vuelo vertical
            return 0.0 * ureg.second
        return (2 * self.base_movimiento.velocidad_inicial_y) / self.base_movimiento.gravedad

    def altura_maxima(self) -> Q_:
        """
        Calcula la altura máxima alcanzada por el proyectil.

        Returns:
            Q_: Altura máxima (m).
        
        Notes:
            Retorna `0.0 * ureg.meter` si el ángulo de lanzamiento es 0 grados.
        """
        if self.base_movimiento.angulo_radianes.magnitude == 0: # Si el ángulo es 0, la altura máxima es 0
            return 0.0 * ureg.meter
        return (self.base_movimiento.velocidad_inicial_y ** 2) / (2 * self.base_movimiento.gravedad)

    def alcance_maximo(self) -> Q_:
        """
        Calcula el alcance horizontal máximo del proyectil (cuando y=0).

        Returns:
            Q_: Alcance horizontal máximo (m).
        """
        tiempo_total = self.tiempo_vuelo()
        return self.base_movimiento.velocidad_inicial_x * tiempo_total
