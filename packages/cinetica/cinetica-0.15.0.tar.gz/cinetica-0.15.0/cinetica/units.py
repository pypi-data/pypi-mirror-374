from typing import TYPE_CHECKING
from pint import UnitRegistry, Quantity

ureg: UnitRegistry = UnitRegistry()

if TYPE_CHECKING:
    from typing import TypeAlias

    Q_: TypeAlias = Quantity
else:
    Q_ = ureg.Quantity
