# 🇨🇦 Canatax – Canadian Tax Calculator

[![PyPI - Version](https://img.shields.io/pypi/v/typed-api-response.svg)](https://pypi.org/project/canatax/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/canatax.svg)](https://pypi.org/project/canatax/)
[![Python Version](https://img.shields.io/pypi/pyversions/canatax.svg)](https://pypi.org/project/canatax/)
[![License](https://img.shields.io/pypi/l/canatax.svg)](https://github.com/yourusername/canatax/blob/main/LICENSE)

**Canatax** is a dependency-free Python package for estimating Canadian income and sales taxes. Built for developers who need quick tax calculations for applications, prototyping, or general estimation purposes.

## ⚠️ Important Disclaimer

**This software provides tax estimates only and is not professional accounting software.** I am not a licensed accountant or tax professional. While the calculations are based on current CRA guidelines and provincial tax rates, this tool should not be used as your sole source for tax planning, filing, or financial decisions.

For official tax advice, consult a qualified accountant or use CRA-approved software.

## Features

**Income Tax Estimation:**
- Federal and provincial/territorial income tax
- CPP/QPP contributions (province-specific)
- Employment Insurance (EI) premiums
- Quebec Parental Insurance Plan (QPIP) for Quebec residents
- Basic Personal Amount (BPA) calculations with high-income phase-outs
- Uses **2025 tax rates and brackets**

**Sales Tax Calculation:**
- GST, PST, HST, and QST calculations
- Automatic tax selection based on province/territory
- Structured breakdown of all applicable taxes

**Zero Dependencies:** Pure Python with no external requirements.

## Installation

```bash
pip install canatax
```

## Quick Start

### Income Tax Estimation

```python
from canatax import IncomeTaxCalculator

# Calculate tax estimate for $80,000 income in British Columbia
estimate = IncomeTaxCalculator.calculate(income=80000, province="BC")

print(f"Province: {estimate.province}")
print(f"Federal Tax: ${estimate.federal_tax:,.2f}")
print(f"Provincial Tax: ${estimate.provincial_tax:,.2f}")
print(f"CPP: ${estimate.cpp:,.2f}")
print(f"EI: ${estimate.ei:,.2f}")
print(f"Total Tax: ${estimate.total_tax:,.2f}")
print(f"Net Income: ${estimate.net_income:,.2f}")
```

### Sales Tax Calculation

```python
from canatax import SalesTaxCalculator

# Calculate sales tax for $100 purchase in Quebec
estimate = SalesTaxCalculator.calculate(amount=100.00, province="QC")

print(f"Province: {estimate.province}")
print(f"GST: ${estimate.gst:,.2f}")
print(f"QST: ${estimate.qst:,.2f}")
print(f"Total Tax: ${estimate.tax_total:,.2f}")
print(f"After Tax: ${estimate.after_tax:,.2f}")
```

## API Reference

### IncomeTaxCalculator

**`IncomeTaxCalculator.calculate(income: float, province: str) -> IncomeTaxEstimate`**

Calculates income tax estimate for the given income and province.

**Parameters:**
- `income`: Annual gross income (float)
- `province`: Two-letter province code (e.g., "ON", "BC", "QC")

**Returns:** `IncomeTaxEstimate` object with calculated taxes and deductions.

### SalesTaxCalculator

**`SalesTaxCalculator.calculate(amount: float, province: str) -> SalesTaxEstimate`**

Calculates applicable sales taxes for a purchase amount.

**Parameters:**
- `amount`: Purchase amount before tax (float)
- `province`: Two-letter province code

**Returns:** `SalesTaxEstimate` object with tax breakdown.

### Supported Provinces and Territories

All Canadian provinces and territories are supported:
- **AB, BC, MB, NB, NL, NT, NS, NU, ON, PE, QC, SK, YT**

## Use Cases

- **E-commerce applications:** Calculate tax estimates for shopping carts
- **Payroll prototyping:** Rough estimation of payroll deductions
- **Financial planning tools:** Provide ballpark tax calculations
- **Educational purposes:** Demonstrate Canadian tax system mechanics
- **Budget calculators:** Help users estimate take-home pay

## Accuracy Notes

Tax calculations are based on:
- Current CRA federal tax brackets and rates
- Provincial/territorial tax rates and basic personal amounts (BPAs)
- 2025 CPP, EI, and other contribution limits
- Published GST/PST/HST rates by province

**Limitations:**
- Does not account for tax credits beyond basic personal amounts
- Does not include deductions for RRSP, childcare, etc.
- Simplified calculation model suitable for estimation purposes
- May not reflect mid-year rate changes or special circumstances


## Contributing

Bug reports, feature requests, and contributions are welcome! This project helps developers build better financial tools for Canadians.


## License

MIT License – Free for personal and commercial use.


## Support

If this tool has been helpful for your projects, consider [buying me a coffee](https://www.buymeacoffee.com/FirstFlush). No promises that I'll spend the money responsibly.