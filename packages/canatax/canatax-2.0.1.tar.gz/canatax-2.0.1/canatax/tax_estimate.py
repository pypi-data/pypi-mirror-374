from dataclasses import dataclass, asdict
from decimal import Decimal
from typing import Any
from canatax.enums import ProvinceOrTerritory
from canatax.utils import to_currency


@dataclass
class BaseTaxEstimate:
    
    province: ProvinceOrTerritory

    def _prettify(self, d:dict[str, Any]) -> dict[str,Any]:
        d2 = {}
        for k, v in d.items():
            if isinstance(v, Decimal):
                d2[k] = to_currency(v)
            elif isinstance(v, ProvinceOrTerritory):
                d2[k] = v.value
            else:
                d2[k] = v
        return d2

    def to_dict(self, prettify:bool=False) -> dict[str, Any]:
        """Convert the object's attributes to a dictionary representation.

        Args:
            prettify (bool): If True, applies formatting to the dictionary values.
                            - Floats are formatted as currency strings.
                            - `ProvinceOrTerritory` enum values are converted to their string representation.
                            Defaults to False.

        Returns:
            dict[str, Any]: A dictionary containing the object's attributes. 
                            If `prettify` is True, the dictionary values are formatted accordingly.
        """
        d = asdict(self)
        if prettify:
            d = self._prettify(d)
        return d
    

@dataclass
class SalesTaxEstimate(BaseTaxEstimate):
    
    before_tax: Decimal
    gst: Decimal
    pst: Decimal
    hst: Decimal
    qst: Decimal
    tax_total: Decimal
    after_tax: Decimal


@dataclass
class IncomeTaxEstimate(BaseTaxEstimate):
    
    gross_income: Decimal
    federal_tax: Decimal
    provincial_tax: Decimal
    cpp: Decimal
    ei: Decimal
    qpip: Decimal
    qpp: Decimal
    total_tax: Decimal
    net_income: Decimal