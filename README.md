<h1 align="center">
	<img src="https://i.imgur.com/Ok56fSu.png" width="150px"><br>
    Dragon
</h1>
<p align="center">
	The all-in-one tool to help you find profitable wallets on Solana, Ethereum and Binance Smart Chain.
</p><br>
<p align="center"><b>Note, the GMGN.ai domain is cloudflare protected,<br> meaning some requests will fail to get access to an unprotected endpoint <br>Join the Discord Server<br>https://discord.gg/xxWqZppjht</b></p>
<h1 align="left">Suggestions</h1>
<a href="https://x.com/DragonWallets/status/1853618085149778392" target="_blank">Drop Suggestions!</a> (and a follow)
<h1 align="left">Tutorial</h1>
<a href="https://youtu.be/ab17qHh2P-o?si=vIKSK2lbY-UdaqGP" target="_blank">YouTube Video</a>
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
2. Receive the bundle data.<br><br>
Note: This will only recognise a bundle if the bundled wallets are shown under the "DEV" tab on GMGN.ai - <a href="https://gmgn.ai/sol/token/231Y5yfc5aeajFfqaM5P9WvwqSiMG5CyuwSib9Pbpump?tag=creator">Example</a>
</p>

<h1 align="left">
Bulk Wallet Checker
</h1>
<p>Check a large list of wallets to receive their PnL, winrate and more data.</p>
<p>
1. Select your .txt file or enter your own directory.<br>
2. Enter the amount of threads you'd like to use.<br>
3. Select whether you'd like to use proxies or not.<br>
4. Enter whether you'd like to skip certain wallets.<br>
5. Receive your wallet data.
</p>

<h1 align="left">
Top Traders Scraper
</h1>
<p>Scrape the top 100 traders of Solana tokens to receive their PnL, winrate and more data.</p>
<p>
1. Load <code>data/Solana/TopTraders/tokens.txt</code> with contract addresses.<br>
2. Enter the amount of threads you'd like to use.<br>
3. Select whether you'd like to use proxies or not.<br>
4. Receive your top traders data.
</p>

<h1 align="left">
All Transaction Scan
</h1>
<p>Grab every single wallet address that made a buy transaction of a Solana token. I do not recommend a large market cap token.</p>
<p>
1. Enter a contract address. <br>
2. Enter the amount of threads you'd like to use.<br>
3. Select whether you'd like to use proxies or not.<br>
4. Wait and receive your wallet addresses.
</p>

<h1 align="left">
Get Transaction By Timestamp
</h1>
<p>Grab every single wallet address that made a buy transaction of a Solana token between 2 timestamps.</p>
<p>
1. Enter a contract address. <br>
2. Enter the amount of threads you'd like to use.<br>
3. Select whether you'd like to use proxies or not.<br>
4. Enter first & second timestamps.<br>
5. Wait and receive your wallet addresses.
</p>

<h1 align="left">
Copy Wallet Finder
</h1>

[Use This](https://github.com/1f1n/solana-check-contested-wallets)

<h1 align="left">
Top Holders Scraper
</h1>
<p>Scrape the top 100 holders of Solana tokens to receive their PnL, winrate and more data.</p>
<p>
1. Load <code>data/Solana/TopHolders/tokens.txt</code> with contract addresses.<br>
2. Enter the amount of threads you'd like to use.<br>
3. Select whether you'd like to use proxies or not.<br>
4. Receive your top traders data.
</p>

<h1 align="left">
Early Buyers Scraper
</h1>
<p>Scrape the early buyers, excluding the dev, of Solana tokens to receive their PnL and more data.</p>
<p>
1. Load <code>data/Solana/EarlyBuyers/tokens.txt</code> with contract addresses.<br>
2. Enter the amount of early buyers you'd like to scrape per contract address.<br>
3. Enter the amount of threads you'd like to use.<br>
4. Select whether you'd like to use proxies or not.<br>
5. Receive your top traders data.
</p>

<h1 align="left">
GMGN Modules
</h1>
<p>Scrape the contract addresses of new, soaring, completing and bonding tokens on Pump.Fun and Moonshot.</p>
<p>
1. Select the module you want to use from the four listed.<br>
2. Enter the amount of threads you'd like to use.<br>
3. Select whether you'd like to use proxies or not.<br>
4. Receive your contract addresses.<br><br>
Note, here are the links to where the data is being grabbed from:<br>
<a href="https://gmgn.ai/meme?chain=sol&tab=new_creation">New Token</a><br>
<a href="https://gmgn.ai/meme?chain=sol&tab=completing">Completing Token</a><br>
<a href="https://gmgn.ai/meme?chain=sol&tab=soaring">Soaring Token</a><br>
<a href="https://gmgn.ai/meme?chain=sol&tab=complete">Bonded Token</a>
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
</p>
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
<p>
23/09/2024<br>
- Added Ethereum support.<br>
</p>
<p>
09/10/2024<br>
- Added <a href="https://github.com/1f1n/Dragon/blob/main/Dragon/data/Proxies/proxies.txt">proxy support</a> to Solana modules.<br>
- Added Top Holders scraper to Solana modules.<br>
- Added Copy Wallet Finder to Solana modules.<br>
</p>
<p>
16/10/2024<br>
- Fixed Copytrade Wallet Finder showing previous 10 instead of after 10.<br>
- Added attempts to filter out volume & MEV bots from the 10 traders.
</p>
<p>
23/10/2024<br>
- Added TLS session randomisation to support GMGN's recent API endpoint changes.
</p>
<p>
04/11/2024<br>
- Added Early Buyers scraper to Solana modules.
</p>
<p>
05/11/2024<br>
- Added GMGN Contract Address scraping modules for Pump.Fun and Moonshot.
</p>
<p>
06/11/2024<br>
- Deprecated Tron modules.
</p>
<p>
27/11/2024<br>
- Fixed Bundle Checker for Solana module.
</p>
<p>
03/02/2025<br>
- Removed Cloudscraper (sucks).<br>
- Fixed Bundle Checker.<br>
- Various other small fixes.
</p>
<p>
22/03/2025<br>
- Added Cloudflare bypass to Ethereum modules.<br>
- Added BSC chain modules.<br>
- Various other small improvments and fixes.
</p>
<p>
23/03/2025<br>
- Added automatic updater.
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
<a href="https://github.com/azek10">
Azek<br>
</a>
