"""Provide basic constant and types used by all submodules,
should facilitate avoiding circular imports
"""

from abc import ABC, abstractmethod
import datetime
from enum import Enum, auto
from typing import List, TypeAlias, Any
import logging as log
import importlib

import yaml
from importlib_resources import files
from freeports_analysis import data
from freeports_analysis.i18n import _
from freeports_analysis.i18n import _


logger = log.getLogger(__name__)
STANDARD_LOG_FORMATTER = log.Formatter("%(levelname)s %(name)s: %(message)s")
STANDARD_LOG_FORMATTER_MP = log.Formatter(
    "%(levelname)s[%(process)d] %(name)s: %(message)s"
)
STANDARD_LOG_FORMATTER = log.Formatter("%(levelname)s %(name)s: %(message)s")
STANDARD_LOG_FORMATTER_MP = log.Formatter(
    "%(levelname)s[%(process)d] %(name)s: %(message)s"
)

ENV_PREFIX = "AFINANCE_"


# Leggi il file YAML
YAML_DATA = None
with files(data).joinpath("format_url_mapping.yaml").open("r") as f:
    YAML_DATA = yaml.safe_load(f)

PdfFormats = Enum(
    "PdfFormats", {k: v if v is not None else [] for k, v in YAML_DATA.items()}
)


class FinancialInstrument(Enum):
    """Enumeration of financial instrument types."""

    EQUITY = auto()
    BOND = auto()


class Currency(Enum):
    """Enumeration of supported currency codes.

    Contains standard 3-letter ISO currency codes for major world currencies.
    """

    USD = "$"
    EUR = "€"
    GBP = "£"
    JPY = "¥"
    CNY = "¥"
    AUD = "$"
    CAD = "$"
    CHF = "CHF"
    SEK = "kr"
    NOK = "kr"
    DKK = "kr"
    SGD = "$"
    HKD = "$"
    KRW = "₩"
    INR = "₹"
    BRL = "R$"
    MXN = "$"
    RUB = "₽"
    ZAR = "R"
    TRY = "₺"
    PLN = "zł"
    THB = "฿"
    IDR = "Rp"
    MYR = "RM"
    PHP = "₱"
    ILS = "₪"
    AED = "د.إ"
    SAR = "﷼"
    QAR = "ر.ق"
    KWD = "د.ك"
    CLP = "$"
    COP = "$"
    PEN = "S/."
    ARS = "$"
    VND = "₫"
    UAH = "₴"
    CZK = "Kč"
    HUF = "Ft"
    RON = "lei"
    HRK = "kn"
    BGN = "лв"
    ISK = "kr"
    NZD = "$"


PromisesResolutionMap: TypeAlias = dict
PromisesResolutionContext: TypeAlias = dict


class Promise:
    """Base class for deferred value resolution in financial data processing.
    Implements a promise pattern where values can be resolved later from a mapping.
    Attributes
    ----------
    id : str
        The key used to lookup the promised value in the resolution mapping.
    Methods
    -------
    fulfill_with(mapping: PromisesResolutionMap) -> Any
        Resolves the promised value from the given mapping.
    """

    def __init__(self, ID: str):
        """Initialize a Promise with the given lookup ID.
        Parameters
        ----------
        ID : str
            The key to use when resolving this promise from a mapping.
        """
        self._id = ID

    @property
    def id(self) -> str:
        """str: The lookup key for this promise."""
        return self._id

    def fulfill_with(self, mapping: PromisesResolutionMap) -> Any:
        """Resolve this promise's value from the given mapping.
        Parameters
        ----------
        mapping : PromisesResolutionMap
            Dictionary containing values to resolve promises from.
        Returns
        -------
        Any
            The resolved value from the mapping.
        """
        return mapping[self.id]

    def __str__(self) -> str:
        """str: String representation showing promise class and ID."""
        return f'{self.__class__.__name__}("{self.id}")'


class CompanyPromise(Promise):
    """Promise for resolving company names in financial data."""


class SubfundPromise(Promise):
    """Promise for resolving subfund names in financial data."""


class CurrencyPromise(Promise):
    """Promise for resolving currency values in financial data."""


class NominalQuantityPromise(Promise):
    """Promise for resolving nominal quantity values in financial data."""


class MarkedValuePromise(Promise):
    """Promise for resolving marked value amounts in financial data."""


class PercNetAssetsPromise(Promise):
    """Promise for resolving percentage of net assets values."""


class AcquisitionCostPromise(Promise):
    """Promise for resolving acquisition cost values."""


class MaturityPromise(Promise):
    """Promise for resolving maturity dates in bond instruments."""


class InterestRatePromise(Promise):
    """Promise for resolving interest rate values in bond instruments."""


