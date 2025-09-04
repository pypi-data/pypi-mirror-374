from canatax.rates.sales.base import BaseSalesTaxRate


class AlbertaSalesTaxRate(BaseSalesTaxRate):
    
    GST = 5
    PST = None
    HST = None


class BritishColumbiaSalesTaxRate(BaseSalesTaxRate):
        
    GST = 5
    PST = 7
    HST = None


class ManitobaSalesTaxRate(BaseSalesTaxRate):
        
    GST = 5
    PST = 7
    HST = None


class QuebecSalesTaxRate(BaseSalesTaxRate):
        
    GST = 5
    PST = 9.975
    HST = None


class PEISalesTaxRate(BaseSalesTaxRate):
        
    GST = None
    PST = None
    HST = 15


class NovaScotiaSalesTaxRate(BaseSalesTaxRate):
        
    GST = None
    PST = None
    HST = 15


class NewBrunswickSalesTaxRate(BaseSalesTaxRate):
        
    GST = None
    PST = None
    HST = 15


class NewfoundlandSalesTaxRate(BaseSalesTaxRate):
        
    GST = None
    PST = None
    HST = 15


class NunavutSalesTaxRate(BaseSalesTaxRate):
        
    GST = 5
    PST = None
    HST = None


class NorthwestTerritoriesSalesTaxRate(BaseSalesTaxRate):
        
    GST = 5
    PST = None
    HST = None


class SaskatchewanSalesTaxRate(BaseSalesTaxRate):
        
    GST = 5
    PST = 6
    HST = None


class OntarioSalesTaxRate(BaseSalesTaxRate):
        
    GST = None
    PST = None
    HST = 13


class YukonSalesTaxRate(BaseSalesTaxRate):
        
    GST = 5
    PST = None
    HST = None
