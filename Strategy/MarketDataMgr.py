from datetime import datetime
import logging
from pydoc import describe
from urllib import request
import os.path
import pandas as pd

class MarketDataMgr:
    dataFileFolder = './data'
    dataFilePath = os.path.join(dataFileFolder, '{}.csv')

    #market data fields
    date_lbl = 'Date'
    open_lbl = 'Open'
    high_lbl = 'High'
    low_lbl ='Low'
    close_lbl = 'Close'
    adjcls_lbl = 'Adj Close'
    volume_lbl = 'Volume'
    labels = [date_lbl, open_lbl, high_lbl, low_lbl, close_lbl, adjcls_lbl, volume_lbl]

    @staticmethod
    #set getMktDataCSV to false to avoid downloading duplicate market data files
    def retrieveHistoryDataToCSV(symbols: list, startDate: datetime, endDate: datetime, getMktDataCSV= True)-> str:
        url = 'https://query1.finance.yahoo.com/v7/finance/download/{0}?period1={1}&period2={2}&interval=1d&events=history&includeAdjustedClose=true'

        base = datetime(1970,1,1)
        symbols = set([str.upper(x) for x in symbols])
        starttick = ((startDate - base).days*24*60*60)
        endtick = (((endDate - base).days+1)*24*60*60)

        res = {}
        for symbol in symbols:
            queryUrl = url.format(symbol, starttick, endtick)
            filepath = MarketDataMgr.dataFilePath.format(symbol)
            try:
                if getMktDataCSV:
                    request.urlretrieve(queryUrl, filepath)
                res[str.upper(symbol)]= filepath
            except:
                logging.error("Fail to retrieve history data, symbol: {}".format(str.upper(symbol)))
                print("Fail to retrieve history data, symbol: {}".format(str.upper(symbol)))

        return res
    
    @staticmethod
    def retrieveHistoryDataStr(symbols: list, startDate: str, endDate: str)-> str:
        start = datetime.strptime(startDate, '%m/%d/%Y')
        end = datetime.strptime(endDate, '%m/%d/%Y')
        return MarketDataMgr.retrieveHistoryDataToCSV(list, start, end)

    #return a single dataframe with symbols as column 
    @staticmethod
    def getEquityDataSingleField(symbols: list, field: str, startDate: datetime, endDate:datetime, innerjoin = True, getMktDataCSV = True )->pd.DataFrame:
        if field not in MarketDataMgr.labels: return None
        ath = MarketDataMgr.dataFilePath
        res = None
        for symbol in symbols:
            md = MarketDataMgr.retrieveHistoryDataToCSV([symbol], startDate, endDate, getMktDataCSV)
            name= md[str.upper(symbol)]
            df = pd.read_csv(name, index_col=0)
            df.index = pd.to_datetime(df.index)
            df.sort_index(axis=0)
            temp = df[field].rename(str.upper(symbol))
            if res is None :
                res = pd.DataFrame(temp)
            else:
                if innerjoin:
                    res = pd.concat([res, temp], axis = 1, join = 'inner')
                else :
                    res = pd.concat([res, temp], axis = 1)
        return res

    #return Dictionary with key is Symbol and value is Dataframe contain all field for the symbol
    #innerjoin set to true for returning all symbols in the same datetime range
    @staticmethod
    def getEquityDataMultiFields(symbols: list, fields: list, startDate: datetime, endDate:datetime, innerjoin = True, getMktDataCSV = True )->pd.DataFrame:
        fields = [x for x in fields if x in MarketDataMgr.labels]
        symbols = [str.upper(x) for x in symbols]
        if len(fields) == 0: return None

        path = MarketDataMgr.dataFilePath
        res = {}
        idx = None
        for symbol in symbols:
            md = MarketDataMgr.retrieveHistoryDataToCSV([symbol], startDate, endDate, getMktDataCSV)
            if symbol not in md: continue

            name= md[symbol]
            df = pd.read_csv(name, index_col=0)
            df.index = pd.to_datetime(df.index)        
            res[symbol] = df[fields]

            if idx is None:
                idx = df.index
            else:
                idx =  idx.intersection(df.index, sort=None)
    
        if innerjoin:
            for key in res:
                tmp = res[key].loc[idx]
                res[key] = tmp

        return res



