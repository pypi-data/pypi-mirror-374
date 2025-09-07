from typing import Union, Optional
import numpy as np
from ..base_movimiento import Movimiento
from ...units import ureg, Q_


class MovimientoEspacial(Movimiento):
    """
    Clase para simular movimiento en el espacio tridimensional.

    Esta clase implementa las ecuaciones cinemáticas para el movimiento
    de un objeto en el espacio 3D con aceleración constante, utilizando
    vectores para representar posición, velocidad y aceleración.

    Parameters
    ----------
    posicion_inicial : numpy.ndarray or pint.Quantity, optional
        Vector de posición inicial en coordenadas cartesianas [x, y, z].
        Default es el origen [0, 0, 0].
    velocidad_inicial : numpy.ndarray or pint.Quantity, optional
        Vector de velocidad inicial [vₓ, vᵧ, vᶻ]. Default es [0, 0, 0].
    aceleracion_constante : numpy.ndarray or pint.Quantity, optional
        Vector de aceleración constante [aₓ, aᵧ, aᶻ]. Default es [0, 0, 0].

    Attributes
    ----------
    posicion_inicial : pint.Quantity
        Vector de posición inicial en 3D.
    velocidad_inicial : pint.Quantity
        Vector de velocidad inicial en 3D.
    aceleracion_constante : pint.Quantity
        Vector de aceleración constante en 3D.

    Examples
    --------
    >>> mov = MovimientoEspacial(
    ...     posicion_inicial=[0, 0, 0],
    ...     velocidad_inicial=[10, 5, 0],
    ...     aceleracion_constante=[0, 0, -9.81]
    ... )
    >>> pos = mov.posicion(tiempo=1)
    >>> print(f"Posición: {pos}")

    Notes
    -----
    El movimiento espacial es útil para modelar:
    - Trayectorias de proyectiles en 3D
    - Movimiento de partículas en campos de fuerza
    - Dinámica de satélites
    - Movimiento de objetos bajo múltiples fuerzas constantes
    """

    def __init__(
        self,
        posicion_inicial: Union[np.ndarray, Q_] = Q_(
            np.array([0.0, 0.0, 0.0]), ureg.meter
        ),
        velocidad_inicial: Union[np.ndarray, Q_] = Q_(
            np.array([0.0, 0.0, 0.0]), ureg.meter / ureg.second
        ),
        aceleracion_constante: Union[np.ndarray, Q_] = Q_(
            np.array([0.0, 0.0, 0.0]), ureg.meter / ureg.second**2
        ),
    ) -> None:
        """
        Inicializa una instancia de Movimiento Espacial.

        Parameters
        ----------
        posicion_inicial : numpy.ndarray or pint.Quantity, optional
            Vector de posición inicial en coordenadas cartesianas [x, y, z], en metros.
            Si se proporciona un array, se asume que está en metros.
            Debe ser un vector de 3 dimensiones. Default es [0, 0, 0].
        velocidad_inicial : numpy.ndarray or pint.Quantity, optional
            Vector de velocidad inicial [vₓ, vᵧ, vᶻ], en m/s.
            Si se proporciona un array, se asume que está en m/s.
            Debe ser un vector de 3 dimensiones. Default es [0, 0, 0].
        aceleracion_constante : numpy.ndarray or pint.Quantity, optional
            Vector de aceleración constante [aₓ, aᵧ, aᶻ], en m/s².
            Si se proporciona un array, se asume que está en m/s².
            Debe ser un vector de 3 dimensiones. Default es [0, 0, 0].

        Raises
        ------
        ValueError
            Si alguno de los vectores no es de exactamente 3 dimensiones.

        Examples
        --------
        >>> mov = MovimientoEspacial()
        >>> mov = MovimientoEspacial(
        ...     posicion_inicial=[0, 0, 10],
        ...     velocidad_inicial=[5, 0, 0],
        ...     aceleracion_constante=[0, 0, -9.81]
        ... )
        >>> from cinetica.units import ureg
        >>> mov = MovimientoEspacial(
        ...     posicion_inicial=[0, 0, 10] * ureg.meter,
        ...     velocidad_inicial=[5, 0, 0] * ureg.meter / ureg.second,
        ...     aceleracion_constante=[0, 0, -9.81] * ureg.meter / ureg.second**2
        ... )
        """
        if not isinstance(posicion_inicial, Q_):
            posicion_inicial = Q_(np.array(posicion_inicial), ureg.meter)
        if not isinstance(velocidad_inicial, Q_):
            velocidad_inicial = Q_(
                np.array(velocidad_inicial), ureg.meter / ureg.second
            )
        if not isinstance(aceleracion_constante, Q_):
            aceleracion_constante = Q_(
                np.array(aceleracion_constante), ureg.meter / ureg.second**2
            )

        if not (
            len(posicion_inicial.magnitude) == 3
            and len(velocidad_inicial.magnitude) == 3
            and len(aceleracion_constante.magnitude) == 3
        ):
            raise ValueError(
                "Todos los vectores (posición, velocidad, aceleración) deben ser de 3 dimensiones."
            )

        self.posicion_inicial = posicion_inicial
        self.velocidad_inicial = velocidad_inicial
        self.aceleracion_constante = aceleracion_constante

    def graficar(
        self, t_max: Union[float, Q_] = 10.0 * ureg.second, num_points: int = 100
    ) -> None:
        """
        Genera un gráfico 3D de la trayectoria del movimiento.

        Crea una visualización tridimensional de la trayectoria del objeto
        en el espacio durante el intervalo de tiempo especificado.

        Parameters
        ----------
        t_max : float or pint.Quantity, optional
            Tiempo máximo para la simulación y graficación, en segundos.
            Si se proporciona un float, se asume que está en segundos.
            Default es 10.0 segundos.
        num_points : int, optional
            Número de puntos a calcular y graficar en la trayectoria.
            Mayor número de puntos resulta en una curva más suave.
            Default es 100.

        Examples
        --------
        >>> mov = MovimientoEspacial(
        ...     velocidad_inicial=[10, 5, 15],
        ...     aceleracion_constante=[0, 0, -9.81]
        ... )
        >>> mov.graficar(t_max=3, num_points=150)

        Notes
        -----
        Este método requiere matplotlib para generar el gráfico.
        El gráfico mostrará la trayectoria completa en el espacio 3D
        con ejes etiquetados apropiadamente.
        """
        import matplotlib.pyplot as plt

        if not isinstance(t_max, Q_):
            t_max = Q_(t_max, ureg.second)

        t = np.linspace(0, t_max.magnitude, num_points) * ureg.second
        posiciones = np.array([self.posicion(ti).magnitude for ti in t])

        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
        ax.plot(posiciones[:, 0], posiciones[:, 1], posiciones[:, 2])
        ax.set_xlabel(f"X ({self.posicion_inicial.units:~P})")
        ax.set_ylabel(f"Y ({self.posicion_inicial.units:~P})")
        ax.set_zlabel(f"Z ({self.posicion_inicial.units:~P})")
        ax.set_title("Trayectoria en 3D")
        plt.show()

    def posicion(self, tiempo: Union[float, Q_]) -> Q_:
        """
        Calcula el vector de posición del objeto en un tiempo dado.

        Utiliza la ecuación cinemática fundamental para movimiento
        con aceleración constante en 3D:
        r⃗(t) = r⃗₀ + v⃗₀·t + ½·a⃗·t²

        Parameters
        ----------
        tiempo : float or pint.Quantity
            Tiempo transcurrido desde el inicio del movimiento, en segundos.
            Si se proporciona un float, se asume que está en segundos.
            Debe ser un valor no negativo.

        Returns
        -------
        pint.Quantity
            Vector de posición [x, y, z] del objeto en el tiempo especificado,
            con unidades de longitud.

        Raises
        ------
        ValueError
            Si el tiempo proporcionado es negativo.

        Examples
        --------
        >>> mov = MovimientoEspacial(
        ...     posicion_inicial=[0, 0, 0],
        ...     velocidad_inicial=[10, 5, 0],
        ...     aceleracion_constante=[0, 0, -9.81]
        ... )
        >>> pos = mov.posicion(tiempo=1)
        >>> print(f"Posición: {pos}")
        Posición: [10.0 5.0 -4.905] meter

        Notes
        -----
        Esta ecuación es válida para cualquier sistema de coordenadas
        cartesianas y asume aceleración constante en cada componente.
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        if tiempo.magnitude < 0:
            raise ValueError("El tiempo no puede ser negativo.")
        return (
            self.posicion_inicial
            + self.velocidad_inicial * tiempo
            + 0.5 * self.aceleracion_constante * (tiempo**2)
        )

    def velocidad(self, tiempo: Union[float, Q_]) -> Q_:
        """
        Calcula el vector de velocidad del objeto en un tiempo dado.

        Utiliza la ecuación cinemática para velocidad con
        aceleración constante en 3D:
        v⃗(t) = v⃗₀ + a⃗·t

        Parameters
        ----------
        tiempo : float or pint.Quantity
            Tiempo transcurrido desde el inicio del movimiento, en segundos.
            Si se proporciona un float, se asume que está en segundos.
            Debe ser un valor no negativo.

        Returns
        -------
        pint.Quantity
            Vector de velocidad [vₓ, vᵧ, vᶻ] del objeto en el tiempo especificado,
            con unidades de velocidad.

        Raises
        ------
        ValueError
            Si el tiempo proporcionado es negativo.

        Examples
        --------
        >>> mov = MovimientoEspacial(
        ...     velocidad_inicial=[10, 5, 0],
        ...     aceleracion_constante=[0, 0, -9.81]
        ... )
        >>> vel = mov.velocidad(tiempo=1)
        >>> print(f"Velocidad: {vel}")
        Velocidad: [10.0 5.0 -9.81] meter / second

        Notes
        -----
        La velocidad varía linealmente con el tiempo cuando
        la aceleración es constante.
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        if tiempo.magnitude < 0:
            raise ValueError("El tiempo no puede ser negativo.")
        return self.velocidad_inicial + self.aceleracion_constante * tiempo

    def aceleracion(self, tiempo: Optional[Union[float, Q_]] = None) -> Q_:
        """
        Obtiene el vector de aceleración del objeto.

        En este modelo, la aceleración es constante e independiente del tiempo:
        a⃗(t) = a⃗_constante

        Parameters
        ----------
        tiempo : float, pint.Quantity, or None, optional
            Tiempo transcurrido en segundos. Este parámetro no afecta el resultado
            ya que la aceleración es constante. Default es None.

        Returns
        -------
        pint.Quantity
            Vector de aceleración [aₓ, aᵧ, aᶻ] del objeto,
            con unidades de aceleración.

        Examples
        --------
        >>> mov = MovimientoEspacial(
        ...     aceleracion_constante=[0, 0, -9.81]
        ... )
        >>> acel = mov.aceleracion()
        >>> print(f"Aceleración: {acel}")
        Aceleración: [0.0 0.0 -9.81] meter / second ** 2

        Notes
        -----
        Este método devuelve el vector de aceleración completo.
        Para obtener solo la magnitud, use magnitud_aceleracion().
        """
        # La aceleración es constante, no depende del tiempo
        return self.aceleracion_constante

    def magnitud_aceleracion(self) -> Q_:
        """
        Calcula la magnitud del vector de aceleración.

        La magnitud se calcula como la norma euclidiana del vector:
        |a⃗| = √(aₓ² + aᵧ² + aᶻ²)

        Returns
        -------
        pint.Quantity
            Magnitud escalar de la aceleración, con unidades de aceleración.

        Examples
        --------
        >>> mov = MovimientoEspacial(
        ...     aceleracion_constante=[3, 4, 0]
        ... )
        >>> mag_a = mov.magnitud_aceleracion()
        >>> print(f"Magnitud de aceleración: {mag_a}")
        Magnitud de aceleración: 5.0 meter / second ** 2

        Notes
        -----
        Este método es equivalente a magnitud_aceleracion_constante().
        """
        return Q_(
            np.linalg.norm(self.aceleracion_constante.magnitude),
            self.aceleracion_constante.units,
        )

    def magnitud_velocidad(self, tiempo: Union[float, Q_]) -> Q_:
        """
        Calcula la magnitud del vector de velocidad en un tiempo dado.

        La magnitud se calcula como la norma euclidiana del vector velocidad:
        |v⃗(t)| = √(vₓ(t)² + vᵧ(t)² + vᶻ(t)²)

        Parameters
        ----------
        tiempo : float or pint.Quantity
            Tiempo transcurrido desde el inicio del movimiento, en segundos.
            Si se proporciona un float, se asume que está en segundos.

        Returns
        -------
        pint.Quantity
            Magnitud escalar de la velocidad en el tiempo especificado,
            con unidades de velocidad.

        Examples
        --------
        >>> mov = MovimientoEspacial(
        ...     velocidad_inicial=[3, 4, 0],
        ...     aceleracion_constante=[0, 0, 0]
        ... )
        >>> mag_v = mov.magnitud_velocidad(tiempo=1)
        >>> print(f"Magnitud de velocidad: {mag_v}")
        Magnitud de velocidad: 5.0 meter / second

        Notes
        -----
        La magnitud de velocidad representa la rapidez del objeto,
        independientemente de su dirección de movimiento.
        """
        if not isinstance(tiempo, Q_):
            tiempo = Q_(tiempo, ureg.second)
        velocity_vector = self.velocidad(tiempo)
        return Q_(np.linalg.norm(velocity_vector.magnitude), velocity_vector.units)

    def magnitud_aceleracion_constante(self) -> Q_:
        """
        Calcula la magnitud de la aceleración constante.

        Este método es equivalente a magnitud_aceleracion() y se proporciona
        para mayor claridad semántica.

        Returns
        -------
        pint.Quantity
            Magnitud escalar de la aceleración constante,
            con unidades de aceleración.

        Examples
        --------
        >>> mov = MovimientoEspacial(
        ...     aceleracion_constante=[0, 0, -9.81]
        ... )
        >>> mag_a = mov.magnitud_aceleracion_constante()
        >>> print(f"Magnitud de aceleración: {mag_a}")
        Magnitud de aceleración: 9.81 meter / second ** 2

        See Also
        --------
        magnitud_aceleracion : Método equivalente
        """
        return Q_(
            np.linalg.norm(self.aceleracion_constante.magnitude),
            self.aceleracion_constante.units,
        )
