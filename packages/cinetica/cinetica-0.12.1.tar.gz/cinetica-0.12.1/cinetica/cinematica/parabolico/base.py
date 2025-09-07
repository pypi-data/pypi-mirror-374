import math
from ..base_movimiento import Movimiento
from ...units import ureg, Q_

class MovimientoParabolicoBase(Movimiento):
    """
    Clase base para simular trayectorias en Movimiento Parabólico.
    Se asume que el lanzamiento se realiza desde el origen (0,0) y la gravedad actúa hacia abajo.
    """

    def __init__(self, velocidad_inicial: Q_, angulo_grados: Q_, gravedad: Q_ = 9.81 * ureg.meter / ureg.second**2):
        """
        Inicializa el objeto MovimientoParabolicoBase con las condiciones iniciales.

        Args:
            velocidad_inicial (Q_): Magnitud de la velocidad inicial (m/s).
            angulo_grados (Q_): Ángulo de lanzamiento con respecto a la horizontal (grados).
            gravedad (Q_): Aceleración debido a la gravedad (m/s^2).
        
        Raises:
            ValueError: Si la velocidad inicial es negativa, el ángulo no está entre 0 y 90 grados, o la gravedad es menor o igual a cero.
        """
        if not isinstance(velocidad_inicial, Q_):
            velocidad_inicial = Q_(velocidad_inicial, ureg.meter / ureg.second)
        if not isinstance(angulo_grados, Q_):
            angulo_grados = Q_(angulo_grados, ureg.degree)
        if not isinstance(gravedad, Q_):
            gravedad = Q_(gravedad, ureg.meter / ureg.second**2)

        if velocidad_inicial.magnitude < 0:
            raise ValueError("La velocidad inicial no puede ser negativa.")
        if not (0 <= angulo_grados.magnitude <= 90):
            raise ValueError("El ángulo de lanzamiento debe estar entre 0 y 90 grados.")
        if gravedad.magnitude <= 0:
            raise ValueError("La gravedad debe ser un valor positivo.")

        self.velocidad_inicial = velocidad_inicial
        self.angulo_radianes = angulo_grados.to(ureg.radian)
        self.gravedad = gravedad

        self.velocidad_inicial_x = self.velocidad_inicial * math.cos(self.angulo_radianes.magnitude)
        self.velocidad_inicial_y = self.velocidad_inicial * math.sin(self.angulo_radianes.magnitude)

    def posicion(self, tiempo: Q_) -> tuple[Q_, Q_]:
        """
        Calcula la posición (x, y) del proyectil en un tiempo dado.

        Args:
            tiempo (Q_): Tiempo transcurrido (s).

        Returns:
            tuple: Una tupla (x, y) con las coordenadas de la posición (m).
        
        Raises:
            ValueError: Si el tiempo es negativo.
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        if tiempo.magnitude < 0:
            raise ValueError("El tiempo no puede ser negativo.")

        posicion_x = self.velocidad_inicial_x * tiempo
        posicion_y = (self.velocidad_inicial_y * tiempo) - (0.5 * self.gravedad * (tiempo ** 2))
        return (posicion_x, posicion_y)

    def velocidad(self, tiempo: Q_) -> tuple[Q_, Q_]:
        """
        Calcula la velocidad (vx, vy) del proyectil en un tiempo dado.

        Args:
            tiempo (Q_): Tiempo transcurrido (s).

        Returns:
            tuple: Una tupla (vx, vy) con las componentes de la velocidad (m/s).
        
        Raises:
            ValueError: Si el tiempo es negativo.
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        if tiempo.magnitude < 0:
            raise ValueError("El tiempo no puede ser negativo.")

        velocidad_x = self.velocidad_inicial_x
        velocidad_y = self.velocidad_inicial_y - (self.gravedad * tiempo)
        return (velocidad_x, velocidad_y)

    def aceleracion(self, tiempo: Q_ = None) -> tuple[Q_, Q_]:
        """
        Calcula la aceleración (ax, ay) del proyectil en un tiempo dado.

        Args:
            tiempo (Q_): Tiempo transcurrido (s).

        Returns:
            tuple: Una tupla (ax, ay) con las componentes de la aceleración (m/s^2).
        """
        # La aceleración en X es 0, y en Y es -gravedad
        return (0.0 * ureg.meter / ureg.second**2, -self.gravedad)
