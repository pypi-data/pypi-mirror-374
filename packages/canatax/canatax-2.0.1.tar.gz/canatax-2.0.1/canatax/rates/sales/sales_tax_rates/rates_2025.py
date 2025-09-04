from canatax.rates.sales.base import BaseSalesTaxRate

# 2025
# https://www.canada.ca/en/revenue-agency/services/tax/businesses/topics/gst-hst-businesses/charge-collect-which-rate/calculator.html
# https://www.revenuquebec.ca/en/businesses/consumption-taxes/gsthst-and-qst/basic-rules-for-applying-the-gsthst-and-qst/tables-of-gst-and-qst-rates/


class AlbertaSalesTaxRate(BaseSalesTaxRate):
    
    GST = 5
    PST = 0
    HST = 0
    QST = 0


class BritishColumbiaSalesTaxRate(BaseSalesTaxRate):
        
    GST = 5
    PST = 7
    HST = 0
    QST = 0


class ManitobaSalesTaxRate(BaseSalesTaxRate):

    GST = 5
    PST = 7
    HST = 0
    QST = 0


class NewBrunswickSalesTaxRate(BaseSalesTaxRate):
        
    GST = 0
    PST = 0
    HST = 15
    QST = 0


class NewfoundlandSalesTaxRate(BaseSalesTaxRate):
        
    GST = 0
    PST = 0
    HST = 15
    QST = 0


class NorthwestTerritoriesSalesTaxRate(BaseSalesTaxRate):
        
    GST = 5
    PST = 0
    HST = 0
    QST = 0


class NovaScotiaSalesTaxRate(BaseSalesTaxRate):
        
    GST = 0
    PST = 0
    HST = 14
    QST = 0


class NunavutSalesTaxRate(BaseSalesTaxRate):
        
    GST = 5
    PST = 0
    HST = 0
    QST = 0


class OntarioSalesTaxRate(BaseSalesTaxRate):
        
    GST = 0
    PST = 0
    HST = 13
    QST = 0


class PEISalesTaxRate(BaseSalesTaxRate):
        
    GST = 0
    PST = 0
    HST = 15
    QST = 0
    

class QuebecSalesTaxRate(BaseSalesTaxRate):
        
    GST = 5
    PST = 0
    HST = 0
    QST = 9.975


class SaskatchewanSalesTaxRate(BaseSalesTaxRate):
        
    GST = 5
    PST = 6
    HST = 0
    QST = 0


class YukonSalesTaxRate(BaseSalesTaxRate):

    GST = 5
    PST = 0
    HST = 0
    QST = 0
