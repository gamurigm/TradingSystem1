import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'venv/Lib/site-packages'))

import time, datetime
import queue
import pandas as pd

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.client import Contract

from lightweight_charts import Chart

from threading import Thread


INITIAL_SYMBOL = "NVDA"

DEFAULT_HOST = '127.0.0.1'
DEFAULT_CLIENT_ID = 1

LIVE_TRADING = False
LIVE_TRADING_PORT = 7496
PAPER_TRADING_PORT = 7497
TRADING_PORT = PAPER_TRADING_PORT
if LIVE_TRADING:
    TRADING_PORT = LIVE_TRADING_PORT

data_queue = queue.Queue()

class IBClient(EWrapper, EClient):
     
    def __init__(self, host, port, client_id):
        EClient.__init__(self, self) 
        
        self.connect(host, port, client_id)

        thread = Thread(target=self.run)
        thread.start()


    def error(self, req_id, code, msg, misc):
        if code in [2104, 2106, 2158]:
            print(msg)
        else:
            print('Error {}: {}'.format(code, msg))

    def historicalData(self, req_id, bar):
        print(bar)

        t = datetime.datetime.fromtimestamp(int(bar.date))

        # creation bar dictionary for each bar received
        data = {
            'date': t,
            'open': bar.open,
            'high': bar.high,
            'low': bar.low,
            'close': bar.close,
            'volume': int(bar.volume)
        }

        print(data)

        # Put the data into the queue
        data_queue.put(data)

    # callback when all historical data has been received
    def historicalDataEnd(self, reqId, start, end):
        print(f"end of data {start} {end}")

        update_chart()



def get_bar_data(symbol, timeframe):
    print(f"getting bar data for {symbol} {timeframe}")

    contract = Contract()
    contract.symbol = symbol
    contract.secType = 'STK'
    contract.exchange = 'SMART'
    contract.currency = 'USD'
    what_to_show = 'TRADES'
    
    #now = datetime.datetime.now().strftime('%Y%m%d %H:%M:%S')
    #chart.spinner(True)

    client.reqHistoricalData(
        2, contract, '', '30 D', timeframe, what_to_show, True, 2, False, []
    )

    time.sleep(1)
       
    chart.watermark(symbol)

# called when we want to update what is rendered on the chart 
def update_chart():
    try:
        bars = []
        while True:  # Keep checking the queue for new data
            data = data_queue.get_nowait()
            bars.append(data)
    except queue.Empty:
        print("empty queue")
    finally:
        # once we have received all the data, convert to pandas dataframe
        df = pd.DataFrame(bars)
        print(df)

        # set the data on the chart
        if not df.empty:
            chart.set(df)

            # once we get the data back, we don't need a spinner anymore
            #chart.spinner(False)

if __name__ == '__main__':
    client = IBClient(DEFAULT_HOST, TRADING_PORT, DEFAULT_CLIENT_ID)
    time.sleep(1)

    chart = Chart(toolbox=True, width=1000, inner_width=0.6, inner_height=1)
    chart.legend(True)
    chart.topbar.textbox('symbol', INITIAL_SYMBOL)

    get_bar_data(INITIAL_SYMBOL, '5 mins')

    time.sleep(1)

    chart.show(block=True)