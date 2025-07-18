"""Module common to each format, it contains the definitions used by all the formats"""

from enum import Enum
from typing import Optional, List, Callable
import logging as log
from lxml import etree
from freeports_analysis.consts import FinancialData, PromisesResolutionContext
from freeports_analysis.i18n import _

logger = log.getLogger(__name__)


class LogFormatterWithPage(log.Formatter):
    """Formatter that inherit the behaviour from
    another formatter given in input, but insert into it
    an attrinbute that rappresent the page number of the pdf report
    """

    def __init__(self, old_formatter: log.Formatter):
        """Initialize the LogFormatterWithPage taking another formatter
        as reference to modify

        Parameters
        ----------
        old_formatter : logging.Formatter
            the formatter to take as reference
        """
        super().__init__()
        self._parent_fmt = old_formatter
        self.page = None

    def format(self, record: log.LogRecord) -> str:
        """Method used to get the rappresentation of the report.
        overwrite the inherited one

        Parameters
        ----------
        record : logging.LogRecord
            the record to format

        Returns
        -------
        str
            formatted version of the record
        """
        string = self._parent_fmt.format(record).replace(":", f"{{pag. {self.page}}}:")
        return string


def _str_blocks(blk) -> str:
    """Basic function to format both PdfBlock and TextBlock
    for string rappresentation

    Parameters
    ----------
    blk : PdfBlock | TextBlock
        block to format

    Returns
    -------
    str
        formatted version
    """
    type_translated = _("({} type)").format(blk.type_block.name)
    metadata_translated = _("metadata")
    text = f"{blk.__class__.__name__}:  {type_translated}\n"
    text += f"\t{metadata_translated} {blk.metadata}\n"
    text_no_last_nl = blk.content
    if len(blk.content) > 0:
        if blk.content[-1] == "\n":
            text_no_last_nl = text_no_last_nl[:-1]
    text += f'\t"{text_no_last_nl}"'
    return text


def _eq_blocks(a, b) -> bool:
    equal = True
    equal = equal and a.type_block == b.type_block
    equal = equal and a.metadata == b.metadata
    equal = equal and a.content == b.content
    return equal


class PdfBlock:
    """Represents a PDF content block with data to be extracted or relevant
    for subsequent filtering stages.

    Attributes
    ----------
    type_block : Enum
        The type of the PDF block.
    metadata : Optional[dict]
        Additional metadata associated with the block.
    content : Optional[str]
        The textual content extracted from the block.
    """

    type_block: Enum
    metadata: Optional[dict]
    content: Optional[str]

    def _text_form_element(self, ele: etree.Element) -> str:
        """Extracts text content from an XML element representing a PDF block.

        Args
        ----
        ele : etree.Element
            The XML element to extract text from.

        Returns
        -------
        str
            The extracted text content.
        """
        text = ""
        if ele.tag == "line":
            lines = [ele]
        else:
            lines = ele.findall("line")
        for line in lines:
            for e in line.findall(".//char"):
                c = e.get("c")
                if c is not None:
                    text += c
            text += "\n"
        return text

    def __eq__(self, other):
        """Compares two PdfBlock instances for equality.

        Parameters
        ----------
        other : PdfBlock
            The other PdfBlock to compare with.

        Returns
        -------
        bool
            True if the blocks are equal, False otherwise.
        """
        equal = _eq_blocks(self, other)
        return equal

    def __init__(
        self,
        type_block: Enum,
        metadata: dict,
        xml_ele: etree.Element | List[etree.Element],
    ):
        """Initializes a PdfBlock instance.

        Parameters
        ----------
        type_block : Enum
            The type of the PDF block.
        metadata : dict
            Additional metadata for the block.
        xml_ele : etree.Element | List[etree.Element]
            The XML element(s) containing the block's content.
        """
        self.type_block = type_block
        self.metadata = metadata
        txt = ""
        if isinstance(xml_ele, list):
            for ele in xml_ele:
                txt += self._text_form_element(ele)
        else:
            txt = self._text_form_element(xml_ele)
        self.content = txt

    def __str__(self) -> str:
        """Returns a string representation of the PdfBlock.

        Returns
        -------
        str
            The string representation.
        """
        return _str_blocks(self)


