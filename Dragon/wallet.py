import csv
import datetime
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
        self.proxyPosition = 0
        self.results = []

    def loadProxies(self):
        with open("Dragon/data/Proxies/proxies.txt", 'r') as file:
            proxies = file.read().splitlines()

        formatted_proxies = []
        for proxy in proxies:
            if ':' in proxy:  
                parts = proxy.split(':')
                if len(parts) == 4:
                    ip, port, username, password = parts
                    formatted_proxies.append({
                        'http': f"http://{username}:{password}@{ip}:{port}",
                        'https': f"http://{username}:{password}@{ip}:{port}"
                    })
                else:
                    formatted_proxies.append({
                        'http': f"http://{proxy}",
                        'https': f"http://{proxy}"
                    })
            else:
                formatted_proxies.append(f"http://{proxy}")        
        return formatted_proxies
    
    def configureProxy(self, proxy):
        if isinstance(proxy, dict): 
            self.sendRequest.proxies = proxy
        elif proxy:
            self.sendRequest.proxies = {
                'http': proxy,
                'https': proxy
            }
        return proxy
    
    def getNextProxy(self):
        proxies = self.loadProxies()
        proxy = proxies[self.proxyPosition % len(proxies)]
        self.proxyPosition += 1
        return proxy

    
    def getTokenDistro(self, wallet: str, useProxies):
        url = f"https://gmgn.ai/defi/quotation/v1/rank/sol/wallets/{wallet}/unique_token_7d?interval=7d"
        headers = {
            "User-Agent": ua.random
        }
        retries = 3
        tokenDistro = []

        for attempt in range(retries):
            try:
                proxy = self.getNextProxy() if useProxies else None
                self.configureProxy(proxy)
                response = self.sendRequest.get(url, headers=headers).json()
                tokenDistro = response['data']['tokens']
                if tokenDistro:  
                    break
            except Exception:
                time.sleep(1)
            
            try:
                proxy = self.getNextProxy() if useProxies else None
                proxies = {'http': proxy, 'https': proxy} if proxy else None
                response = self.cloudScraper.get(url, headers=headers, proxies=proxies).json()
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
        
        # filter checks
        plus100 = 0
        plus200 = 0
        plus500 = 0
        plus1000 = 0

        for profit in tokenDistro:
            total_profit_pnl = profit.get('total_profit_pnl')
            if total_profit_pnl is not None:
                profitMultiplier = total_profit_pnl * 100

                if profitMultiplier >= 1000:
                    plus1000 += 1
                elif profitMultiplier >= 500:
                    plus500 += 1
                elif profitMultiplier >= 200:
                    plus200 += 1
                elif profitMultiplier >= 100:
                    plus100 += 1

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
            "600% +": SixPlus,
            
            "100%+": plus100,
            "200%+": plus200,
            "500%+": plus500,
            "1000%+": plus1000
        }
    
    
    def getWalletData(self, wallet: str, skipWallets: bool, useProxies: bool = None, filters: dict = None):
        url = f"https://gmgn.ai/defi/quotation/v1/smartmoney/sol/walletNew/{wallet}?period=7d"
        headers = {
            "User-Agent": ua.random
        }
        retries = 3
        
        for attempt in range(retries):
            try:
                proxy = self.getNextProxy() if useProxies else None
                self.configureProxy(proxy)
                response = self.sendRequest.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    if data['msg'] == "success":
                        data = data['data']

                        if skipWallets and 'buy_30d' in data and isinstance(data['buy_30d'], (int, float)) and data['buy_30d'] == 0:#  and float(data['sol_balance']) >= 1.0: (uncomment this to filter out insiders that cashed out already)
                            self.skippedWallets += 1
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Skipped {self.skippedWallets} wallets", end="\r")
                            return None

                        if filters["minWinRate"] and (data['winrate'] is None or data['winrate'] * 100 < filters["minWinRate"]):
                            self.skippedWallets += 1
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Skipped {self.skippedWallets} wallets", end="\r")
                            return None

                        if filters["maxWinRate"] and filters["maxWinRate"] != 0 and (data['winrate'] is None or data['winrate']*100 > filters["maxWinRate"]):
                            self.skippedWallets += 1
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Skipped {self.skippedWallets} wallets", end="\r")
                            return None

                        if filters["minPNL"] and (data['pnl_7d'] is None or data['pnl_7d'] < filters["minPNL"]):
                            self.skippedWallets += 1
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Skipped {self.skippedWallets} wallets", end="\r")
                            return None

                        if filters["maxPNL"] and filters["maxPNL"] != 0 and (data['pnl_7d'] is None or data['pnl_7d'] > filters["maxPNL"]):
                            self.skippedWallets += 1
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Skipped {self.skippedWallets} wallets", end="\r")
                            return None

                        if filters["minTokensTraded"] and (data['buy_7d'] is None or data['buy_7d'] < filters["minTokensTraded"]):
                            self.skippedWallets += 1
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Skipped {self.skippedWallets} wallets", end="\r")
                            return None

                        if filters["maxTokensTraded"] and filters["maxTokensTraded"] != 0 and (data['buy_7d'] is None or data['buy_7d'] > filters["maxTokensTraded"]):
                            self.skippedWallets += 1
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Skipped {self.skippedWallets} wallets", end="\r")
                            return None

                        return self.processWalletData(wallet, data, headers, useProxies, filters)
            
            except Exception as e:
                print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Error fetching data, trying backup...  {e}")
            
            try:
                proxy = self.getNextProxy() if useProxies else None
                response = self.cloudScraper.get(url, headers=headers, proxies=proxy).json()
                if response.status_code == 200:
                    data = response.json()
                    if data['msg'] == "success":
                        data = data['data']

                        if skipWallets and 'buy_30d' in data and isinstance(data['buy_30d'], (int, float)) and data['buy_30d'] == 0:#  and float(data['sol_balance']) >= 1.0: (uncomment this to filter out insiders that cashed out already)
                            self.skippedWallets += 1
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Skipped {self.skippedWallets} wallets", end="\r")
                            return None

                        if filters["minWinRate"] and (data['winrate'] is None or data['winrate'] * 100 < filters["minWinRate"]):
                            self.skippedWallets += 1
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Skipped {self.skippedWallets} wallets", end="\r")
                            return None

                        if filters["maxWinRate"] and filters["maxWinRate"] != 0 and (data['winrate'] is None or data['winrate']*100 > filters["maxWinRate"]):
                            self.skippedWallets += 1
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Skipped {self.skippedWallets} wallets", end="\r")
                            return None

                        if filters["minPNL"] and (data['pnl_7d'] is None or data['pnl_7d'] < filters["minPNL"]):
                            self.skippedWallets += 1
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Skipped {self.skippedWallets} wallets", end="\r")
                            return None

                        if filters["maxPNL"] and filters["maxPNL"] != 0 and (data['pnl_7d'] is None or data['pnl_7d'] > filters["maxPNL"]):
                            self.skippedWallets += 1
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Skipped {self.skippedWallets} wallets", end="\r")
                            return None

                        if filters["minTokensTraded"] and (data['buy_7d'] is None or data['buy_7d'] < filters["minTokensTraded"]):
                            self.skippedWallets += 1
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Skipped {self.skippedWallets} wallets", end="\r")
                            return None

                        if filters["maxTokensTraded"] and filters["maxTokensTraded"] != 0 and (data['buy_7d'] is None or data['buy_7d'] > filters["maxTokensTraded"]):
                            self.skippedWallets += 1
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Skipped {self.skippedWallets} wallets", end="\r")
                            return None
                        
                        return self.processWalletData(wallet, data, headers, useProxies, filters)
                    
                
            except Exception as e:
                print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Backup scraper failed, retrying... {e}")
            
            time.sleep(1)
        
        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Failed to fetch data for wallet {wallet} after {retries} attempts.")
        return None

    
    def processWalletData(self, wallet, data, headers, useProxies, filters: dict = None):
        direct_link = f"https://gmgn.ai/sol/address/{wallet}"
        total_profit_percent = f"{data['total_profit_pnl'] * 100:.2f}%" if data['total_profit_pnl'] is not None else "error"
        realized_profit_7d_usd = f"${data['realized_profit_7d']:,.2f}" if data['realized_profit_7d'] is not None else "error"
        realized_profit_30d_usd = f"${data['realized_profit_30d']:,.2f}" if data['realized_profit_30d'] is not None else "error"
        winrate_7d = f"{data['winrate'] * 100:.2f}%" if data['winrate'] is not None else "?"
        sol_balance = f"{float(data['sol_balance']):.2f}" if data['sol_balance'] is not None else "?"
        buy_7d = f"{data['buy_7d']}" if data['buy_7d'] is not None else "?"

        try:
            winrate_30data = self.sendRequest.get(
                f"https://gmgn.ai/defi/quotation/v1/smartmoney/sol/walletNew/{wallet}?period=30d", 
                headers=headers
            ).json()['data']
            winrate_30d = f"{winrate_30data['winrate'] * 100:.2f}%" if winrate_30data['winrate'] is not None else "?"
        except Exception as e:
            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Error fetching winrate 30d data, trying backup..")
            winrate_30data = self.cloudScraper.get(
                f"https://gmgn.ai/defi/quotation/v1/smartmoney/sol/walletNew/{wallet}?period=30d", 
                headers=headers
            ).json()['data']
            winrate_30d = f"{winrate_30data['winrate'] * 100:.2f}%" if winrate_30data['winrate'] is not None else "?"

        #try:
        #    total_profit_percent_value = float(data['total_profit_pnl']) * 100 if data['total_profit_pnl'] is not None else 0
        #except Exception:
        #    total_profit_percent_value = 0

        #if total_profit_percent_value <= 75:
        #    return None

        if "Skipped" in data.get("tags", []):
            return {
                "wallet": wallet,
                "tags": ["Skipped"],
                "directLink": direct_link
            }

        tokenDistro = self.getTokenDistro(wallet, useProxies)
        if filters["minAmount100"] and filters["minAmount100"] != 0 and tokenDistro.get("100%+") is not None and tokenDistro["100%+"] < filters["minAmount100"]:
            return None
        
        if filters["minAmount200"] and filters["minAmount200"] != 0 and tokenDistro.get("200%+") is not None and tokenDistro["200%+"] < filters["minAmount200"]:
            return None
        
        if filters["minAmount500"] and filters["minAmount500"] != 0 and tokenDistro.get("500%+") is not None and tokenDistro["500%+"] < filters["minAmount500"]:
            return None
        
        if filters["minAmount1000"] and filters["minAmount1000"] != 0 and tokenDistro.get("1000%+") is not None and tokenDistro["1000%+"] < filters["minAmount1000"]:
            return None

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
            "directLink": direct_link,
            "buy_7d": buy_7d
        }
    
    def fetchWalletData(self, wallets, threads, 
                        skipWallets,useProxies,
                        filters=None):
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(self.getWalletData, wallet.strip(), skipWallets, useProxies,filters): wallet for wallet in wallets}
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
                print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Missing 'wallet' key in result: {result}")

        if self.results and 'token_distribution' in self.results[0]:
            token_dist_keys = self.results[0]['token_distribution'].keys()
        else:
            token_dist_keys = []  
        
        if not result_dict:
            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No data fetched, exiting...")
            return
        
        identifier = self.shorten(list(result_dict)[0])
        filename = f"{identifier}_{random.randint(1111, 9999)}.csv"

        path = f"Dragon/data/Solana/BulkWallet/wallets_{filename}"

        try:
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
        except Exception as e:
            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Error saving data: {e}")
            return

        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Saved data for {len(result_dict.items())} wallets to {filename}")
