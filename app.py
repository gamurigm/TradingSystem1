import time
from ibapi.client import EClient
from ibapi.wrapper import EWrapper

from ibapi.client import Contract

from threading import Thread


class IBClient(EWrapper, EClient):
     
    def __init__(self, host, port, client_id):
        EClient.__init__(self, self) 
        
        self.connect(host, port, client_id)

        thread = Thread(target=self.run)
        thread.start()

    def historicalData(self, req_id, bar):
        print(bar)


    # callback when all historical data has been received
    def historicalDataEnd(self, reqId, start, end):
        print(f"end of data {start} {end}")


    def error(self, req_id, code, msg, misc):
        if code in [2104, 2106, 2158]:
            print(msg)
        else:
            print('Msg {}: {}'.format(code, msg))


if __name__ == '__main__':
    client = IBClient('127.0.0.1', 7497, 1)

    time.sleep(1)

    contract = Contract()
    contract.symbol = 'TSM'
    contract.secType = 'STK'
    contract.exchange = 'SMART'
    contract.currency = 'USD'
    what_to_show = 'TRADES'

    client.reqHistoricalData(
        2, contract, '', '30 D', '5 mins', what_to_show, True, 2, False, []
    )

    time.sleep(1)