import datetime
import json
import tls_client
import cloudscraper
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import time

ua = UserAgent(os='linux', browsers=['firefox'])

class TopHolders:

    def __init__(self):
        self.sendRequest = tls_client.Session(client_identifier='chrome_103')
        self.cloudScraper = cloudscraper.create_scraper()
        self.shorten = lambda s: f"{s[:4]}...{s[-5:]}" if len(s) >= 9 else s
        self.allData = {}
        self.allAddresses = set()
        self.addressFrequency = defaultdict(int)
        self.totalTraders = 0
        self.proxyPosition = 0

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

    def getBondingCurve(self, contractAddress: str, useProxies):
        retries = 3
        headers = {
            "User-Agent": ua.random
        }
        url = f"https://gmgn.ai/defi/quotation/v1/tokens/sol/{contractAddress}"

        for attempt in range(retries):
            try:
                proxy = self.getNextProxy() if useProxies else None
                self.configureProxy(proxy)
                response = self.sendRequest.get(url, headers=headers)
                data = response.json().get('data', None)
                if data:
                    try:
                        bondingCurve = data['token']['pool_info']['pool_address']
                    except Exception:
                        bondingCurve = ""
                    return bondingCurve
            except Exception:
                print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Error fetching data on attempt, trying backup")
            finally:
                try:
                    proxy = self.getNextProxy() if useProxies else None
                    proxies = {'http': proxy, 'https': proxy} if proxy else None
                    response = self.cloudScraper.get(url, headers=headers, proxies=proxies)
                    data = response.json().get('data', None)
                    if data:
                        try:
                            bondingCurve = data['token']['pool_info']['pool_address']
                        except Exception:
                            bondingCurve = ""
                        return bondingCurve
                except Exception as e:
                    print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Error fetching data on attempt, trying backup {e}")
            time.sleep(1)
        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Failed to fetch data after {retries} attempts.")
        return ""


    def fetchTopHolders(self, contractAddress: str, useProxies):
        url = f"https://gmgn.ai/defi/quotation/v1/tokens/top_holders/sol/{contractAddress}?orderby=amount_percentage&direction=desc"
        retries = 3
        headers = {
            "User-Agent": ua.random
        }
        
        for attempt in range(retries):
            try:
                proxy = self.getNextProxy() if useProxies else None
                self.configureProxy(proxy)
                response = self.sendRequest.get(url, headers=headers)
                data = response.json().get('data', None)
                if data:
                    return data
            except Exception:
                print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Error fetching data on attempt, trying backup...")
            finally:
                try:
                    proxy = self.getNextProxy() if useProxies else None
                    proxies = {'http': proxy, 'https': proxy} if proxy else None
                    response = self.cloudScraper.get(url, headers=headers, proxies=proxies)
                    data = response.json().get('data', None)
                    if data:
                        return data
                except Exception:
                    print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Backup scraper failed, retrying...")
                    
            time.sleep(1)
        
        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Failed to fetch data after {retries} attempts.")
        return []

    def topHolderData(self, contractAddresses, threads, useProxies):
        
        excludeAddress = ["5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1", "TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM"]

        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(self.fetchTopHolders, address, useProxies): address for address in contractAddresses}

            for future in as_completed(futures):
                contract_address = futures[future]
                response = future.result()
                
                bondingCurve = self.getBondingCurve(contract_address, useProxies)
                excludeAddress.append(bondingCurve)
                self.allData[contract_address] = {}
                self.totalTraders += len(response)

                for top_trader in response:
                    
                    if top_trader['address'] in excludeAddress or top_trader['cost_cur'] < 50:
                        continue

                    multiplier_value = top_trader['profit_change']
                    
                    if multiplier_value:
                        address = top_trader['address']
                        self.addressFrequency[address] += 1 
                        self.allAddresses.add(address)
                        
                        bought_usd = f"${top_trader['total_cost']:,.2f}"
                        total_profit = f"${top_trader['realized_profit']:,.2f}"
                        unrealized_profit = f"${top_trader['unrealized_profit']:,.2f}"
                        multiplier = f"{multiplier_value:.2f}x"
                        buys = f"{top_trader['buy_tx_count_cur']}"
                        sells = f"{top_trader['sell_tx_count_cur']}"
                        
                        self.allData[address] = {
                            "boughtUsd": bought_usd,
                            "totalProfit": total_profit,
                            "unrealizedProfit": unrealized_profit,
                            "multiplier": multiplier,
                            "buys": buys,
                            "sells": sells
                        }
        
        repeatedAddresses = [address for address, count in self.addressFrequency.items() if count > 1]
        
        identifier = self.shorten(list(self.allAddresses)[0])
        
        with open(f'Dragon/data/Solana/TopHolders/allTopAddresses_{identifier}.txt', 'w') as av:
            for address in self.allAddresses:
                av.write(f"{address}\n")

        if len(repeatedAddresses) != 0:
            with open(f'Dragon/data/Solana/TopHolders/repeatedTopTraders_{identifier}.txt', 'w') as ra:
                for address in repeatedAddresses:
                    ra.write(f"{address}\n")
            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Saved {len(repeatedAddresses)} repeated addresses to repeatedTopTraders_{identifier}.txt")

        with open(f'Dragon/data/Solana/TopHolders/topTraders_{identifier}.json', 'w') as tt:
            json.dump(self.allData, tt, indent=4)

        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Saved {self.totalTraders} top traders for {len(contractAddresses)} tokens to allTopAddresses_{identifier}.txt")
        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Saved {len(self.allAddresses)} top trader addresses to topTraders_{identifier}.json")

        return
