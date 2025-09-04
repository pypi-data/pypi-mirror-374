from decimal import Decimal


class BaseSalesTaxRate:

    GST = 0
    PST = 0
    HST = 0
    QST = 0

    @property
    def rate(self) -> Decimal:
        applicable_taxes = [tax for tax in self.tax_types if tax > 0]
        if not applicable_taxes:
            raise AttributeError(f"`{self.__class__.__name__}`: GST, PST, HST, and QST are all 0!")
        return Decimal(sum(applicable_taxes))

    @property
    def tax_types(self) -> list[Decimal]:
        return [Decimal(self.GST), Decimal(self.PST), Decimal(self.HST), Decimal(self.QST)]

