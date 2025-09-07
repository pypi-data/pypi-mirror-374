from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class PeripheralDef:
    instances: tuple
    version: str
    tags: tuple[str, ...] = field(default_factory=tuple)


@dataclass(slots=True, frozen=True)
class Peripheral:
    name: str
    instances: tuple
    version: str
    tags: tuple[str, ...]

    @classmethod
    def from_dict(cls, d: dict):
        return cls(d["name"], tuple(d["instances"]), d["version"], tuple(d["tags"]))


@dataclass(slots=True, frozen=True)
class PeripheralMasked:
    name: str
    instances: tuple
    version: str
    tags: tuple[str, ...]
    mask: str
