from QuantConnect.Data.UniverseSelection import *
import operator
from math import ceil,floor

#This is clone of Fama-French Three-Factor Model Tutorial code, with rename some variables/flags for better understanding

class CoarseFineFundamentalComboAlgorithm(QCAlgorithm):
    def Initialize(self):

        self.SetStartDate(2007, 1, 1)  #Set Start Date
        self.SetEndDate(2009, 5, 11)    #Set End Date
        self.SetCash(100000)           #Set Strategy Cash
        self.rebalance_interval = 3
        self.rebalance_count = self.rebalance_interval-1 #Initializ count to rebalance_interval-1, to start algo immediately
        self.isFineSelectionChanged = False
        self.topFine = []
        self.SetBenchmark("SPY")
    

        self.UniverseSettings.Resolution = Resolution.Daily        
        
        self.AddUniverse(self.CoarseSelectionFunction, self.FineSelectionFunction)
        self.AddEquity("SPY")
        self.__numberOfCoarseSymbols = 100
        self.__numberOfSymbolsFine = 30
        self.num_portfolios = 5
 
        self._changes = None
        self.Schedule.On(self.DateRules.MonthStart("SPY"), self.TimeRules.AfterMarketOpen("SPY"), Action(self.Rebalancing))


    def CoarseSelectionFunction(self, coarse):
        if self.rebalance_count == self.rebalance_interval:
            CoarseWithFundamental = [x for x in coarse if x.HasFundamentalData]
            sortedByDollarVolume = sorted(CoarseWithFundamental, key=lambda x: x.DollarVolume, reverse=True) 
            top = sortedByDollarVolume[:self.__numberOfCoarseSymbols]
            return [x.Symbol for x in top]
        else:
            return [x.Symbol for x in self.topFine]


    def FineSelectionFunction(self, fine):
        if self.rebalance_count == self.rebalance_interval:
            self.rebalance_count = 0
            self.isFineSelectionChanged = True
        
            filtered_fine = [x for x in fine if x.OperationRatios.OperationMargin.Value
                                            and x.ValuationRatios.PriceChange1M 
                                            and x.ValuationRatios.BookValuePerShare]
    
            sortedByfactor1 = sorted(filtered_fine, key=lambda x: x.OperationRatios.OperationMargin.Value, reverse=True)
            sortedByfactor2 = sorted(filtered_fine, key=lambda x: x.ValuationRatios.PriceChange1M, reverse=True)
            sortedByfactor3 = sorted(filtered_fine, key=lambda x: x.ValuationRatios.BookValuePerShare, reverse=True)
            
            num_stocks = floor(len(filtered_fine)/self.num_portfolios)
            
            self.Log(str(num_stocks))


            stock_dict = {}
            
            for i,ele in enumerate(sortedByfactor1):
                rank1 = i
                rank2 = sortedByfactor2.index(ele)
                rank3 = sortedByfactor3.index(ele)
                score = sum([rank1*0.2,rank2*0.4,rank3*0.4])
                stock_dict[ele] = score
            
            self.sorted_stock = sorted(stock_dict.items(), key=lambda d:d[1],reverse=False)
            sorted_symbol = [self.sorted_stock[i][0] for i in range(len(self.sorted_stock))]
            self.topFine = sorted_symbol[:self.__numberOfSymbolsFine]
                
            
            return [x.Symbol for x in self.topFine]
        else:
            return [x.Symbol for x in self.topFine]


    def OnData(self, data):
        if len(self.topFine)>0:
            if self.isFineSelectionChanged == True:
                self.isFineSelectionChanged = False

                # if we have no changes, do nothing
                if self._changes == None: return
                # liquidate removed securities
                for security in self._changes.RemovedSecurities:
                    if security.Invested:
                        self.Liquidate(security.Symbol)
                 
                #for security in self._changes.AddedSecurities:
                #    self.SetHoldings(security.Symbol, 1/float(len(self._changes.AddedSecurities)))    
                
                for x in self.topFine:
                    self.SetHoldings(x.Symbol, 1/float(len(self.topFine)))  
                
                invested = [x.Key for x in self.Portfolio if x.Value.Invested]
                keys = self.Portfolio.Keys
                self.Log("Portfolio count: {0}, invested: {1}".format(len(keys), len(invested)))
         
                self._changes = None

    # this event fires whenever we have changes to our universe
    def OnSecuritiesChanged(self, changes):
        self._changes = changes
    
    def Rebalancing(self):
        self.rebalance_count += 1