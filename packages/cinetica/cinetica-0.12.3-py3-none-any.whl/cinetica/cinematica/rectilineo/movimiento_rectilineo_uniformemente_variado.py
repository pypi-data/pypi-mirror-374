import math
from typing import Union, Optional
from ..base_movimiento import Movimiento
from ...units import ureg, Q_

class MovimientoRectilineoUniformementeVariado(Movimiento):
    """
    Clase para calcular posición, velocidad y aceleración en Movimiento Rectilíneo Uniformemente Variado (MRUV).
    """

    def __init__(self, posicion_inicial: Union[float, Q_] = 0.0 * ureg.meter, velocidad_inicial: Union[float, Q_] = 0.0 * ureg.meter / ureg.second, aceleracion_inicial: Union[float, Q_] = 0.0 * ureg.meter / ureg.second**2) -> None:
        """
        Inicializa el objeto MovimientoRectilineoUniformementeVariado con condiciones iniciales.

        Args:
            posicion_inicial (Q_): Posición inicial del objeto (m).
            velocidad_inicial (Q_): Velocidad inicial del objeto (m/s).
            aceleracion_inicial (Q_): Aceleración inicial del objeto (m/s^2).
        """
        if not isinstance(posicion_inicial, Q_):
            posicion_inicial = Q_(posicion_inicial, ureg.meter)
        if not isinstance(velocidad_inicial, Q_):
            velocidad_inicial = Q_(velocidad_inicial, ureg.meter / ureg.second)
        if not isinstance(aceleracion_inicial, Q_):
            aceleracion_inicial = Q_(aceleracion_inicial, ureg.meter / ureg.second**2)

        self.posicion_inicial = posicion_inicial
        self.velocidad_inicial = velocidad_inicial
        self.aceleracion_inicial = aceleracion_inicial

    def posicion(self, tiempo: Union[float, Q_]) -> Q_:
        """
        Calcula la posición en MRUV.
        Ecuación: x = x0 + v0 * t + 0.5 * a * t^2

        Args:
            tiempo (Q_): Tiempo transcurrido (s).

        Returns:
            Q_: Posición final (m).
        
        Raises:
            ValueError: Si el tiempo es negativo.
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        if tiempo.magnitude < 0:
            raise ValueError("El tiempo no puede ser negativo.")
        return self.posicion_inicial + self.velocidad_inicial * tiempo + 0.5 * self.aceleracion_inicial * (tiempo ** 2)

    def velocidad(self, tiempo: Union[float, Q_]) -> Q_:
        """
        Calcula la velocidad en MRUV.
        Ecuación: v = v0 + a * t

        Args:
            tiempo (Q_): Tiempo transcurrido (s).

        Returns:
            Q_: Velocidad final (m/s).
        
        Raises:
            ValueError: Si el tiempo es negativo.
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        if tiempo.magnitude < 0:
            raise ValueError("El tiempo no puede ser negativo.")
        return self.velocidad_inicial + self.aceleracion_inicial * tiempo

    def velocidad_sin_tiempo(self, posicion_final: Union[float, Q_]) -> Q_:
        """
        Calcula la velocidad usando la ecuación v^2 = v0^2 + 2*a*Δx.
        Esta ecuación es útil cuando no se conoce el tiempo.

        Args:
            posicion_final (Q_): Posición final (m).

        Returns:
            Q_: Velocidad (m/s).
        """
        if not isinstance(posicion_final, Q_):
            posicion_final = Q_(posicion_final, ureg.meter)
        
        delta_x = posicion_final - self.posicion_inicial
        v_squared = self.velocidad_inicial**2 + 2 * self.aceleracion_inicial * delta_x
        
        if v_squared.magnitude < 0:
            raise ValueError("No se puede calcular la velocidad real para esta posición (velocidad al cuadrado negativa).")
        
        # Determine the sign of the velocity
        # This is a simplification, a more robust solution might involve checking the direction of motion
        # or considering the context of the problem.
        # For now, we'll assume the sign is determined by the initial velocity and acceleration over a small time step.
        test_time = 1 * ureg.second # Use a small positive time to check direction
        test_velocity = self.velocidad_inicial + self.aceleracion_inicial * test_time
        
        return Q_(math.sqrt(v_squared.magnitude), ureg.meter / ureg.second) * (1 if test_velocity.magnitude >= 0 else -1)

    def tiempo_por_posicion(self, posicion_final: Union[float, Q_]) -> list[Q_]:
        """
        Calcula el tiempo necesario para alcanzar una posición final específica.
        Ecuación: x = x0 + v0 * t + 0.5 * a * t^2
        Resuelve para t: 0.5 * a * t^2 + v0 * t + (x0 - x) = 0

        Args:
            posicion_final (Q_): Posición final deseada (m).

        Returns:
            list[Q_]: Lista de tiempos posibles (s). Puede tener 0, 1 o 2 soluciones.
        
        Raises:
            ValueError: Si no hay soluciones reales.
        """
        if not isinstance(posicion_final, Q_):
            posicion_final = Q_(posicion_final, ureg.meter)
        
        # Coeficientes de la ecuación cuadrática: at² + bt + c = 0
        a = 0.5 * self.aceleracion_inicial
        b = self.velocidad_inicial
        c = self.posicion_inicial - posicion_final
        
        # Si a = 0, es una ecuación lineal
        if abs(a.magnitude) < 1e-10:
            if abs(b.magnitude) < 1e-10:
                if abs(c.magnitude) < 1e-10:
                    # Cualquier tiempo es válido (posición constante)
                    return [Q_(0, ureg.second)]
                else:
                    # No hay solución
                    raise ValueError("No se puede alcanzar la posición final con velocidad y aceleración cero.")
            else:
                # Ecuación lineal: bt + c = 0 → t = -c/b
                t = -c / b
                if t.magnitude >= 0:
                    return [t]
                else:
                    raise ValueError("El tiempo calculado es negativo.")
        
        # Ecuación cuadrática
        discriminante = b**2 - 4 * a * c
        
        if discriminante.magnitude < 0:
            raise ValueError("No hay soluciones reales para alcanzar la posición final.")
        
        sqrt_discriminante = Q_(math.sqrt(discriminante.magnitude), discriminante.units**0.5)
        
        t1 = (-b + sqrt_discriminante) / (2 * a)
        t2 = (-b - sqrt_discriminante) / (2 * a)
        
        # Filtrar tiempos negativos
        tiempos = []
        if t1.magnitude >= 0:
            tiempos.append(t1)
        if t2.magnitude >= 0 and abs(t2.magnitude - t1.magnitude) > 1e-10:
            tiempos.append(t2)
        
        if not tiempos:
            raise ValueError("Todos los tiempos calculados son negativos.")
        
        return sorted(tiempos, key=lambda t: t.magnitude)

    def aceleracion(self, tiempo: Optional[Union[float, Q_]] = None) -> Q_:
        """
        Calcula la aceleración en MRUV (es constante).
        Ecuación: a = a0

        Args:
            tiempo (Q_, optional): Tiempo transcurrido (s). No afecta al resultado.

        Returns:
            Q_: Aceleración (m/s^2).
        """
        return self.aceleracion_inicial
