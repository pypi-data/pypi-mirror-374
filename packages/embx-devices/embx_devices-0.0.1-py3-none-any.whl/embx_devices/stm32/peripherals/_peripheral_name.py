import re
from dataclasses import dataclass

from ..._logger import logger

_peripheral_name_pattern = re.compile(
    r"(?P<name>.*?)"
    r"(?P<instance>\d{1,2})?"
)


class WrongPeripheralNamePattern(Exception):
    def __init__(self, name_str: str):
        super().__init__(
            f"Peripheral name '{name_str}' does not match expected pattern"
        )


@dataclass(slots=True, frozen=True)
class PeripheralName:
    name: str
    instance: int

    @classmethod
    def from_str(cls, s: str):
        try:
            match = _peripheral_name_pattern.fullmatch(s.lower())
            if match is None:
                raise WrongPeripheralNamePattern(s)
            instance = int(match.group("instance")) if match.group("instance") else 0
            name = match.group("name")
            return cls(name, instance)

        except WrongPeripheralNamePattern:
            logger.exception("Can't parse peripheral name because of pattern mismatch")
            raise
