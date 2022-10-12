from os import POSIX_FADV_NOREUSE
from FinUtil import *
from MarketDataMgr import *
from datetime import datetime
import matplotlib.pyplot as plt
import logging
from AbstractStrategy import *
from Strategy.AbstractStrategy import AbstractStrategy

#strategy name
#list of strategy parameters and their ranges

class TestHarness:
    def __init__(self) -> None:
        pass


    def Run(strategy: AbstractStrategy, params: dict):
        pass
    

    def RunSymbolMatrixTest(stragegy: AbstractStrategy, parms: list, symbols: list):
        #1. prepare market data for each symbol
        
        #2. run back test for each symbol pair

        #3. rank the performance

        pass