class CircularPromisesChain(Exception):
    """Exception raised when a circular dependency is detected in promise resolution.
    This occurs when a promise chain references itself either directly or indirectly,
    creating an infinite loop that cannot be resolved.
    """


def flatten_promise_map(mapping: PromisesResolutionMap) -> PromisesResolutionMap:
    """Flatten a mapping containing Promise objects by resolving all references.
    Processes a dictionary that may contain Promise objects, resolving each promise
    by looking up its value in the mapping until all values are concrete (non-Promise).
    Detects and prevents circular references that would cause infinite resolution loops.
    Parameters
    ----------
    mapping : PromisesResolutionMap
        Dictionary containing both direct values and Promise objects to be resolved.
    Returns
    -------
    PromisesResolutionMap
        A new dictionary with all Promise objects resolved to their final values.
    Raises
    ------
    CircularPromisesChain
        If a circular reference is detected in the promise resolution chain.
    """
    flattened = {}
    resolve_history = {}
    promises = []

    # Initial pass: separate promises from concrete values
    for key, value in mapping.items():
        if isinstance(value, Promise):
            promises.append(key)
            resolve_history[key] = []
        else:
            flattened[key] = value
    if len(promises) == 0:
        return flattened

    # Process promises until all are resolved
    while True:
        i = 0
        while True:
            p = promises[i]
            value = mapping[p]
            if not isinstance(value, Promise):
                # Found concrete value - add to flattened and remove from processing
                flattened[p] = value
                promises.pop(i)
            else:
                # Check for circular reference
                if value.id in resolve_history[p]:
                    _debug_str = f"{resolve_history[p]} -> {value.id}"
                    raise CircularPromisesChain(
                        _("Circular reference detected in promise resolution chain: ")
                        + _debug_str
                    )

                # Track resolution path and follow the reference
                resolve_history[p].append(value.id)
                mapping[p] = mapping[value.id]
                i += 1
            if i >= len(promises):
                break

        if len(promises) == 0:
            break

    return flattened


