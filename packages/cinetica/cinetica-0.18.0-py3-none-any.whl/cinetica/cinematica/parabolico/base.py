import math
from ..base_movimiento import Movimiento
from ...units import ureg, Q_


class MovimientoParabolicoBase(Movimiento):
    """
    Clase base para simular trayectorias en Movimiento Parabólico.

    Esta clase implementa las ecuaciones cinemáticas para el movimiento parabólico,
    también conocido como movimiento de proyectiles. Se asume que el lanzamiento
    se realiza desde el origen (0,0) y que la gravedad actúa verticalmente hacia abajo.

    Parameters
    ----------
    velocidad_inicial : pint.Quantity
        Magnitud de la velocidad inicial del proyectil.
    angulo_grados : pint.Quantity
        Ángulo de lanzamiento con respecto a la horizontal.
    gravedad : pint.Quantity, optional
        Aceleración debido a la gravedad. Default es 9.81 m/s².

    Attributes
    ----------
    velocidad_inicial : pint.Quantity
        Magnitud de la velocidad inicial.
    angulo_radianes : pint.Quantity
        Ángulo de lanzamiento en radianes.
    gravedad : pint.Quantity
        Aceleración gravitacional.
    velocidad_inicial_x : pint.Quantity
        Componente horizontal de la velocidad inicial.
    velocidad_inicial_y : pint.Quantity
        Componente vertical de la velocidad inicial.

    Notes
    -----
    El movimiento parabólico es la combinación de:
    - Movimiento rectilíneo uniforme en la dirección horizontal
    - Movimiento rectilíneo uniformemente variado en la dirección vertical

    Examples
    --------
    >>> mp = MovimientoParabolicoBase(
    ...     velocidad_inicial=20, angulo_grados=45
    ... )
    >>> pos_x, pos_y = mp.posicion(tiempo=1)
    >>> print(f"Posición: x={pos_x}, y={pos_y}")
    """

    def __init__(
        self,
        velocidad_inicial: Q_,
        angulo_grados: Q_,
        gravedad: Q_ = 9.81 * ureg.meter / ureg.second**2,
    ):
        """
        Inicializa una instancia de Movimiento Parabólico.

        Parameters
        ----------
        velocidad_inicial : float or pint.Quantity
            Magnitud de la velocidad inicial del proyectil, en m/s.
            Si se proporciona un float, se asume que está en m/s.
            Debe ser un valor no negativo.
        angulo_grados : float or pint.Quantity
            Ángulo de lanzamiento con respecto a la horizontal, en grados.
            Si se proporciona un float, se asume que está en grados.
            Debe estar entre 0 y 90 grados.
        gravedad : float or pint.Quantity, optional
            Aceleración debido a la gravedad, en m/s².
            Si se proporciona un float, se asume que está en m/s².
            Default es 9.81 m/s².

        Raises
        ------
        ValueError
            Si la velocidad inicial es negativa, el ángulo no está entre 0 y 90 grados,
            o la gravedad es menor o igual a cero.

        Examples
        --------
        >>> mp = MovimientoParabolicoBase(
        ...     velocidad_inicial=20, angulo_grados=45
        ... )
        >>> from cinetica.units import ureg
        >>> mp = MovimientoParabolicoBase(
        ...     velocidad_inicial=20 * ureg.meter / ureg.second,
        ...     angulo_grados=45 * ureg.degree,
        ...     gravedad=9.81 * ureg.meter / ureg.second**2
        ... )
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

        self.velocidad_inicial_x = self.velocidad_inicial * math.cos(
            self.angulo_radianes.magnitude
        )
        self.velocidad_inicial_y = self.velocidad_inicial * math.sin(
            self.angulo_radianes.magnitude
        )

    def posicion(self, tiempo: Q_) -> tuple[Q_, Q_]:
        """
        Calcula la posición cartesiana del proyectil en un tiempo dado.

        Utiliza las ecuaciones cinemáticas del movimiento parabólico:
        x(t) = v₀ₓ·t
        y(t) = v₀ᵧ·t - ½·g·t²

        Parameters
        ----------
        tiempo : float or pint.Quantity
            Tiempo transcurrido desde el lanzamiento, en segundos.
            Si se proporciona un float, se asume que está en segundos.
            Debe ser un valor no negativo.

        Returns
        -------
        tuple[pint.Quantity, pint.Quantity]
            Tupla (x, y) con las coordenadas de posición del proyectil.
            Ambas coordenadas tienen unidades de longitud.

        Raises
        ------
        ValueError
            Si el tiempo proporcionado es negativo.

        Examples
        --------
        >>> mp = MovimientoParabolicoBase(
        ...     velocidad_inicial=20, angulo_grados=45
        ... )
        >>> pos_x, pos_y = mp.posicion(tiempo=1)
        >>> print(f"Posición: x={pos_x:.2f}, y={pos_y:.2f}")
        Posición: x=14.14 meter, y=9.24 meter

        Notes
        -----
        La coordenada x aumenta linealmente con el tiempo (MRU),
        mientras que la coordenada y sigue una parábola (MRUV).
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        if tiempo.magnitude < 0:
            raise ValueError("El tiempo no puede ser negativo.")

        posicion_x = self.velocidad_inicial_x * tiempo
        posicion_y = (self.velocidad_inicial_y * tiempo) - (
            0.5 * self.gravedad * (tiempo**2)
        )
        return (posicion_x, posicion_y)

    def velocidad(self, tiempo: Q_) -> tuple[Q_, Q_]:
        """
        Calcula las componentes de velocidad del proyectil en un tiempo dado.

        Utiliza las ecuaciones cinemáticas del movimiento parabólico:
        vₓ(t) = v₀ₓ (constante)
        vᵧ(t) = v₀ᵧ - g·t

        Parameters
        ----------
        tiempo : float or pint.Quantity
            Tiempo transcurrido desde el lanzamiento, en segundos.
            Si se proporciona un float, se asume que está en segundos.
            Debe ser un valor no negativo.

        Returns
        -------
        tuple[pint.Quantity, pint.Quantity]
            Tupla (vₓ, vᵧ) con las componentes de velocidad del proyectil.
            Ambas componentes tienen unidades de velocidad.

        Raises
        ------
        ValueError
            Si el tiempo proporcionado es negativo.

        Examples
        --------
        >>> mp = MovimientoParabolicoBase(
        ...     velocidad_inicial=20, angulo_grados=45
        ... )
        >>> vel_x, vel_y = mp.velocidad(tiempo=1)
        >>> print(f"Velocidad: vₓ={vel_x:.2f}, vᵧ={vel_y:.2f}")
        Velocidad: vₓ=14.14 meter / second, vᵧ=4.33 meter / second

        Notes
        -----
        La componente horizontal de velocidad permanece constante,
        mientras que la componente vertical disminuye linealmente debido a la gravedad.
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
        Obtiene las componentes de aceleración del proyectil.

        En el movimiento parabólico, la aceleración es constante:
        aₓ = 0 (no hay fuerzas horizontales)
        aᵧ = -g (aceleración gravitacional hacia abajo)

        Parameters
        ----------
        tiempo : float, pint.Quantity, or None, optional
            Tiempo transcurrido en segundos. Este parámetro no afecta el resultado
            ya que la aceleración es constante en movimiento parabólico.
            Default es None.

        Returns
        -------
        tuple[pint.Quantity, pint.Quantity]
            Tupla (aₓ, aᵧ) con las componentes de aceleración del proyectil.
            Ambas componentes tienen unidades de aceleración.

        Examples
        --------
        >>> mp = MovimientoParabolicoBase(
        ...     velocidad_inicial=20, angulo_grados=45
        ... )
        >>> acel_x, acel_y = mp.aceleracion()
        >>> print(f"Aceleración: aₓ={acel_x}, aᵧ={acel_y}")
        Aceleración: aₓ=0.0 meter / second ** 2, aᵧ=-9.81 meter / second ** 2

        Notes
        -----
        La aceleración horizontal es siempre cero (despreciando la resistencia del aire),
        y la aceleración vertical es siempre igual a la gravedad hacia abajo.
        """
        # La aceleración horizontal es 0, la vertical es -gravedad
        return (0.0 * ureg.meter / ureg.second**2, -self.gravedad)
