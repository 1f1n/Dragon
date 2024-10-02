<h1 align="center">
	<img src="https://i.imgur.com/Ok56fSu.png" width="150px"><br>
    Dragon
</h1>
<p align="center">
	The all-in-one tool to help you find profitable wallets on Solana, Tron and Ethereum.
</p><br>
<h1 align="left">
Setup
</h1>

`
pip install -r requirements.txt
`
<br><br>
`
python dragon.py
`

<h1 align="left">
Bundle Checker 
</h1>
<p>Check if a Solana contract has had multiple buys bundled into one transaction.</p>
<p>
1. Enter a contract address.<br>
2. Receive the bundle data.
</p>

<h1 align="left">
Bulk Wallet Checker
</h1>
<p>Check a large list of wallets to receive their PnL, winrate and more data.</p>
<p>
1. Select your .txt file or enter your own directory.<br>
2. Enter the amount of threads you'd like to use.<br>
3. Enter whether you'd like to skip certain wallets.<br>
4. Receive your wallet data.
</p>

<h1 align="left">
Top Traders Scraper
</h1>
<p>Scrape the top 100 traders of Solana tokens to receive their PnL, winrate and more data.</p>
<p>
1. Load <code>data/Solana/TopTraders/tokens.txt`</code> with contract addresses.<br>
2. Enter the amount of threads you'd like to use.<br>
3. Receive your top traders data.
</p>

<h1 align="left">
All Transaction Scan
</h1>
<p>Grab every single wallet address that made a buy transaction of a Solana token. I do not recommend a large market cap token.</p>
<p>
1. Enter a contract address. <br>
2. Enter the amount of threads you'd like to use.<br>
3. Wait and receive your wallet addresses.
</p>

<h1 align="left">
Get Transaction By Timestamp
</h1>
<p>Grab every single wallet address that made a buy transaction of a Solana token between 2 timestamps.</p>
<p>
1. Enter a contract address. <br>
2. Enter the amount of threads you'd like to use.<br>
3. Enter first & second timestamps.
4. Wait and receive your wallet addresses.
</p>

<h1 align="left">
Updates
</h1>
<p>
19/08/2024<br>
- General logic fixes.<br>
- Thread cap of 100.
</p>
<p>
20/08/2024<br>
- Added backup requests using cloudscraper, please reinstall requirements.txt.
</p>
<p>
21/08/2024<br>
- General logic fixes.<br>
- Added random user agent generator to all requests, please reinstall requirements.txt.
</p>
22/08/2024<br>
- Added clear client function when a general exception occurs.<br>
- Added new module to find wallet address by transaction timestamp.
<p><br>
29/08/2024<br>
- General logic fixes.<br>
- Added option to purge all files.<br>
- Added token distribution data to the Bulk Wallet Checker.<br>
- Added request retries, will attempt 3 times until data is found, boosting request success rate by 80% roughly.
</p><br>
02/09/2024<br>
- General logic fixes.<br>
- Added chain selection.<br>
- Added Tron Bulk Wallet Checker. (Inaccurate at the moment, thanks GMGN.)<br>
- Added Tron Top Trader Scraper.
<p><br>
08/09/2024<br>
- Added SOL Balance & Trading Platform data to Bulk Wallet Checker.<br>
- Slowing down on the updates due to market conditions & the tool is stacked.
</p>
<p><br>
23/09/2024<br>
- Added Ethereum support.<br>
</p>
<h1 align="left">
Donations
</h1>
Donations are appreciated! (Solana)

```
FF3gkF88aJ6DayFHVmUw7TvNYJnXzmGBu6P5RrEcoins
```

<h1 align="left">
Credits
</h1>
<a href="https://github.com/1f1n">
Me<br>
</a>
