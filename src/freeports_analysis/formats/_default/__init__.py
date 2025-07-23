from enum import Enum
from lxml import etree
from typing import List
from .. import PdfBlock, TextBlock


def pdf_filter(xml_root: etree.Element) -> List[PdfBlock]:
    raise NotImplementedError


def text_extract(pdf_blocks: List[PdfBlock], targets: List[str]) -> List[TextBlock]:
    raise NotImplementedError


def deserialize(txt_blocks: TextBlock) -> dict:
    raise NotImplementedError


class PdfBlockType(Enum): ...


class TextBlockType(Enum): ...
