from dataclasses import dataclass
from ..base import BaseContribution

# CPP:
# https://www.canada.ca/en/revenue-agency/news/newsroom/tax-tips/tax-tips-2024/canada-revenue-agency-announces-maximum-pensionable-earnings-contributions-2025.html
#
# EI & EIQuebec:
# https://www.canada.ca/en/revenue-agency/services/tax/businesses/topics/payroll/payroll-deductions-contributions/employment-insurance-ei/ei-premium-rates-maximums.html
#
# QPP:
# https://www.revenuquebec.ca/en/businesses/source-deductions-and-employer-contributions/calculating-source-deductions-and-employer-contributions/quebec-pension-plan-contributions/maximum-pensionable-salary-or-wages-and-contribution-rate/
#
# QPIP:
# https://www.quebec.ca/nouvelles/actualites/details/maintien-des-taux-de-cotisation-au-regime-quebecois-dassurance-parentale-en-2025-56294



@dataclass(frozen=True)
class EI(BaseContribution):

    rate = 1.64
    max_earnings = 65700


@dataclass(frozen=True)
class EIQuebec(EI):
    
    rate = 1.31
    
    
@dataclass(frozen=True)
class CPP(BaseContribution):

    rate = 5.95
    max_earnings = 71300
    exemption = 3500

    additional_rate = 4.00
    additional_min = 71300
    additional_max = 81200

    @property
    def additional_rate_decimal(self) -> float:
        return self.additional_rate / 100


@dataclass(frozen=True)
class QPP(CPP):

    rate = 6.40
 
    
@dataclass(frozen=True)
class QPIP(BaseContribution):
    
    max_earnings = 98000
    rate = 0.494