class FinancialData(ABC):
    """Abstract base class representing financial data.

    This class serves as the foundation for specific financial instrument types,
    providing common attributes and validation.

    Attributes
    ----------
    page : int
        The page number where the financial data appears (must be positive).
    targets: List[str]
        The list of companies to search for, used as company validation
    company : str | CompanyPromise
        The name of the company or issuer.
    market_value : float | MarketValuePromise
        The current market value of the instrument.
    currency : Currency | CurrencyPromise
        The currency in which the value is denominated.
    perc_net_assets : float | PercNetAssetsPromise
        Percentage of net assets (must be between 0 and 1).
    subfund : str | SubfundPromise
        The subfund to which this instrument belongs.
    nominal_quantity : int | NominalQuantityPromise , optional
        The nominal quantity of the instrument, if applicable.
    acquisition_cost : float | AcquisitionCostPromise , optional
        The original acquisition cost of the instrument.

    Raises
    ------
    ValueError
        If perc_net_assets is not between 0 and 1.
        If page is not a positive number.
        If company is not in targets.
        If company is not in targets.
    """

    def __init__(
        self,
        page: int,
        targets: List[str],
        company: str | CompanyPromise,
        subfund: str | SubfundPromise,
        nominal_quantity: int | NominalQuantityPromise,
        market_value: float | MarkedValuePromise,
        currency: Currency | CurrencyPromise,
        perc_net_assets: float | PercNetAssetsPromise,
        acquisition_cost: float | AcquisitionCostPromise = None,
    ):
        if not page > 0:
            raise ValueError(_("page should be a positive number, not {}").format(page))
        if not isinstance(perc_net_assets, PercNetAssetsPromise):
            self._validate_perc_net_assets(perc_net_assets)
        if not isinstance(company, CompanyPromise):
            self._validate_company(company, targets)

        self._company = company
        self._page = page
        self._market_value = market_value
        self._currency = currency
        self._perc_net_assets = perc_net_assets
        self._subfund = subfund
        self._nominal_quantity = nominal_quantity
        self._acquisition_cost = acquisition_cost

    @property
    @abstractmethod
    def instrument(self) -> FinancialInstrument:
        """Abstract property to identify the financial instrument type.
        Returns
        -------
        FinancialInstrument
            The type of financial instrument (EQUITY, BOND, etc.)
        """

    @property
    def page(self) -> int:
        """int: The page number where the financial data appears."""
        return self._page

    @property
    def perc_net_assets(self) -> float:
        """float: Percentage of net assets (between 0 and 1)."""
        return self._perc_net_assets

    @property
    def company(self) -> str:
        """str: The name of the company or issuer."""
        return self._company

    @property
    def market_value(self) -> float:
        """float: The current market value of the instrument."""
        return self._market_value

    @property
    def currency(self) -> Currency:
        """Currency: The currency in which the value is denominated."""
        return self._currency

    @property
    def subfund(self) -> str:
        """str: The subfund to which this instrument belongs."""
        return self._subfund

    @property
    def nominal_quantity(self) -> int:
        """int or None: The nominal quantity of the instrument, if applicable."""
        return self._nominal_quantity

    @property
    def acquisition_cost(self) -> float:
        """float or None: The original acquisition cost of the instrument."""
        return self._acquisition_cost

    def _validate_perc_net_assets(self, perc_net_assets: float):
        if not 0.0 <= perc_net_assets <= 1.0:
            raise ValueError(
                _("perc_net_assets must be between 0 and 1, not {}").format(
                    perc_net_assets
                )
            )

    def _validate_company(self, company: str, targets: List[str]):
        if company not in targets:
            raise ValueError(
                _("company should be between targets, not {}").format(company)
            )

    def fulfill_promises(
        self, mapping: PromisesResolutionMap, targets: List[str]
    ) -> None:
        """Resolve all promise objects in this financial data instance.

        Processes each attribute that may contain a Promise object, resolving it
        using the provided mapping and performing validation where required.

        Parameters
        ----------
        mapping : PromisesResolutionMap
            Dictionary containing values to resolve promises from.
        targets : List[str]
            List of valid company names for validation.

        Notes
        -----
        For attributes that require validation (perc_net_assets, company),
        the resolved values will be validated before assignment.
        """
        if isinstance(self._subfund, SubfundPromise):
            self._subfund = self._subfund.fulfill_with(mapping)

        if isinstance(self._currency, CurrencyPromise):
            self._currency = self._currency.fulfill_with(mapping)

        if isinstance(self._nominal_quantity, NominalQuantityPromise):
            self._nominal_quantity = self._nominal_quantity.fulfill_with(mapping)

        if isinstance(self._acquisition_cost, AcquisitionCostPromise):
            self._acquisition_cost = self._acquisition_cost.fulfill_with(mapping)

        if isinstance(self._market_value, MarkedValuePromise):
            self._market_value = self._market_value.fulfill_with(mapping)

        if isinstance(self._perc_net_assets, PercNetAssetsPromise):
            perc_net_assets = self._perc_net_assets.fulfill_with(mapping)
            self._validate_perc_net_assets(perc_net_assets)
            self._perc_net_assets = perc_net_assets
        if isinstance(self._company, CompanyPromise):
            company = self._company.fulfill_with(mapping)
            self._validate_company(company, targets)
            self._company = company

    def to_dict(self) -> dict:
        """Cast financial data to python dictionary

        Returns
        -------
        dict
            casted data
        """
        return {
            "Page report": self.page,
            "Company": self.company,
            "Financial instrument": self.instrument.name,
            "Sub-fund": self.subfund,
            "Nominal/Quantity": self.nominal_quantity,
            "Market value": self.market_value,
            "Currency": self.currency.name,
            "% Net Assets": self.perc_net_assets,
            "Acquisition cost": self.acquisition_cost,
            "Maturity": None,
            "Interest rate": None,
        }

    def _str_additional_infos(self) -> str:
        string = ""
        if self.acquisition_cost is not None:
            translated_field = _("Acquisition cost")
            string += f"\t\t{translated_field}:\t{self.acquisition_cost:.2f}{self.currency.value}\n"
        return string

    def __str__(self) -> str:
        string = f"{self.__class__.__name__}:\n"
        translated_field = _("Type match")
        string += f"\t{translated_field}:\t{self.instrument.name}\t(pag. {self.page})\n"
        translated_field = _("Subfund")
        string += f"\t{translated_field}:\t{self.subfund}\n"
        translated_field = _("Company")
        string += f"\t{translated_field}:\t{self.company}\n"
        translated_field = _("Currency")
        string += f"\t{translated_field}:\t{self.currency.name}\n"
        translated_field = _("Market value")
        string += f"\t{translated_field}:\t{self.market_value:.2f}{self.currency.value}"
        translated_field = _("of net assets")
        string += f"\t({self.perc_net_assets:.3%} {translated_field})\n"
        translated_field = _("Quantity")
        string += f"\t{translated_field}:\t{self.nominal_quantity}\n"
        translated_field = _("Additional infos")
        string += f"\t{translated_field}: {{"
        add_string = self._str_additional_infos()
        if add_string != "":
            string += "\n" + add_string + "\t"
        string += "}\n"
        return string

    def __eq__(self, other) -> bool:
        eq = True
        eq = eq and self.instrument == other.instrument
        eq = eq and self.page == other.page
        eq = eq and self.subfund == other.subfund
        eq = eq and self.currency == other.currency
        eq = eq and self.market_value == other.market_value
        eq = eq and self.perc_net_assets == other.perc_net_assets
        eq = eq and self.nominal_quantity == other.nominal_quantity
        eq = eq and self.acquisition_cost == other.acquisition_cost
        eq = eq and self.company == other.company
        return eq


