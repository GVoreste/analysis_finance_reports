"""Utils for creating deserialize routines and functions"""

from logging import getLogger
from typing import List, Callable, TypeAlias
from datetime import date, datetime
import re
from freeports_analysis.formats import TextBlock
from freeports_analysis.consts import Bond, Equity, Currency
from freeports_analysis.i18n import _
from .text_extract import EquityBondTextBlockType
from . import normalize_word, overwrite_if_implemented, normalize_string

logger = getLogger(__name__)

DeserializeFunc: TypeAlias = Callable[[TextBlock], Equity | Bond]


def perc_to_float(perc: str, norm: bool = True) -> float:
    """Convert a percentage string to float value.

    Handles various percentage string formats by:
    - Normalizing the string (removing spaces, converting commas to dots)
    - Removing percentage signs (if percentage sign is present,
      the number gets normalized dividing by 100)
    - Optionally converting to decimal form (dividing by 100)

    Parameters
    ----------
    perc : str
        The percentage string to convert (may contain '%', ',', or '.')
    norm : bool, optional
        Whether to normalize the result by dividing by 100 (default True)
        If False, returns the raw numeric value from the string

    Returns
    -------
    float
        The converted float value

    Raises
    ------
    ValueError
        If the string cannot be converted to a float after processing
    """
    perc = normalize_word(perc)

    # Handle percentage sign
    if "%" in perc:
        perc = perc.replace("%", "")
        perc = normalize_word(perc)
        if not norm:
            logger.warning(
                _(
                    "Found percentage symbol '%' but `norm` is False - forcing normalization"
                )
            )
        norm = True

    try:
        f = to_float(perc)
        return f / 100.0 if norm else f
    except ValueError as e:
        logger.exception(_("Failed to convert percentage string '%s' to float"), perc)
        raise e


def _force_numeric(data: str) -> str:
    reg_num = r"^\d+([\.,]\d+)*$"
    data = normalize_word(data)
    if not re.match(reg_num, data):
        logger.warning(
            _("Trying to cast to number but found '%s' - forcing cast"), data
        )
        data = re.sub(r"[^a-zA-Z.,0-9]+", "", data)
    return data


def to_float(data: str) -> float:
    """Cast to float in a more loose way than the standard python `float`
    namely it removes dots or commas and spaces around the string and handles
    thousand separators.

    Parameters
    ----------
    data : str
        number written in string form

    Returns
    -------
    float
        casted result

    Raises
    ------
    ValueError
        the resulting processed string cannot be casted to `float`
    """
    data = normalize_word(data)
    data = _force_numeric(data)
    pos_dot = data.find(".")
    pos_com = data.find(",")
    if pos_dot != -1 and pos_com != -1:
        first_pos = min(pos_dot, pos_com)
        data = data.replace(data[first_pos], "")

    data = data.replace(",", ".")
    int_reg = r"^[1-9]\d{0,2}\.\d{3}(\.\d{3})+$"
    if re.match(int_reg, data):
        data = data.replace(".", "")
    return float(data)


def to_int(data: str) -> int:
    """Cast to int in a more loose way than the standard python `int`
    namely it remove dots or commas and spaces around the string

    Parameters
    ----------
    data : str
        number written in string form

    Returns
    -------
    int
        casted result

    Raises
    ------
    ValueError
        the resulting processed string cannot be casted to `int`
    """
    data = normalize_word(data)
    data = _force_numeric(data)
    pos_dot = data.find(".")
    pos_com = data.find(",")
    if pos_dot != -1 and pos_com != -1:
        first_pos = min(pos_dot, pos_com)
        data = data.replace(data[first_pos], "")

    data = data.replace(",", ".")
    int_reg = r"^[1-9]\d{0,2}(\.\d{3})+$"
    if re.match(int_reg, data):
        data = data.replace(".", "")

    pos_dot = data.find(".")
    if pos_dot != -1:
        mantissa = int(data[pos_dot + 1 :])
        if mantissa != 0:
            raise ValueError(
                _("Number {} has a mantissa different form 0").format(data)
            )
        data = data[:pos_dot]
    return int(data)


def to_str(data: str) -> str:
    """Normalize a string by stripping whitespace from both ends.

    Parameters
    ----------
    data : str
        The input string to be normalized

    Returns
    -------
    str
        The stripped string
    """

    return normalize_string(data, lower=False)


