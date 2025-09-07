from dataclasses import dataclass
import re
from itertools import product

from .._logger import logger


class WrongSTM32NamePattern(Exception):
    def __init__(self, name_str: str):
        super().__init__(f"STM32 name '{name_str}' does not match expected pattern")


_stm32_name_pattern = re.compile(
    r"stm32"
    r"(?P<family>f0|f1|f2|f3|f4|f7|l0|l1|l4|l4\+|l5|u0|u3|u5|n6|h5|h7|g0|g4|wb|wb0|wba|wl|c0|mp1|mp2|wl3)"
    r"(?:(?P<line>[0-9a-z]{2})"
    r"(?:(?P<pin>[dyfegkthscurjmovqzaibnxplw])"
    r"(?:(?P<memory>[0123456789abzcdefghiyj])"
    r"(?:(?P<package>[bdghijkmpqtuvyxflcaes])"
    r"(?:(?P<temperature>[673abcdx])"
    r"(?P<variant>.*)?)?)?)?)?)?"
)


@dataclass(slots=True, frozen=True)
class DevName:
    family: str
    line: str
    pin: str
    memory: str
    package: str
    temperature: str
    variant: str

    @property
    def model(self) -> str:
        return f"stm32{self.family}{self.line}{self.pin}{self.memory}{self.package}"

    @classmethod
    def from_str(cls, s: str):
        try:
            match = _stm32_name_pattern.fullmatch(s.lower())
            if match is None:
                raise WrongSTM32NamePattern(s)

            def get_field(field_name: str, remove_x: bool = False) -> str:
                d = match.group(field_name) or ""
                if remove_x:
                    d = "" if d == "x" else d
                return d

            return cls(
                family=get_field("family"),
                line=get_field("line"),
                pin=get_field("pin"),
                memory=get_field("memory"),
                package=get_field("package", remove_x=True),
                temperature=get_field("temperature", remove_x=True),
                variant=get_field("variant"),
            )

        except WrongSTM32NamePattern:
            logger.exception("Can't parse STM32 name because of pattern mismatch")
            raise


# STM32G473P(B-C-E)Ix
def expand_name_variants(s: str) -> list[str]:
    parts = re.split(r"(\([^)]+\))", s)
    option_lists = []
    for part in parts:
        if part.startswith("(") and part.endswith(")"):
            # bracket part
            options = part[1:-1].split("-")
            option_lists.append(options)
        else:
            # non-bracket part
            option_lists.append([part])

    variants = ["".join(combo) for combo in product(*option_lists)]
    return variants
