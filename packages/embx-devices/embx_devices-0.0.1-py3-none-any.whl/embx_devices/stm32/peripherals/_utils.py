from ._models import PeripheralDef
from ..device_name import DevName
from ..mask import check_mask
from ._db import stm32_peripheral_db
from ..._logger import logger


class NoPeripheralVersionInDB(Exception):
    def __init__(self, peripheral_name: str, instance: int, dev: DevName):
        super().__init__(
            f"Peripheral version not found in database: "
            f"name='{peripheral_name}', instance={instance}, device='{dev.model}'"
        )


def get_peripheral_from_db(
    peripheral_name: str, instance: int, dev: DevName
) -> PeripheralDef | None:
    if peripheral_name in stm32_peripheral_db.keys():
        periph_db = stm32_peripheral_db[peripheral_name]
        for mask in periph_db.keys():
            if check_mask(mask, dev):
                for periph_case in periph_db[mask]:
                    if instance in periph_case.instances:
                        return periph_case

    try:
        raise NoPeripheralVersionInDB(peripheral_name, instance, dev)
    except NoPeripheralVersionInDB:
        logger.exception("Can't find peripheral version in database")
        raise
