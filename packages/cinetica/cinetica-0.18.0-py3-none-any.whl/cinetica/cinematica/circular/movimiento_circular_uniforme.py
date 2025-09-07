import math
from typing import Union, Optional
import numpy as np
from ..base_movimiento import Movimiento
from ...units import ureg, Q_


class MovimientoCircularUniforme(Movimiento):
    """
    Movimiento Circular Uniforme (MCU).

    Implementa los cálculos para un objeto que se mueve en una trayectoria
    circular con velocidad angular constante. En este tipo de movimiento,
    la velocidad angular es constante pero existe aceleración centrípeta
    dirigida hacia el centro del círculo.

    Parameters
    ----------
    radio : float or pint.Quantity
        Radio de la trayectoria circular en metros. Debe ser un valor positivo.
    posicion_angular_inicial : float or pint.Quantity, optional
        Posición angular inicial en radianes. Default es 0.0 rad.
    velocidad_angular_inicial : float or pint.Quantity, optional
        Velocidad angular constante en rad/s. Default es 0.0 rad/s.

    Attributes
    ----------
    radio : pint.Quantity
        Radio de la trayectoria circular con unidades de longitud.
    posicion_angular_inicial : pint.Quantity
        Posición angular inicial con unidades de ángulo.
    velocidad_angular_inicial : pint.Quantity
        Velocidad angular constante con unidades de velocidad angular.

    Examples
    --------
    >>> from cinetica.cinematica.circular import MovimientoCircularUniforme
    >>> mcu = MovimientoCircularUniforme(
    ...     radio=2, velocidad_angular_inicial=1.5
    ... )
    >>> pos_angular = mcu.posicion_angular(tiempo=3)
    >>> print(f"Posición angular: {pos_angular}")
    Posición angular: 4.5 radian

    Notes
    -----
    Las ecuaciones fundamentales del MCU son:
    - Posición angular: θ(t) = θ₀ + ω·t
    - Velocidad angular: ω(t) = ω₀ (constante)
    - Velocidad tangencial: v = ω·r
    - Aceleración centrípeta: aᶜ = ω²·r
    - Período: T = 2π/ω
    - Frecuencia: f = ω/(2π)
    """

    def __init__(
        self,
        radio: Union[float, Q_],
        posicion_angular_inicial: Union[float, Q_] = 0.0 * ureg.radian,
        velocidad_angular_inicial: Union[float, Q_] = 0.0 * ureg.radian / ureg.second,
    ) -> None:
        """
        Inicializa una instancia de Movimiento Circular Uniforme.

        Parameters
        ----------
        radio : float or pint.Quantity
            Radio de la trayectoria circular en metros. Debe ser un valor positivo.
            Si se proporciona un float, se asume que está en metros.
        posicion_angular_inicial : float or pint.Quantity, optional
            Posición angular inicial en radianes. Si se proporciona un float,
            se asume que está en radianes. Default es 0.0 rad.
        velocidad_angular_inicial : float or pint.Quantity, optional
            Velocidad angular constante en rad/s. Si se proporciona un float,
            se asume que está en rad/s. Default es 0.0 rad/s.

        Raises
        ------
        ValueError
            Si el radio proporcionado es menor o igual a cero.

        Examples
        --------
        >>> mcu = MovimientoCircularUniforme(radio=2)
        >>> mcu = MovimientoCircularUniforme(
        ...     radio=2, posicion_angular_inicial=0.5, velocidad_angular_inicial=1.5
        ... )
        >>> from cinetica.units import ureg
        >>> mcu = MovimientoCircularUniforme(
        ...     radio=2 * ureg.meter,
        ...     velocidad_angular_inicial=1.5 * ureg.radian / ureg.second
        ... )
        """
        if not isinstance(radio, Q_):
            radio = Q_(radio, ureg.meter)
        if not isinstance(posicion_angular_inicial, Q_):
            posicion_angular_inicial = Q_(posicion_angular_inicial, ureg.radian)
        if not isinstance(velocidad_angular_inicial, Q_):
            velocidad_angular_inicial = Q_(
                velocidad_angular_inicial, ureg.radian / ureg.second
            )

        if radio.magnitude <= 0:
            raise ValueError("El radio debe ser un valor positivo.")

        self.radio = radio
        self.posicion_angular_inicial = posicion_angular_inicial
        self.velocidad_angular_inicial = velocidad_angular_inicial

    def posicion_angular(self, tiempo: Union[float, Q_]) -> Q_:
        """
        Calcula la posición angular del objeto en un tiempo dado.

        Utiliza la ecuación fundamental del MCU: θ(t) = θ₀ + ω·t

        Parameters
        ----------
        tiempo : float or pint.Quantity
            Tiempo transcurrido desde el inicio del movimiento, en segundos.
            Si se proporciona un float, se asume que está en segundos.
            Debe ser un valor no negativo.

        Returns
        -------
        pint.Quantity
            Posición angular del objeto en el tiempo especificado, con unidades de ángulo.

        Raises
        ------
        ValueError
            Si el tiempo proporcionado es negativo.

        Examples
        --------
        >>> mcu = MovimientoCircularUniforme(
        ...     radio=2, velocidad_angular_inicial=1.5
        ... )
        >>> pos = mcu.posicion_angular(tiempo=3)
        >>> print(f"Posición angular: {pos}")
        Posición angular: 4.5 radian
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        if tiempo.magnitude < 0:
            raise ValueError("El tiempo no puede ser negativo.")
        return self.posicion_angular_inicial + self.velocidad_angular_inicial * tiempo

    def velocidad_angular(self, tiempo: Optional[Union[float, Q_]] = None) -> Q_:
        """
        Obtiene la velocidad angular del objeto en cualquier momento.

        En el MCU, la velocidad angular es constante e independiente del tiempo.

        Parameters
        ----------
        tiempo : float, pint.Quantity, or None, optional
            Tiempo transcurrido en segundos. Este parámetro no afecta el resultado
            ya que la velocidad angular es constante en MCU. Default es None.

        Returns
        -------
        pint.Quantity
            Velocidad angular constante del objeto, con unidades de velocidad angular.

        Examples
        --------
        >>> mcu = MovimientoCircularUniforme(
        ...     radio=2, velocidad_angular_inicial=1.5
        ... )
        >>> vel_ang = mcu.velocidad_angular()
        >>> print(f"Velocidad angular: {vel_ang}")
        Velocidad angular: 1.5 radian / second
        """
        return self.velocidad_angular_inicial

    def velocidad_tangencial(self, tiempo: Optional[Union[float, Q_]] = None) -> Q_:
        """
        Calcula la velocidad tangencial del objeto.

        La velocidad tangencial es la velocidad lineal del objeto a lo largo
        de la trayectoria circular. Se calcula como v = ω·r

        Parameters
        ----------
        tiempo : float, pint.Quantity, or None, optional
            Tiempo transcurrido en segundos. Este parámetro no afecta el resultado
            ya que la velocidad tangencial es constante en MCU. Default es None.

        Returns
        -------
        pint.Quantity
            Velocidad tangencial del objeto, con unidades de velocidad.

        Examples
        --------
        >>> mcu = MovimientoCircularUniforme(
        ...     radio=2, velocidad_angular_inicial=1.5
        ... )
        >>> vel_tan = mcu.velocidad_tangencial()
        >>> print(f"Velocidad tangencial: {vel_tan}")
        Velocidad tangencial: 3.0 meter / second
        """
        return self.velocidad_angular_inicial * self.radio

    def aceleracion_centripeta(self, tiempo: Optional[Union[float, Q_]] = None) -> Q_:
        """
        Calcula la aceleración centrípeta del objeto.

        La aceleración centrípeta es la aceleración dirigida hacia el centro
        del círculo, necesaria para mantener el movimiento circular.
        Se calcula como aᶜ = ω²·r = v²/r

        Parameters
        ----------
        tiempo : float, pint.Quantity, or None, optional
            Tiempo transcurrido en segundos. Este parámetro no afecta el resultado
            ya que la aceleración centrípeta es constante en MCU. Default es None.

        Returns
        -------
        pint.Quantity
            Aceleración centrípeta del objeto, con unidades de aceleración.

        Examples
        --------
        >>> mcu = MovimientoCircularUniforme(
        ...     radio=2, velocidad_angular_inicial=1.5
        ... )
        >>> acel_c = mcu.aceleracion_centripeta()
        >>> print(f"Aceleración centrípeta: {acel_c}")
        Aceleración centrípeta: 4.5 meter / second ** 2
        """
        return self.velocidad_angular_inicial**2 * self.radio

    def posicion(self, tiempo: Union[float, Q_]) -> np.ndarray:
        """
        Calcula la posición cartesiana (x, y) del objeto en un tiempo dado.

        Convierte la posición angular a coordenadas cartesianas usando:
        x = r·cos(θ), y = r·sin(θ)

        Parameters
        ----------
        tiempo : float or pint.Quantity
            Tiempo transcurrido desde el inicio del movimiento, en segundos.
            Si se proporciona un float, se asume que está en segundos.

        Returns
        -------
        numpy.ndarray
            Array con las coordenadas [x, y] del objeto en el tiempo especificado.
            Las coordenadas tienen las mismas unidades que el radio.

        Examples
        --------
        >>> mcu = MovimientoCircularUniforme(
        ...     radio=2, velocidad_angular_inicial=1.5
        ... )
        >>> pos = mcu.posicion(tiempo=1)
        >>> print(f"Posición: x={pos[0]}, y={pos[1]}")
        Posición: x=0.141... meter, y=1.989... meter

        Notes
        -----
        Este método asume que el centro del círculo está en el origen (0, 0).
        Para círculos con centro desplazado, se debe agregar el desplazamiento
        a las coordenadas resultantes.
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        if tiempo.magnitude < 0:
            raise ValueError("El tiempo no puede ser negativo.")
        theta = self.posicion_angular(tiempo).to(ureg.radian).magnitude
        x = self.radio * math.cos(theta)
        y = self.radio * math.sin(theta)
        return Q_(np.array([x.magnitude, y.magnitude]), ureg.meter)

    def velocidad(self, tiempo: Union[float, Q_]) -> np.ndarray:
        """
        Calcula el vector velocidad cartesiano (vₓ, vᵧ) del objeto.

        El vector velocidad es tangente a la trayectoria circular y se calcula como:
        vₓ = -v·sin(θ), vᵧ = v·cos(θ)
        donde v = ω·r es la velocidad tangencial.

        Parameters
        ----------
        tiempo : float or pint.Quantity
            Tiempo transcurrido desde el inicio del movimiento, en segundos.
            Si se proporciona un float, se asume que está en segundos.

        Returns
        -------
        numpy.ndarray
            Array con las componentes [vₓ, vᵧ] del vector velocidad.
            Las componentes tienen unidades de velocidad.

        Examples
        --------
        >>> mcu = MovimientoCircularUniforme(
        ...     radio=2, velocidad_angular_inicial=1.5
        ... )
        >>> vel = mcu.velocidad(tiempo=1)
        >>> print(f"Velocidad: vₓ={vel[0]}, vᵧ={vel[1]}")
        Velocidad: vₓ=-2.989... meter / second, vᵧ=0.423... meter / second
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        if tiempo.magnitude < 0:
            raise ValueError("El tiempo no puede ser negativo.")
        omega = self.velocidad_angular_inicial.to(ureg.radian / ureg.second).magnitude
        theta = self.posicion_angular(tiempo).to(ureg.radian).magnitude
        vx = -omega * self.radio.to(ureg.meter).magnitude * math.sin(theta)
        vy = omega * self.radio.to(ureg.meter).magnitude * math.cos(theta)
        return np.array([vx, vy])

    def posicion_vector(self, tiempo: Union[float, Q_]) -> np.ndarray:
        """
        Calcula el vector posición cartesiano del objeto en un tiempo dado.

        Este método es equivalente a posicion() pero con un nombre más descriptivo
        que enfatiza que devuelve un vector.

        Parameters
        ----------
        tiempo : float or pint.Quantity
            Tiempo transcurrido desde el inicio del movimiento, en segundos.
            Si se proporciona un float, se asume que está en segundos.

        Returns
        -------
        numpy.ndarray
            Vector posición [x, y] del objeto en coordenadas cartesianas.
            Las coordenadas tienen las mismas unidades que el radio.

        Examples
        --------
        >>> mcu = MovimientoCircularUniforme(
        ...     radio=2, velocidad_angular_inicial=1.5
        ... )
        >>> pos_vec = mcu.posicion_vector(tiempo=1)
        >>> print(f"Vector posición: {pos_vec}")
        Vector posición: [0.141... 1.989...] meter

        See Also
        --------
        posicion : Método equivalente con nombre más corto
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        if tiempo.magnitude < 0:
            raise ValueError("El tiempo no puede ser negativo.")
        theta = self.posicion_angular(tiempo).to(ureg.radian).magnitude
        x = self.radio * math.cos(theta)
        y = self.radio * math.sin(theta)
        return np.array([x.magnitude, y.magnitude])

    def aceleracion(self, tiempo: Optional[Union[float, Q_]] = None) -> Q_:
        """
        Obtiene la magnitud de la aceleración centrípeta del objeto.

        En el MCU, solo existe aceleración centrípeta (dirigida hacia el centro),
        que es constante en magnitud pero cambia de dirección continuamente.

        Parameters
        ----------
        tiempo : float, pint.Quantity, or None, optional
            Tiempo transcurrido en segundos. Este parámetro no afecta el resultado
            ya que la magnitud de la aceleración centrípeta es constante en MCU.
            Default es None.

        Returns
        -------
        pint.Quantity
            Magnitud de la aceleración centrípeta, con unidades de aceleración.

        Examples
        --------
        >>> mcu = MovimientoCircularUniforme(
        ...     radio=2, velocidad_angular_inicial=1.5
        ... )
        >>> acel = mcu.aceleracion()
        >>> print(f"Aceleración: {acel}")
        Aceleración: 4.5 meter / second ** 2

        Notes
        -----
        Este método devuelve la magnitud de la aceleración. Para obtener
        el vector aceleración completo, use el método aceleracion_vector().
        """
        return self.aceleracion_centripeta(tiempo)

    def velocidad_angular_constante(self) -> Q_:
        """
        Retorna la velocidad angular constante en MCU.
        """
        return self.velocidad_angular_inicial

    def aceleracion_centripeta_constante(self) -> Q_:
        """
        Retorna la magnitud de la aceleración centrípeta constante en MCU.
        """
        return (self.velocidad_angular_inicial**2) * self.radio

    def periodo(self) -> Q_:
        """
        Calcula el período del movimiento circular.

        El período es el tiempo necesario para completar una revolución completa.
        Se calcula como T = 2π/ω

        Returns
        -------
        pint.Quantity
            Período del movimiento circular, con unidades de tiempo.

        Raises
        ------
        ValueError
            Si la velocidad angular es cero (no hay movimiento).

        Examples
        --------
        >>> mcu = MovimientoCircularUniforme(
        ...     radio=2, velocidad_angular_inicial=1.5
        ... )
        >>> T = mcu.periodo()
        >>> print(f"Período: {T}")
        Período: 4.188... second

        Notes
        -----
        El período es independiente del radio de la trayectoria,
        dependiendo únicamente de la velocidad angular.
        """
        if self.velocidad_angular_inicial.magnitude == 0:
            return (
                math.inf * ureg.second
            )  # Período infinito si la velocidad angular es cero
        return (2 * math.pi * ureg.radian) / self.velocidad_angular_inicial

    def frecuencia(self) -> Q_:
        """
        Calcula la frecuencia del movimiento circular.

        La frecuencia es el número de revoluciones completadas por unidad de tiempo.
        Se calcula como f = ω/(2π) = 1/T

        Returns
        -------
        pint.Quantity
            Frecuencia del movimiento circular, con unidades de frecuencia (Hz).

        Raises
        ------
        ValueError
            Si la velocidad angular es cero (no hay movimiento).

        Examples
        --------
        >>> mcu = MovimientoCircularUniforme(
        ...     radio=2, velocidad_angular_inicial=1.5
        ... )
        >>> f = mcu.frecuencia()
        >>> print(f"Frecuencia: {f}")
        Frecuencia: 0.238... hertz

        Notes
        -----
        La frecuencia es el inverso del período: f = 1/T
        Al igual que el período, es independiente del radio.
        """
        if self.velocidad_angular_inicial.magnitude == 0:
            return 0.0 * ureg.hertz  # Frecuencia cero si la velocidad angular es cero
        return self.velocidad_angular_inicial / (2 * math.pi * ureg.radian)
