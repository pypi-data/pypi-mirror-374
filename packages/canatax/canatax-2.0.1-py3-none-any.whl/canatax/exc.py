from typing import Any
from canatax.enums import ProvinceOrTerritory

class CanataxError(Exception):
    """Base class to all Canatax related errors."""
    pass


class InvalidProvinceError(CanataxError):
    """Raised when ProvinceOrTerritory enum is passed an invalid value."""
    def __init__(self, province:str|ProvinceOrTerritory):
        message = f"Invalid province or territory: `{province}`. Value must be two-letter string: AB,BC,MB,NB,NL,NS,NT,NU,ON,PE,QC,SK,YK."
        super().__init__(message)


class InvalidDollarAmount(CanataxError):
    """Raised when an invalid amount is passed to a tax calculator."""
    def __init__(self, amount:Any):
        message = f"Invalid dollar amount `{amount}`"
        super().__init__(message)