class TextBlock:
    """Represents a processed text block derived from a PdfBlock.

    Attributes
    ----------
    type_block : Enum
        The type of the text block.
    metadata : dict
        Additional metadata associated with the block.
    content : str
        The textual content of the block.
    pdf_block : PdfBlock
        The original PdfBlock this text was derived from.
    """

    type_block: Enum
    metadata: dict
    content: str
    pdf_block: PdfBlock

    def __init__(self, type_block: Enum, metadata: dict, pdf_block: PdfBlock):
        """Initializes a TextBlock instance.

        Parameters
        ----------
        type_block : Enum
            The type of the text block.
        metadata : dict
            Additional metadata for the block.
        pdf_block : PdfBlock
            The source PdfBlock.
        """
        self.type_block = type_block
        self.metadata = metadata
        self.pdf_block = pdf_block
        self.content = pdf_block.content

    def __str__(self) -> str:
        """Returns a string representation of the TextBlock.

        Returns
        -------
        str
            The string representation.
        """
        return _str_blocks(self)

    def __eq__(self, other):
        """Compares two TextBlock instances for equality.

        Args
        ----
        other : TextBlock
            The other TextBlock to compare with.

        Returns
        -------
        bool
            True if the blocks are equal, False otherwise.
        """
        equal = _eq_blocks(self, other)
        equal = equal and self.pdf_block == other.pdf_block
        return equal


def pdf_filter_exec(
    batch_pages: List[str],
    i_batch_page: int,
    n_pages: int,
    pdf_filter_func: Callable[[List[str]], List[PdfBlock]],
) -> List[PdfBlock]:
    """Processes a PDF document through a filter function to extract relevant blocks.

    Args
    ----

    document : List[str]
        The PDF document to process as a list of xml pages.
    i_batch_page : int
        Starting page of the batch processed by the instance of `pdf_filter_exec` function,
        used for informative purposes
    n_pages : int
        Total number of pages in the document, used for informative purposes.
    pdf_filter_func : Callable[[List[str]], List[PdfBlock]]
        A function that takes an XML element and returns a list of relevant PdfBlock.

    Returns
    -------
    List[PdfBlock]
        PdfBlock objects containing the filtered content.
    """
    batch_results = []
    logger.propagate = False
    std_err_log = log.StreamHandler()
    page_format_log = LogFormatterWithPage(logger.parent.handlers[0].formatter)
    std_err_log.setFormatter(page_format_log)
    logger.addHandler(std_err_log)

    for page_number, page in enumerate(batch_pages, start=i_batch_page + 1):
        page_format_log.page = page_number
        if (page_number + i_batch_page) % (n_pages // min(10, n_pages)) == 0:
            logger.info(_("Still filtering..."))

        for r in pdf_filter_func(page):
            r.metadata["page"] = page_number
            batch_results.append(r)
    return batch_results


def text_extract_exec(
    pdf_blocks: List[PdfBlock],
    targets: List[str],
    text_extract_func: Callable[[List[PdfBlock], List[str]], List[TextBlock]],
) -> List[TextBlock]:
    """Extracts text content from PDF blocks using a specified extraction function.

    Args
    ----
    pdf_blocks : List[PdfBlock]
        PdfBlock objects to process.
    targets : List[str]
        Target companies identified for extraction.
    text_extract_func : Callable[[List[PdfBlock], List[str]], List[TextBlock]]
        Function that processes PdfBlocks and targets into TextBlocks.

    Returns
    -------
    List[TextBlock]
        TextBlock objects containing the extracted content.
    """
    return text_extract_func(pdf_blocks, targets)


def deserialize_exec(
    text_blocks: List[TextBlock],
    targets: List[str],
    deserialize_func: Callable[
        [TextBlock, List[str]], FinancialData | PromisesResolutionContext
    ],
) -> List[FinancialData | PromisesResolutionContext]:
    """Converts TextBlocks into tabular data using a specified function that
    from an expected formatting, return a python object.

    Args
    ----
    text_blocks : List[TextBlock]
        TextBlock objects to process.
    targets : List[str]
        Targets companies to validate the object creation
    deserialize_func : Callable[[TextBlock, List[str]], FinancialData | PromisesResolutionContext]
        Function that converts a TextBlock into a finantial data class or into
        a bit of context for resolving deferred values

    Returns
    -------
    List[FinancialData | PromisesResolutionContext]
        FinantialData classes containing the deserialized data or context
        for resolving deferred values
    """
    return [deserialize_func(txtblk, targets) for txtblk in text_blocks]


class ExpectedPdfBlockNotFound(Exception):
    """Raised when a required PdfBlock is not found"""


class ExpectedTextBlockNotFound(Exception):
    """Raised when a required TextBlock is not found"""
