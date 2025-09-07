import math
from typing import Union, Optional
from ..base_movimiento import Movimiento
from ...units import ureg, Q_


class MovimientoRectilineoUniformementeVariado(Movimiento):
    """
    Movimiento Rectilíneo Uniformemente Variado (MRUV).

    Implementa los cálculos para un objeto que se mueve en línea recta
    con aceleración constante. En este tipo de movimiento, la velocidad
    cambia uniformemente con el tiempo y la posición varía cuadráticamente.

    Parameters
    ----------
    posicion_inicial : float or pint.Quantity, optional
        Posición inicial del objeto en metros. Default es 0.0 m.
    velocidad_inicial : float or pint.Quantity, optional
        Velocidad inicial del objeto en m/s. Default es 0.0 m/s.
    aceleracion_inicial : float or pint.Quantity, optional
        Aceleración constante del objeto en m/s². Default es 0.0 m/s².

    Attributes
    ----------
    posicion_inicial : pint.Quantity
        Posición inicial del objeto con unidades de longitud.
    velocidad_inicial : pint.Quantity
        Velocidad inicial del objeto con unidades de velocidad.
    aceleracion_inicial : pint.Quantity
        Aceleración constante del objeto con unidades de aceleración.

    Examples
    --------
    >>> from cinetica.cinematica.rectilineo import MovimientoRectilineoUniformementeVariado
    >>> mruv = MovimientoRectilineoUniformementeVariado(
    ...     posicion_inicial=0, velocidad_inicial=10, aceleracion_inicial=2
    ... )
    >>> posicion_final = mruv.posicion(tiempo=5)
    >>> print(f"Posición a los 5s: {posicion_final}")
    Posición a los 5s: 75.0 meter

    Notes
    -----
    Las ecuaciones fundamentales del MRUV son:
    - Posición: x(t) = x₀ + v₀·t + ½·a·t²
    - Velocidad: v(t) = v₀ + a·t
    - Aceleración: a(t) = a₀ (constante)
    - Velocidad sin tiempo: v² = v₀² + 2·a·Δx
    """

    def __init__(
        self,
        posicion_inicial: Union[float, Q_] = 0.0 * ureg.meter,
        velocidad_inicial: Union[float, Q_] = 0.0 * ureg.meter / ureg.second,
        aceleracion_inicial: Union[float, Q_] = 0.0 * ureg.meter / ureg.second**2,
    ) -> None:
        """
        Inicializa una instancia de Movimiento Rectilíneo Uniformemente Variado.

        Parameters
        ----------
        posicion_inicial : float or pint.Quantity, optional
            Posición inicial del objeto en metros. Si se proporciona un float,
            se asume que está en metros. Default es 0.0 m.
        velocidad_inicial : float or pint.Quantity, optional
            Velocidad inicial del objeto en m/s. Si se proporciona un float,
            se asume que está en m/s. Default es 0.0 m/s.
        aceleracion_inicial : float or pint.Quantity, optional
            Aceleración constante del objeto en m/s². Si se proporciona un float,
            se asume que está en m/s². Default es 0.0 m/s².

        Examples
        --------
        >>> mruv = MovimientoRectilineoUniformementeVariado()
        >>> mruv = MovimientoRectilineoUniformementeVariado(
        ...     posicion_inicial=10, velocidad_inicial=5, aceleracion_inicial=2
        ... )
        >>> from cinetica.units import ureg
        >>> mruv = MovimientoRectilineoUniformementeVariado(
        ...     posicion_inicial=10 * ureg.meter,
        ...     velocidad_inicial=5 * ureg.meter / ureg.second,
        ...     aceleracion_inicial=2 * ureg.meter / ureg.second**2
        ... )
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
        Calcula la posición del objeto en un tiempo dado.

        Utiliza la ecuación fundamental del MRUV: x(t) = x₀ + v₀·t + ½·a·t²

        Parameters
        ----------
        tiempo : float or pint.Quantity
            Tiempo transcurrido desde el inicio del movimiento, en segundos.
            Si se proporciona un float, se asume que está en segundos.
            Debe ser un valor no negativo.

        Returns
        -------
        pint.Quantity
            Posición del objeto en el tiempo especificado, con unidades de longitud.

        Raises
        ------
        ValueError
            Si el tiempo proporcionado es negativo.

        Examples
        --------
        >>> mruv = MovimientoRectilineoUniformementeVariado(
        ...     posicion_inicial=0, velocidad_inicial=10, aceleracion_inicial=2
        ... )
        >>> pos = mruv.posicion(tiempo=5)
        >>> print(f"Posición: {pos}")
        Posición: 75.0 meter
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        if tiempo.magnitude < 0:
            raise ValueError("El tiempo no puede ser negativo.")
        return (
            self.posicion_inicial
            + self.velocidad_inicial * tiempo
            + 0.5 * self.aceleracion_inicial * (tiempo**2)
        )

    def velocidad(self, tiempo: Union[float, Q_]) -> Q_:
        """
        Calcula la velocidad del objeto en un tiempo dado.

        Utiliza la ecuación fundamental del MRUV: v(t) = v₀ + a·t

        Parameters
        ----------
        tiempo : float or pint.Quantity
            Tiempo transcurrido desde el inicio del movimiento, en segundos.
            Si se proporciona un float, se asume que está en segundos.
            Debe ser un valor no negativo.

        Returns
        -------
        pint.Quantity
            Velocidad del objeto en el tiempo especificado, con unidades de velocidad.

        Raises
        ------
        ValueError
            Si el tiempo proporcionado es negativo.

        Examples
        --------
        >>> mruv = MovimientoRectilineoUniformementeVariado(
        ...     velocidad_inicial=10, aceleracion_inicial=2
        ... )
        >>> vel = mruv.velocidad(tiempo=5)
        >>> print(f"Velocidad: {vel}")
        Velocidad: 20.0 meter / second
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        if tiempo.magnitude < 0:
            raise ValueError("El tiempo no puede ser negativo.")
        return self.velocidad_inicial + self.aceleracion_inicial * tiempo

    def velocidad_sin_tiempo(self, posicion_final: Union[float, Q_]) -> Q_:
        """
        Calcula la velocidad final sin conocer el tiempo.

        Utiliza la ecuación cinemática: v² = v₀² + 2·a·Δx
        donde Δx = x_final - x_inicial

        Parameters
        ----------
        posicion_final : float or pint.Quantity
            Posición final deseada en metros. Si se proporciona un float,
            se asume que está en metros.

        Returns
        -------
        pint.Quantity
            Velocidad final necesaria para alcanzar la posición especificada,
            con unidades de velocidad.

        Raises
        ------
        ValueError
            Si el discriminante es negativo (velocidad resultante sería imaginaria),
            lo que indica que la posición final no es alcanzable con los parámetros dados.

        Examples
        --------
        >>> mruv = MovimientoRectilineoUniformementeVariado(
        ...     posicion_inicial=0, velocidad_inicial=0, aceleracion_inicial=2
        ... )
        >>> vel_final = mruv.velocidad_sin_tiempo(posicion_final=50)
        >>> print(f"Velocidad final: {vel_final}")
        Velocidad final: 14.142135623730951 meter / second
        """
        if not isinstance(posicion_final, Q_):
            posicion_final = Q_(posicion_final, ureg.meter)

        delta_x = posicion_final - self.posicion_inicial
        v_squared = self.velocidad_inicial**2 + 2 * self.aceleracion_inicial * delta_x

        if v_squared.magnitude < 0:
            raise ValueError(
                "No se puede calcular la velocidad real para esta posición (velocidad al cuadrado negativa)."
            )

        # Determine the sign of the velocity
        # This is a simplification, a more robust solution might involve checking the direction of motion
        # or considering the context of the problem.
        # For now, we'll assume the sign is determined by the initial velocity and acceleration over a small time step.
        test_time = 1 * ureg.second  # Use a small positive time to check direction
        test_velocity = self.velocidad_inicial + self.aceleracion_inicial * test_time

        return Q_(math.sqrt(v_squared.magnitude), ureg.meter / ureg.second) * (
            1 if test_velocity.magnitude >= 0 else -1
        )

    def tiempo_por_posicion(self, posicion_final: Union[float, Q_]) -> list[Q_]:
        """
        Calcula el tiempo necesario para alcanzar una posición específica.

        Resuelve la ecuación cuadrática derivada de x(t) = x₀ + v₀·t + ½·a·t²
        reorganizada como: ½·a·t² + v₀·t + (x₀ - x_final) = 0

        Parameters
        ----------
        posicion_final : float or pint.Quantity
            Posición objetivo que se desea alcanzar, en metros.
            Si se proporciona un float, se asume que está en metros.

        Returns
        -------
        list of pint.Quantity
            Lista de tiempos válidos (no negativos) en segundos para alcanzar
            la posición objetivo. Puede contener 0, 1 o 2 soluciones dependiendo
            de los parámetros físicos del movimiento.

        Raises
        ------
        ValueError
            Si no existen soluciones reales (discriminante negativo), lo que
            indica que la posición objetivo no es alcanzable con los parámetros dados.

        Examples
        --------
        >>> mruv = MovimientoRectilineoUniformementeVariado(
        ...     posicion_inicial=0, velocidad_inicial=0, aceleracion_inicial=2
        ... )
        >>> tiempos = mruv.tiempo_por_posicion(16)
        >>> print(f"Tiempos: {tiempos}")
        Tiempos: [4.0 second]

        >>> mruv2 = MovimientoRectilineoUniformementeVariado(
        ...     posicion_inicial=0, velocidad_inicial=10, aceleracion_inicial=-2
        ... )
        >>> tiempos2 = mruv2.tiempo_por_posicion(12)
        >>> print(f"Tiempos: {tiempos2}")
        Tiempos: [1.27 second, 3.73 second]

        Notes
        -----
        Para movimientos con aceleración cero (MRU), la ecuación se reduce a lineal.
        En casos con aceleración no nula, pueden existir dos soluciones válidas
        correspondientes a los momentos de "ida" y "vuelta" por la posición objetivo.
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
                    raise ValueError(
                        "No se puede alcanzar la posición final con velocidad y aceleración cero."
                    )
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
            raise ValueError(
                "No hay soluciones reales para alcanzar la posición final."
            )

        sqrt_discriminante = Q_(
            math.sqrt(discriminante.magnitude), discriminante.units**0.5
        )

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
        Obtiene la aceleración del objeto en cualquier momento.

        En el MRUV, la aceleración es constante e independiente del tiempo.

        Parameters
        ----------
        tiempo : float, pint.Quantity, or None, optional
            Tiempo transcurrido en segundos. Este parámetro no afecta el resultado
            ya que la aceleración es constante en MRUV. Default es None.

        Returns
        -------
        pint.Quantity
            Aceleración constante del objeto, con unidades de aceleración.

        Examples
        --------
        >>> mruv = MovimientoRectilineoUniformementeVariado(aceleracion_inicial=2)
        >>> acel = mruv.aceleracion()
        >>> print(f"Aceleración: {acel}")
        Aceleración: 2.0 meter / second ** 2
        """
        return self.aceleracion_inicial
