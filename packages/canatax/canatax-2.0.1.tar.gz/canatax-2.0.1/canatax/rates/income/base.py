from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_HALF_UP
from canatax.utils import percent_to_decimal

class BaseIncomeTaxRate(ABC):
    
    brackets: list[tuple[float|int, int | float]]

    def calculate_tax(self, income: Decimal) -> Decimal:
        """Returns the tax owed (estimate) on a given income amount."""
        tax_owed = Decimal(0)
        previous_threshold = Decimal(0)
        for rate, threshold in self.brackets:
            if income > threshold:
                tax_owed += (Decimal(threshold) - Decimal(previous_threshold)) * percent_to_decimal(rate)
                previous_threshold = threshold
            else:
                tax_owed += (income - Decimal(previous_threshold)) * percent_to_decimal(rate)
                break
        return tax_owed.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @classmethod
    def get_bpa(cls, income: Decimal) -> Decimal:
        if hasattr(cls, "BPA") and not hasattr(cls, "_BPA_MIN") and not hasattr(cls, "_BPA_MAX"):
            return getattr(cls, "BPA")
        elif hasattr(cls, "_BPA_MIN") and hasattr(cls, "_BPA_MAX"):
            raise NotImplementedError(f"{cls.__name__} has a BPA (basic personal amount) range. It must implement its own calculation for BPA.")
        else:
            raise NotImplementedError(f"{cls.__name__} missing BPA (basic personal amount) information.")


class ProvincialIncomeTaxRate(BaseIncomeTaxRate):
    ...


class BaseContribution:

    rate = 0
    max_earnings = 0
    
    @property
    def rate_decimal(self) -> Decimal:
        return Decimal(self.rate / 100)
