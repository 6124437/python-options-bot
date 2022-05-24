# python-options-bot

Just playing around with the IBKR API. Building a trading bot that buys and sells options following a fixed strategy.

- [x] Create a simple bot that can buy and sell based on closing value of 1 minute bars
- [ ] Change the bot to trade on bid/ask instead of market
- [ ] Select the correct expiration date (monthly, x days out, volume?)
- [ ] Determine if a certain strike price is under/overpriced
  - [ ]  Find best strike (overpriced) for a certain options chain in certain DELTA range
- [ ] Create a database that keeps track of (open) trades. This to ensure the bot can reload all details of a trade when it has to restart
  - [ ] Read all open positions from IBKR on loading
  - [ ] Save positions/trades in DB
  - [ ] Group multiple positions in one trade/strategy
- [ ] Check for binary events
  - [ ] Earnings
  - [ ] Fed announcement / rate hike / etc
- [ ] Read IV values
- [ ] Calculate beta weighted delta for portfolio
  - [ ] Calculate impact of a trade on BW delta
