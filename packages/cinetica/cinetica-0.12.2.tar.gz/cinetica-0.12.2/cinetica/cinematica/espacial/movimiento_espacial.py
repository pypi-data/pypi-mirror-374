from typing import Union, Optional
import numpy as np
from ..base_movimiento import Movimiento
from ...units import ureg, Q_

class MovimientoEspacial(Movimiento):
    """
    Clase para simular y calcular la trayectoria de un objeto en 3D
    utilizando vectores de posición, velocidad y aceleración.
    """

    def __init__(self,
                 posicion_inicial: Union[np.ndarray, Q_] = Q_(np.array([0.0, 0.0, 0.0]), ureg.meter),
                 velocidad_inicial: Union[np.ndarray, Q_] = Q_(np.array([0.0, 0.0, 0.0]), ureg.meter / ureg.second),
                 aceleracion_constante: Union[np.ndarray, Q_] = Q_(np.array([0.0, 0.0, 0.0]), ureg.meter / ureg.second**2)) -> None:
        """
        Inicializa el objeto MovimientoEspacial con vectores de condiciones iniciales.

        Args:
            posicion_inicial (Q_): Vector de posición inicial (m).
            velocidad_inicial (Q_): Vector de velocidad inicial (m/s).
            aceleracion_constante (Q_): Vector de aceleración constante (m/s^2).
        
        Raises:
            ValueError: Si los vectores no son de 3 dimensiones o unidades incompatibles.
        """
        if not isinstance(posicion_inicial, Q_):
            posicion_inicial = Q_(np.array(posicion_inicial), ureg.meter)
        if not isinstance(velocidad_inicial, Q_):
            velocidad_inicial = Q_(np.array(velocidad_inicial), ureg.meter / ureg.second)
        if not isinstance(aceleracion_constante, Q_):
            aceleracion_constante = Q_(np.array(aceleracion_constante), ureg.meter / ureg.second**2)

        if not (len(posicion_inicial.magnitude) == 3 and len(velocidad_inicial.magnitude) == 3 and len(aceleracion_constante.magnitude) == 3):
            raise ValueError("Todos los vectores (posición, velocidad, aceleración) deben ser de 3 dimensiones.")

        self.posicion_inicial = posicion_inicial
        self.velocidad_inicial = velocidad_inicial
        self.aceleracion_constante = aceleracion_constante

    def graficar(self, t_max: Union[float, Q_] = 10.0 * ureg.second, num_points: int = 100) -> None:
        """
        Grafica la trayectoria del movimiento en 3D.

        Args:
            t_max (Q_): Tiempo máximo a graficar (s).
            num_points (int): Número de puntos a graficar.
        """
        import matplotlib.pyplot as plt

        if not isinstance(t_max, Q_):
            t_max = Q_(t_max, ureg.second)

        t = np.linspace(0, t_max.magnitude, num_points) * ureg.second
        posiciones = np.array([self.posicion(ti).magnitude for ti in t])

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.plot(posiciones[:, 0], posiciones[:, 1], posiciones[:, 2])
        ax.set_xlabel(f'X ({self.posicion_inicial.units:~P})')
        ax.set_ylabel(f'Y ({self.posicion_inicial.units:~P})')
        ax.set_zlabel(f'Z ({self.posicion_inicial.units:~P})')
        ax.set_title('Trayectoria en 3D')
        plt.show()

    def posicion(self, tiempo: Union[float, Q_]) -> Q_:
        """
        Calcula el vector de posición en un tiempo dado.
        Ecuación: r = r0 + v0 * t + 0.5 * a * t^2

        Args:
            tiempo (Q_): Tiempo transcurrido (s).

        Returns:
            Q_: Vector de posición (m).
        
        Raises:
            ValueError: Si el tiempo es negativo.
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        if tiempo.magnitude < 0:
            raise ValueError("El tiempo no puede ser negativo.")
        return self.posicion_inicial + self.velocidad_inicial * tiempo + 0.5 * self.aceleracion_constante * (tiempo ** 2)

    def velocidad(self, tiempo: Union[float, Q_]) -> Q_:
        """
        Calcula el vector de velocidad en un tiempo dado.
        Ecuación: v = v0 + a * t

        Args:
            tiempo (Q_): Tiempo transcurrido (s).

        Returns:
            Q_: Vector de velocidad (m/s).
        
        Raises:
            ValueError: Si el tiempo es negativo.
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        if tiempo.magnitude < 0:
            raise ValueError("El tiempo no puede ser negativo.")
        return self.velocidad_inicial + self.aceleracion_constante * tiempo

    def aceleracion(self, tiempo: Optional[Union[float, Q_]] = None) -> Q_:
        """
        Retorna el vector de aceleración (es constante).
        Ecuación: a = a_constante

        Args:
            tiempo (Q_, optional): Tiempo transcurrido (s). No afecta al resultado.

        Returns:
            Q_: Vector de aceleración (m/s^2).
        """
        # La aceleración es constante, no depende del tiempo
        return self.aceleracion_constante

    def magnitud_aceleracion(self) -> Q_:
        """
        Calcula la magnitud del vector aceleración.

        Returns:
            Q_: Magnitud de la aceleración (m/s²).
        """
        return Q_(np.linalg.norm(self.aceleracion_constante.magnitude), self.aceleracion_constante.units)

    def magnitud_velocidad(self, tiempo: Union[float, Q_]) -> Q_:
        """
        Calcula la magnitud de la velocidad en un tiempo dado.

        Args:
            tiempo (Q_): Tiempo transcurrido (s).

        Returns:
            Q_: Magnitud de la velocidad (m/s).
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        velocity_vector = self.velocidad(tiempo)
        return Q_(np.linalg.norm(velocity_vector.magnitude), velocity_vector.units)

    def magnitud_aceleracion_constante(self) -> Q_:
        """
        Calcula la magnitud de la aceleración constante.

        Returns:
            Q_: Magnitud de la aceleración (m/s^2).
        """
        return Q_(np.linalg.norm(self.aceleracion_constante.magnitude), self.aceleracion_constante.units)
