from xml.etree import ElementTree
from xml.etree.ElementTree import Element
import re

from .._logger import logger


class NamespaceNameAlreadyUsed(Exception):
    def __init__(self, tag: str, name: str, uri_new: str, uri_old: str):
        super().__init__(
            f"Namespace '{name}' already mapped to '{uri_old}', "
            f"can't remap to '{uri_new}' from element '{tag}'"
        )


class BaseXMLParser:
    def __init__(self, filepath: str):
        self._tree = ElementTree.parse(filepath)
        self._root = self._tree.getroot()
        self._ns: dict = {}

    def register_namespace(self, elem: Element, name: str):
        try:
            uri = self._get_namespace_uri(elem)

            if uri is None:
                logger.warning(f"Namespace not found in element '{elem.tag}'")
                return

            if name not in self._ns.keys():
                self._ns[name] = uri
            elif self._ns[name] != uri:
                raise NamespaceNameAlreadyUsed(elem.tag, name, uri, self._ns[name])

        except NamespaceNameAlreadyUsed:
            logger.exception(
                "Namespace with same name but different uri is already registered"
            )
            raise

    @staticmethod
    def _get_namespace_uri(elem: Element) -> str | None:
        m = re.match(r"\{(.*)}", elem.tag)
        return m.group(1) if m else None
