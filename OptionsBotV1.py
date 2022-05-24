from datetime import datetime
from ib_insync import *
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio

from pytz import timezone
# util.startLoop()  # uncomment this line when in a notebook

class OptionsBotV1:

    def __init__(self):
        print("Running bot")

        try:
            self.ib = IB()
            self.ib.connect('127.0.0.1', 7497, clientId=1)
        except Exception as e:
            print(str(e))


        # Create SPY Contract
        self.underlying = Stock('SPY', 'SMART', 'USD')
        self.ib.qualifyContracts(self.underlying)
        print("Backfilling data to catchup ...")
        # Request Streaming bars
        self.data = self.ib.reqHistoricalData(self.underlying,
            endDateTime='',
            durationStr='2 D',
            barSizeSetting='1 min',
            whatToShow='TRADES',
            useRTH=True,
            keepUpToDate=True,)

        #Local variables
        self.in_trade = False

        
        self.chains = self.ib.reqSecDefOptParams(self.underlying.symbol, '', self.underlying.secType, self.underlying.conId)
    

        #Update chain every house
        update_chain_scheduler = BackgroundScheduler(job_defaults={'max_instances': 2}, timezone="Europe/Berlin")
        update_chain_scheduler.add_job(func=self.update_options_chains,trigger='cron',hour='*')
        update_chain_scheduler.start()

        print("Running live")
        # Set callback function for streaming bars
        self.data.updateEvent += self.on_bar_update
        self.ib.execDetailsEvent += self.exec_status
        #Run forever
        self.ib.run()

    #Update options chain
    def update_options_chains(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            print("Updating options chains")
            self.chains = self.ib.reqSecDefOptParams(self.underlying.symbol, '', self.underlying.secType, self.underlying.conId)
            
        except Exception as e:
            print(str(e))

    #On bar Update, when we get new data
    def on_bar_update(self, bars: BarDataList, has_new_bar: bool):
        try:
            if has_new_bar:
                #Convert BarDataList to pandas Dataframe
                df = util.df(bars)
                #Check if we are in a trade
                
                print("Last Close : " + str(df.close.iloc[-1]))
                if not self.in_trade:
                    #Check for 3 Consecutive Higher Closes
                    if df.close.iloc[-1] > df.close.iloc[-2]:# and df.close.iloc[-2] > df.close.iloc[-3]:
                        #Buy call contacts that are out 5usd of the money
                        for optionschain in self.chains:
                            for strike in optionschain.strikes:
                                if strike > df.close.iloc[-1] +5:
                                    print("entering trade")
                                    self.options_contract = Option(self.underlying.symbol,optionschain.expirations[1],strike,'C','SMART',tradingClass=self.underlying.symbol)
                                    options_order = MarketOrder('BUY', 1, account=self.ib.wrapper.accounts[-1])
                                    trade = self.ib.placeOrder(self.options_contract, options_order)
                                    self.lastEstimatedFillPrice = df.close.iloc[-1]
                                    self.in_trade = True
                                    return # Important so it doesnt keep looping trade
                else:#we are in a trade
                    if df.close.iloc[-1] > self.lastEstimatedFillPrice:
                        #Sell for profit scalping
                        print("Scalping profit.")
                        options_order = MarketOrder('SELL', 1, account=self.ib.wrapper.accounts[-1])
                        trade = self.ib.placeOrder(self.options_contract, options_order)
                        self.in_trade = False
        except Exception as e:
            print(str(e))

    #Execution status
    def exec_status(self,trade: Trade, fill: Fill):
        print("Filled")

# contract = Forex('EURUSD')
# bars = ib.reqHistoricalData(
#     contract, endDateTime='', durationStr='30 D',
#     barSizeSetting='1 hour', whatToShow='MIDPOINT', useRTH=True)

# # convert to pandas dataframe:
# df = util.df(bars)
# print(df)

#Instantiate Class to get things rolling
OptionsBotV1()