from datetime import datetime
from urllib import request
import os.path

class MarketDataMgr:
    dataFileFolder = './data'
    dataFilePath = os.path.join(dataFileFolder, '{}.csv')
    @staticmethod
    def retrieveHistoryDataToCSV(symbols: list, startDate: datetime, endDate: datetime)-> str:
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
                request.urlretrieve(queryUrl, filepath)
                res[str.upper(symbol)]= filepath
            except:
                print("Fail to retrieve history data, symbol: {}".format(str.upper(symbol)))

        return res
    
    @staticmethod
    def retrieveHistoryDataStr(symbols: list, startDate: str, endDate: str)-> str:
        start = datetime.strptime(startDate, '%m/%d/%Y')
        end = datetime.strptime(endDate, '%m/%d/%Y')
        return MarketDataMgr.retrieveHistoryDataToCSV(list, start, end)
