import csv
import random
import tls_client
import cloudscraper
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

ua = UserAgent(os='linux', browsers=['firefox'])

class BulkWalletChecker:

    def __init__(self):
        self.sendRequest = tls_client.Session(client_identifier='chrome_103')
        self.cloudScraper = cloudscraper.create_scraper()
        self.shorten = lambda s: f"{s[:4]}...{s[-5:]}" if len(s) >= 9 else s
        self.skippedWallets = 0
        self.results = []

    def getTokenDistro(self, wallet: str):
        url = f"https://gmgn.ai/defi/quotation/v1/rank/sol/wallets/{wallet}/unique_token_7d?interval=30d"
        headers = {
            "User-Agent": ua.random
        }
        retries = 3
        tokenDistro = []

        for attempt in range(retries):
            try:
                response = self.sendRequest.get(url, headers=headers).json()
                tokenDistro = response['data']['tokens']
                if tokenDistro:  
                    break
            except Exception:
                time.sleep(1)
            
            try:
                response = self.cloudScraper.get(url, headers=headers).json()
                tokenDistro = response['data']['tokens']
                if tokenDistro:
                    break
            except Exception:
                time.sleep(1)
        
        if not tokenDistro:
            return {
                "No Token Distribution Data": None
            }

        FiftyPercentOrMore = 0
        ZeroToFifty = 0
        FiftyTo100 = 0
        TwoToFour = 0
        FiveToSix = 0
        SixPlus = 0
        NegativeToFifty = 0 

        for profit in tokenDistro:
            total_profit_pnl = profit.get('total_profit_pnl')
            if total_profit_pnl is not None:
                profitMultiplier = total_profit_pnl * 100

                if profitMultiplier <= -50:
                    FiftyPercentOrMore += 1
                elif -50 < profitMultiplier < 0:
                    NegativeToFifty += 1
                elif 0 <= profitMultiplier < 50:
                    ZeroToFifty += 1
                elif 50 <= profitMultiplier < 199:
                    FiftyTo100 += 1
                elif 200 <= profitMultiplier < 499:
                    TwoToFour += 1
                elif 500 <= profitMultiplier < 600:
                    FiveToSix += 1
                elif profitMultiplier >= 600:
                    SixPlus += 1

        return {
            "-50% +": FiftyPercentOrMore,
            "0% - -50%": NegativeToFifty,
            "0 - 50%": ZeroToFifty,
            "50% - 199%": FiftyTo100,
            "200% - 499%": TwoToFour,
            "500% - 600%": FiveToSix,
            "600% +": SixPlus
        }

    def getWalletData(self, wallet: str, skipWallets: bool):
        url = f"https://gmgn.ai/defi/quotation/v1/smartmoney/sol/walletNew/{wallet}?period=7d"
        headers = {
            "User-Agent": ua.random
        }
        retries = 3
        
        for attempt in range(retries):
            try:
                response = self.sendRequest.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    if data['msg'] == "success":
                        data = data['data']
                        
                        if skipWallets:
                            if 'buy_30d' in data and isinstance(data['buy_30d'], (int, float)) and data['buy_30d'] > 0: # and float(data['sol_balance']) >= 1.0: // uncomment this to help filter out wallets that cashed out to CEX, same on line 124
                                return self.processWalletData(wallet, data, headers)
                            else:
                                self.skippedWallets += 1
                                print(f"[🐲] Skipped {self.skippedWallets} wallets", end="\r")
                                return None
                        else:
                            return self.processWalletData(wallet, data, headers)
            
            except Exception as e:
                print(f"[🐲] Error fetching data, trying backup...")
            
            try:
                response = self.cloudScraper.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    if data['msg'] == "success":
                        data = data['data']
                        
                        if skipWallets:
                            if 'buy_30d' in data and isinstance(data['buy_30d'], (int, float)) and data['buy_30d'] > 0: # and float(data['sol_balance']) >= 1.0:
                                return self.processWalletData(wallet, data, headers)
                            else:
                                self.skippedWallets += 1
                                print(f"[🐲] Skipped {self.skippedWallets} wallets", end="\r")
                                return None
                        else:
                            return self.processWalletData(wallet, data, headers)
            
            except Exception:
                print(f"[🐲] Backup scraper failed, retrying...")
            
            time.sleep(1)
        
        print(f"[🐲] Failed to fetch data for wallet {wallet} after {retries} attempts.")
        return None

    
    def processWalletData(self, wallet, data, headers):
        direct_link = f"https://gmgn.ai/sol/address/{wallet}"
        total_profit_percent = f"{data['total_profit_pnl'] * 100:.2f}%" if data['total_profit_pnl'] is not None else "error"
        realized_profit_7d_usd = f"${data['realized_profit_7d']:,.2f}" if data['realized_profit_7d'] is not None else "error"
        realized_profit_30d_usd = f"${data['realized_profit_30d']:,.2f}" if data['realized_profit_30d'] is not None else "error"
        winrate_7d = f"{data['winrate'] * 100:.2f}%" if data['winrate'] is not None else "?"
        sol_balance = f"{float(data['sol_balance']):.2f}" if data['sol_balance'] is not None else "?"

        try:
            winrate_30data = self.sendRequest.get(f"https://gmgn.ai/defi/quotation/v1/smartmoney/sol/walletNew/{wallet}?period=30d", headers=headers).json()['data']
            winrate_30d = f"{winrate_30data['winrate'] * 100:.2f}%" if winrate_30data['winrate'] is not None else "?"
        except Exception as e:
            print(f"[🐲] Error fetching winrate 30d data, trying backup..")
            winrate_30data = self.cloudScraper.get(f"https://gmgn.ai/defi/quotation/v1/smartmoney/sol/walletNew/{wallet}?period=30d", headers=headers).json()['data']
            winrate_30d = f"{winrate_30data['winrate'] * 100:.2f}%" if winrate_30data['winrate'] is not None else "?"

        if "Skipped" in data.get("tags", []):
            return {
                "wallet": wallet,
                "tags": ["Skipped"],
                "directLink": direct_link
            }
        tokenDistro = self.getTokenDistro(wallet)

        try:
            tags = data['tags'] 
        except Exception:
            tags = "?"
        
        return {
            "wallet": wallet,
            "totalProfitPercent": total_profit_percent,
            "7dUSDProfit": realized_profit_7d_usd,
            "30dUSDProfit": realized_profit_30d_usd,
            "winrate_7d": winrate_7d,
            "winrate_30d": winrate_30d,
            "tags": tags,
            "sol_balance": sol_balance,
            "token_distribution": tokenDistro if tokenDistro else {},
            "directLink": direct_link
        }
    
    def fetchWalletData(self, wallets, threads, skipWallets):
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(self.getWalletData, wallet.strip(), skipWallets): wallet for wallet in wallets}
            for future in as_completed(futures):
                result = future.result()
                if result is not None:
                    self.results.append(result)

        result_dict = {}
        for result in self.results:
            wallet = result.get('wallet')
            if wallet:
                result_dict[wallet] = result
                result.pop('wallet', None)  
            else:
                print(f"[🐲] Missing 'wallet' key in result: {result}")

        if self.results and 'token_distribution' in self.results[0]:
            token_dist_keys = self.results[0]['token_distribution'].keys()
        else:
            token_dist_keys = []  

        identifier = self.shorten(list(result_dict)[0])
        filename = f"{identifier}_{random.randint(1111, 9999)}.csv"

        path = f"Dragon/data/Solana/BulkWallet/wallets_{filename}"

        with open(path, 'w', newline='') as outfile:
            writer = csv.writer(outfile)

            header = ['Identifier'] + list(next(iter(result_dict.values())).keys())

            if 'token_distribution' in header:
                header.remove('token_distribution')

            header.extend(token_dist_keys)

            writer.writerow(header)

            for key, value in result_dict.items():
                row = [key]
                for h in header[1:]:
                    if h in value:
                        row.append(value[h])
                    elif 'token_distribution' in value and h in value['token_distribution']:
                        row.append(value['token_distribution'][h])
                    else:
                        row.append(None)
                writer.writerow(row)

        print(f"[🐲] Saved data for {len(result_dict.items())} wallets to {filename}")