class Equity(FinancialData):
    """Concrete class representing equity financial instruments.

    Inherits from FinancialData and implements the instrument property
    to identify as EQUITY type.
    """

    @property
    def instrument(self) -> FinancialInstrument:
        """FinancialInstrument: Identifies this instrument as EQUITY type.

        Returns
        -------
        FinancialInstrument
            Always returns FinancialInstrument.EQUITY
        """
        return FinancialInstrument.EQUITY


class Bond(FinancialData):
    """Concrete class representing bond financial instruments.

    Extends FinancialData with bond-specific attributes including maturity date
    and interest rate.

    Attributes
    ----------
    maturity : datetime.date, optional
        The maturity date of the bond.
    interest_rate : float, optional
        The interest rate of the bond (should be between 0 and 1).
    """

    def __init__(
        self,
        page: int,
        targets: List[str],
        company: str,
        subfund: str,
        nominal_quantity: int,
        market_value: float,
        currency: Currency,
        perc_net_assets: float,
        acquisition_cost: float = None,
        maturity: datetime.date = None,
        interest_rate: float = None,
    ) -> None:
        """Initialize a Bond financial instrument.

        Parameters
        ----------
        page : int
            The page number where the bond appears.
        targets: List[str]
            The list of companies to search for, used as company validation
        company : str
            The issuer of the bond.
        market_value : float
            Current market value of the bond.
        currency : Currency
            Currency denomination.
        perc_net_assets : float
            Percentage of net assets (0-1).
        subfund : str
            Associated subfund.
        nominal_quantity : int, optional
            Nominal quantity of bonds.
        acquisition_cost : float, optional
            Original acquisition cost.
        maturity : datetime.date, optional
            Bond maturity date.
        interest_rate : float, optional
            Bond interest rate (0-1).
        """
        super().__init__(
            page,
            targets,
            company,
            subfund,
            nominal_quantity,
            market_value,
            currency,
            perc_net_assets,
            acquisition_cost,
        )
        self._maturity = maturity
        if interest_rate is not None and not 0.0 <= interest_rate <= 1.0:
            logger.warning(
                _(
                    "Interest rate of bond in not between 0 and 1, maybe should be normalized?"
                )
            )
        self._interest_rate = interest_rate

    @property
    def maturity(self) -> datetime.date:
        """datetime.date or None: The maturity date of the bond."""
        return self._maturity

    @property
    def interest_rate(self) -> float:
        """float or None: The interest rate of the bond.

        Returns
        -------
        float
            The interest rate value

        Notes
        -----
        Logs a warning if interest rate is not normalized (0-1 range).
        """
        return self._interest_rate

    @property
    def instrument(self) -> FinancialInstrument:
        """FinancialInstrument: Identifies this instrument as BOND type.

        Returns
        -------
        FinancialInstrument
            Always returns FinancialInstrument.BOND
        """
        return FinancialInstrument.BOND

    def to_dict(self):
        row = super().to_dict()
        row["Maturity"] = self.maturity
        row["Interest rate"] = self.interest_rate
        return row

    def _str_additional_infos(self) -> str:
        string = super()._str_additional_infos()
        translated_maturity = _("Maturity")
        translated_interest_rate = _("Interest rate")
        if self.maturity is not None and self.interest_rate is not None:
            string += f"\t\t{translated_maturity}:\t\t{self.maturity} +{self.interest_rate:.3%}\n"
        elif self.maturity is not None:
            string += f"\t\t{translated_maturity}:\t\t{self.maturity}\n"
        elif self.interest_rate is not None:
            string += f"\t\t{translated_interest_rate}:\t{self.interest_rate:.3%}\n"
        return string

    def __eq__(self, other):
        eq = super().__eq__(other)
        eq = eq and self.maturity == other.maturity
        eq = eq and self.interest_rate == other._interest_rate
        return eq


def _get_module(module_name: str):
    try:
        module = importlib.import_module(
            f"freeports_analysis.formats.{module_name.lower()}", package=__package__
        )
    except ImportError:
        logger.error(
            _("Module {} ({}) not found").format(module_name.lower(), module_name)
        )
        logger.error(
            _("Module {} ({}) not found").format(module_name.lower(), module_name)
        )
        raise
    return module