def to_currency(data: str) -> Currency:
    """Convert a string to a Currency enum value.

    Parameters
    ----------
    data : str
        The currency string to convert (e.g. "USD", "EUR")

    Returns
    -------
    Currency
        The corresponding Currency enum value

    Raises
    ------
    KeyError
        If the string doesn't match any Currency enum member
    """
    data = normalize_word(data)
    data = data.upper()
    return Currency[data]


def to_date(data: str) -> date:
    """Convert a date string to a date object using multiple possible formats.

    Parameters
    ----------
    data : str
        The date string to parse

    Returns
    -------
    date
        The parsed date object

    Raises
    ------
    ValueError
        If the string doesn't match any of the supported date formats
    """
    data = normalize_word(data)
    formats = [
        "%Y-%m-%d",  # 2025-07-02
        "%d/%m/%Y",  # 02/07/2025
        "%d/%m/%y",  # 02/07/25
        "%m-%d-%Y",  # 07-02-2025
        "%d-%m-%y",  # 01-05-25
    ]
    for fmt in formats:
        try:
            return datetime.strptime(data, fmt).date()
        except ValueError:
            continue
    raise ValueError(_("Date string '{}' is not in a recognized format.").format(data))


def standard_deserialization(
    cost_and_value_interpret_int=True, quantity_interpret_float=False
) -> Callable[[DeserializeFunc], DeserializeFunc]:
    """Decorator factory that creates a deserializer function for TextBlock metadata.

    The resulting decorator transforms a TextBlock's metadata into a financial data object.

    Parameters
    ----------
    cost_and_value_interpret_int : bool
        interpret market value and acquisition cost column as int before casting to float
    quantity_interpret_float : bool
        interpret quantity column as int before casting to int

    Returns
    -------
    Callable[[DeserializeFunc],DeserializeFunc]
        Decorator to wrap the deserializer functions
    """

    def wrapper(f):
        @overwrite_if_implemented(f)
        def default_other_txt_blk_deserializer(
            blk: TextBlock, targets: List[str]
        ) -> Bond | Equity:
            raise ValueError(
                _("Expected bond or equity text blocks, found {}").format(
                    blk.type_block.__name__
                )
            )

        def deserialize(blk: TextBlock, targets: List[str]) -> Bond | Equity:
            """Transform TextBlock metadata into a typed dictionary.

            Parameters
            ----------
            blk : TextBlock
                The text block containing metadata to deserialize
            targets : List[str]
                List of target companies used as validation when initializing
                the financial data object

            Returns
            -------
            Bond | Equity
                Finantial data deserialized from text block
            """
            if blk is None:
                logger.error(_("Something wrong happened, text block is None..."))
            md = blk.metadata

            def float_cast(x):
                if cost_and_value_interpret_int:
                    return float(to_int(x))
                return to_float(x)

            def int_cast(x):
                if quantity_interpret_float:
                    return int(to_float(x))
                return to_int(x)

            try:
                ac = (
                    float_cast(md["acquisition cost"])
                    if "acquisition cost" in md
                    else None
                )
                args = {
                    "page": md["page"],
                    "targets": targets,
                    "company": to_str(md["company"]),
                    "subfund": to_str(md["subfund"]),
                    "nominal_quantity": int_cast(md["quantity"]),
                    "market_value": float_cast(md["market value"]),
                    "currency": to_currency(md["currency"]),
                    "perc_net_assets": perc_to_float(md["% net assets"]),
                    "acquisition_cost": ac,
                }
                if blk.type_block == EquityBondTextBlockType.EQUITY_TARGET:
                    return Equity(**args)
                if blk.type_block == EquityBondTextBlockType.BOND_TARGET:
                    return Bond(
                        **args,
                        maturity=to_date(md["maturity"]) if "maturity" in md else None,
                        interest_rate=perc_to_float(md["interest rate"])
                        if "interest rate" in md
                        else None,
                    )
                return default_other_txt_blk_deserializer(blk, targets)
            except ValueError as e:
                logger.error(_("Cast error in company %s"), md["company"])
                logger.exception(str(e))
                logger.warning(_("Skipping page"))

        return deserialize

    return wrapper
