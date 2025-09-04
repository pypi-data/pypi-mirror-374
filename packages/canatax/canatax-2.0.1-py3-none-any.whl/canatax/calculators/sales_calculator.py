from decimal import Decimal, ROUND_HALF_UP
from canatax.calculators.base_calculator import BaseCalculator
from canatax.exc import CanataxError
from canatax.enums import ProvinceOrTerritory, TaxType
from canatax.rates.income.current_tax import ProvincialIncomeTaxRate
from canatax.rates.sales.current_sales_tax import BaseSalesTaxRate
from canatax.tax_estimate import SalesTaxEstimate
from canatax.utils import percent_to_decimal, decimal_round


class SalesTaxCalculator(BaseCalculator):

    def __init__(self, province: ProvinceOrTerritory | str):
        super().__init__(province=province)
        self.tax_rate = self._get_tax_rate(TaxType.SALES)

    def _get_tax_rate(self, tax_type: TaxType) -> BaseSalesTaxRate:
        tax_rate = super()._get_tax_rate(tax_type)
        if isinstance(tax_rate, BaseSalesTaxRate):
            return tax_rate
        raise CanataxError(f"{self.__class__.__name__} failed to load tax rate")

    def _calculate(self, amount: float | int | Decimal) -> SalesTaxEstimate:
        """Calculate sales tax for a given amount based on the tax rates for the initialized province or territory.

        This method calculates the GST, PST, and HST based on the provided amount and the applicable tax rates
        for the current province or territory. It raises an `InvalidDollarAmount` exception if the input amount is invalid.

        Args:
            amount (float): The amount to calculate sales tax on.

        Returns:
            SalesTaxEstimate: An object containing detailed information about the calculated sales tax, including
                            GST, PST, HST, total tax, and the after-tax total.

        Raises:
            InvalidDollarAmount: If the provided amount is negative, `None`, or cannot be converted to a valid decimal.
        """
        amount = self._decimalize(amount)
        gst_total = decimal_round((amount * percent_to_decimal(self.tax_rate.GST))) if self.tax_rate.GST else Decimal('0.00')
        pst_total = decimal_round((amount * percent_to_decimal(self.tax_rate.PST))) if self.tax_rate.PST else Decimal('0.00')
        hst_total = decimal_round((amount * percent_to_decimal(self.tax_rate.HST))) if self.tax_rate.HST else Decimal('0.00')
        qst_total = decimal_round((amount * percent_to_decimal(self.tax_rate.QST))) if self.tax_rate.QST else Decimal('0.00')
        tax_total = decimal_round((gst_total + pst_total + hst_total + qst_total))
        after_tax_total = decimal_round((amount + tax_total))
        return SalesTaxEstimate(
            province=self.province,
            before_tax=amount,
            tax_total=tax_total,
            after_tax=after_tax_total,
            gst=gst_total,
            pst=pst_total,
            hst=hst_total,
            qst=qst_total,
        )

    @classmethod
    def calculate(
            cls, 
            amount: float | int | Decimal, 
            province: str | ProvinceOrTerritory,
    ) -> SalesTaxEstimate:
        calculator = cls(province=province)
        return calculator._calculate(amount)
