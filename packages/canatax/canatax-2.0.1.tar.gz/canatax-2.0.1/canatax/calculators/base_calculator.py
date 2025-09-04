from abc import ABC
from decimal import Decimal, InvalidOperation
from typing import Type

from canatax.enums import *
from canatax.exc import InvalidProvinceError, InvalidDollarAmount
from canatax.rates.income.current_tax import *
from canatax.rates.sales.current_sales_tax import *



class BaseCalculator(ABC):

    province: ProvinceOrTerritory

    PROVINCE_MAPPING: dict[
        ProvinceOrTerritory, tuple[Type[ProvincialIncomeTaxRate], Type[BaseSalesTaxRate]]
    ] = {
        ProvinceOrTerritory.ALBERTA : (AlbertaIncomeTaxRate, AlbertaSalesTaxRate),
        ProvinceOrTerritory.BRITISH_COLUMBIA: (BritishColumbiaIncomeTaxRate, BritishColumbiaSalesTaxRate),
        ProvinceOrTerritory.MANITOBA : (ManitobaIncomeTaxRate, ManitobaSalesTaxRate), 
        ProvinceOrTerritory.ONTARIO : (OntarioIncomeTaxRate, OntarioSalesTaxRate),
        ProvinceOrTerritory.NEW_BRUNSWICK : (NewBrunswickIncomeTaxRate, NewBrunswickSalesTaxRate),
        ProvinceOrTerritory.NEWFOUNDLAND : (NewfoundlandIncomeTaxRate, NewfoundlandSalesTaxRate),
        ProvinceOrTerritory.NORTHWEST_TERRITORIES : (NorthwestTerritoriesIncomeTaxRate, NorthwestTerritoriesSalesTaxRate),
        ProvinceOrTerritory.NOVA_SCOTIA : (NovaScotiaIncomeTaxRate, NovaScotiaSalesTaxRate),
        ProvinceOrTerritory.NUNAVUT : (NunavutIncomeTaxRate, NunavutSalesTaxRate),
        ProvinceOrTerritory.PRINCE_EDWARD_ISLAND: (PEIIncomeTaxRate, PEISalesTaxRate),
        ProvinceOrTerritory.QUEBEC: (QuebecIncomeTaxRate, QuebecSalesTaxRate),
        ProvinceOrTerritory.SASKATCHEWAN : (SaskatchewanIncomeTaxRate, SaskatchewanSalesTaxRate),
        ProvinceOrTerritory.YUKON : (YukonIncomeTaxRate, YukonSalesTaxRate),
    }

    def __init__(self, province: str | ProvinceOrTerritory):
        """Initializes the calculator with a province or territory.

        Args:
            province (str | ProvinceOrTerritory): The province or territory as a string or an enum.

        Raises:
            InvalidProvinceError: If the province or territory is not valid.
        """
        self.province = self._coerce_province(province)
        
        
    def _coerce_province(self, province: str | ProvinceOrTerritory) -> ProvinceOrTerritory:
        if not isinstance(province, ProvinceOrTerritory):
            try:
                return ProvinceOrTerritory(province.upper())
            except ValueError as e:
                raise InvalidProvinceError(province) from e

        return province

    def _decimalize(self, amount:int|float|Decimal) -> Decimal:
        try:
            decimal_amount = Decimal(amount)
        except (ValueError, TypeError, InvalidOperation) as e:
            raise InvalidDollarAmount(amount) from e
        else:
            if decimal_amount.is_infinite() or decimal_amount.is_nan():
                raise InvalidDollarAmount(amount)
            if decimal_amount < 0:
                raise InvalidDollarAmount(amount)
        return decimal_amount

    def is_quebec(self) -> bool:
        match self.province:
            case ProvinceOrTerritory.QUEBEC:
                return True
            case _:
                return False

    def _get_tax_rate(self, tax_type:TaxType) -> ProvincialIncomeTaxRate | BaseSalesTaxRate:
        tax_rate_tuple = self.PROVINCE_MAPPING[self.province]
        match tax_type:
            case TaxType.INCOME:
                return tax_rate_tuple[0]()
            case TaxType.SALES:
                return tax_rate_tuple[1]()
            case _:
                raise ValueError(f"Invalid param tax_type: `{tax_type}` ")

#  (AlbertaIncomeTaxRate, AlbertaSalesTaxRate),