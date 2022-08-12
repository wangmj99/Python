import pandas as pd
import numpy as np



class BasicTemplateAlgorithm(QCAlgorithm):
	def __init__(self):
		self.tickers = ['KO','PG']
		self.spy = 'SPY'
		
	def Initialize(self):
		self.SetCash(100000)
		self.SetStartDate(2013,1,1)
		self.SetEndDate(2015,1,1)
		
		for i in range(len(self.tickers)):
			symbol = self.AddEquity(self.tickers[i], Resolution.Daily)
			self.tickers[i] = symbol.Symbol


	def OnData(self, slice):
		if not self.Portfolio.Invested:
			self.SetHoldings(self.tickers[0], -0.48)
			self.SetHoldings(self.tickers[1], 0.5)