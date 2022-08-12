from datetime import datetime
from urllib import request

class MarketDataMgr:

    @staticmethod
    def retrieveHistoryData(symbol: str, startDate: str, endDate: str)-> str:
        url = 'https://query1.finance.yahoo.com/v7/finance/download/{0}?period1={1}&period2={2}&interval=1d&events=history&includeAdjustedClose=true'
        start = datetime.strptime(startDate, '%m/%d/%Y')
        end = datetime.strptime(endDate, '%m/%d/%Y')
        base = datetime(1970,1,1)

        starttick = ((start - base).days*24*60*60)
        endtick = (((end - base).days+1)*24*60*60)

        queryUrl = url.format(str.upper(symbol), starttick, endtick)
        filepath = './data/{}.csv'.format(str.upper(symbol))
        try:
            request.urlretrieve(queryUrl, filepath)
        except:
            print("Fail to retrieve history data, symbol: {}".format(str.upper(symbol)))

        return filepath
