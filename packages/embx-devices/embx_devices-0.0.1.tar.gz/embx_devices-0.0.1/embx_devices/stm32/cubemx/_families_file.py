from ..._logger import logger
from ..device_name import DevName
from ...utils.base_xml_parser import BaseXMLParser
from ..device_group import DevGroup
from ._models import ValidDevices


class FamiliesFile(BaseXMLParser):
    def __init__(self, filepath: str):
        super().__init__(filepath=filepath)

    def extract_valid_devices(self, dev_group: DevGroup) -> ValidDevices:
        mcu_elems = self._root.findall("Family/SubFamily/Mcu")

        ref_names = []
        cubemx_names = set()

        for mcu_elem in mcu_elems:
            ref_name = mcu_elem.get("RefName").lower()
            cubemx_name = mcu_elem.get("Name")
            parsed_name = DevName.from_str(ref_name)
            if dev_group.includes_device(parsed_name):
                ref_names.append(ref_name)
                cubemx_names.add(cubemx_name)

        parsed_names = [DevName.from_str(dev) for dev in sorted(ref_names)]

        return ValidDevices(
            cubemx_names=sorted(cubemx_names),
            devices=parsed_names,
        )
