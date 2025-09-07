from dataclasses import dataclass

from .memory import MemMap
from .peripherals import PeripheralMasked


@dataclass(frozen=True, slots=True)
class STM32Data:
    devices: list[str]
    memory: MemMap
    peripherals: list[PeripheralMasked]
