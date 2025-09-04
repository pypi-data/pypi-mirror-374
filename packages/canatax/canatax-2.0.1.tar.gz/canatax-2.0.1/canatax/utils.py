from decimal import Decimal, ROUND_HALF_UP


def to_currency(n:float|Decimal) -> str:
    return f"{n:,.2f}"


def percent_to_decimal(n:float|Decimal) -> Decimal:
    return Decimal(n / 100)


def decimal_round(n: float | int | Decimal):
    return Decimal(n).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
