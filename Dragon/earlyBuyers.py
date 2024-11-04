import json
import time
import random
import tls_client
import cloudscraper
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

class EarlyBuyers:

    def __init__(self):
        self.cloudScraper = cloudscraper.create_scraper()
        self.shorten = lambda s: f"{s[:4]}...{s[-5:]}" if len(s) >= 9 else s
        self.allData = {}
        self.allAddresses = set()
        self.addressFrequency = defaultdict(int)
        self.totalBuyers = 0
        self.proxyPosition = 0
    
    def randomise(self):
        self.identifier = random.choice([browser for browser in tls_client.settings.ClientIdentifiers.__args__ if browser.startswith(('chrome', 'safari', 'firefox', 'opera'))])
        self.sendRequest = tls_client.Session(random_tls_extension_order=True, client_identifier=self.identifier)

        parts = self.identifier.split('_')
        identifier, version, *rest = parts
        other = rest[0] if rest else None
        
        os = 'windows'
        if identifier == 'opera':
            identifier = 'chrome'
        elif version == 'ios':
            os = 'ios'
        else:
            os = 'windows'

        self.user_agent = UserAgent(browsers=[identifier], os=[os]).random

        self.headers = {
            'Host': 'gmgn.ai',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'dnt': '1',
            'priority': 'u=1, i',
            'referer': 'https://gmgn.ai/?chain=sol',
            'user-agent': self.user_agent
        }

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
            self.sendRequest.proxies = {
                'http': proxy.get('http'),
                'https': proxy.get('https')
            }
        elif isinstance(proxy, str):
            self.sendRequest.proxies = {
                'http': proxy,
                'https': proxy
            }
        else:
            self.sendRequest.proxies = None
        return proxy
    
    def getNextProxy(self):
        proxies = self.loadProxies()
        proxy = proxies[self.proxyPosition % len(proxies)]
        self.proxyPosition += 1
        return proxy
    
    def fetchEarlyBuyers(self, contractAddress: str, useProxies, buyers):
        url = f"https://gmgn.ai/defi/quotation/v1/trades/sol/{contractAddress}?revert=true"
        retries = 3

        for attempt in range(retries):
            try:
                self.randomise()
                proxy = self.getNextProxy() if useProxies else None
                self.configureProxy(proxy)
                response = self.sendRequest.get(url, headers=self.headers, allow_redirects=True)
                data = response.json().get('data', {}).get('history', [])
                if isinstance(data, list):
                    for item in data:
                        if item.get('event') == "buy" and "creator" not in item.get('maker_token_tags'):
                            return data
            except Exception as e:
                print(f"[🐲] Error fetching data on attempt, trying backup... {e}")
            finally:
                self.randomise()
                try:
                    proxy = self.getNextProxy() if useProxies else None
                    proxies = {'http': proxy, 'https': proxy} if proxy else None
                    response = self.cloudScraper.get(url, headers=self.headers, proxies=proxies, allow_redirects=True)
                    data = response.json().get('data', {}).get('history', [])
                    if isinstance(data, list):
                        for item in data:
                            if item.get('event') == "buy" and "creator" not in item.get('maker_token_tags'):
                                return data
                except Exception as e:
                    print(f"[🐲] Backup scraper failed, retrying...")
        time.sleep(1)

        print(f"[🐲] Failed to fetch data after {retries} attempts.")
        return []

    def earlyBuyersdata(self, contractAddresses, threads, useProxies, buyers):
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(self.fetchEarlyBuyers, address, useProxies, buyers): address for address in contractAddresses}

            for future in as_completed(futures):
                contract_address = futures[future]
                response = future.result() 
                limited_response = response[:buyers] if len(response) >= buyers else response

                if contract_address not in self.allData:
                    self.allData[contract_address] = []

                self.totalBuyers += len(limited_response)

                for earlyBuyer in limited_response:
                    address = earlyBuyer['maker']
                    print(address)

                    if address:
                        self.addressFrequency[address] += 1
                        self.allAddresses.add(address)

                        bought_usd = f"${earlyBuyer['amount_usd']:,.2f}" if earlyBuyer['amount_usd'] is not None else "?"
                        total_profit = f"${earlyBuyer['realized_profit']:,.2f}" if earlyBuyer['realized_profit'] is not None else "?"
                        unrealized_profit = f"${earlyBuyer['unrealized_profit']:,.2f}" if earlyBuyer['unrealized_profit'] is not None else "?"
                        trades = f"{earlyBuyer['total_trade']}" if earlyBuyer['total_trade'] is not None else "?"

                        buyer_data = {
                            "boughtUsd": bought_usd,
                            "totalProfit": total_profit,
                            "unrealizedProfit": unrealized_profit,
                            "trades": trades,
                        }
                        self.allData[contract_address].append({address: buyer_data})

        repeatedAddresses = [address for address, count in self.addressFrequency.items() if count > 1]
        identifier = self.shorten(list(self.allAddresses)[0])

        with open(f'Dragon/data/Solana/EarlyBuyers/allTopAddresses_{identifier}.txt', 'w') as av:
            for address in self.allAddresses:
                av.write(f"{address}\n")

        if len(repeatedAddresses) != 0:
            with open(f'Dragon/data/Solana/EarlyBuyers/repeatedEarlyBuyers_{identifier}.txt', 'w') as ra:
                for address in repeatedAddresses:
                    ra.write(f"{address}\n")
            print(f"[🐲] Saved {len(repeatedAddresses)} repeated addresses to repeatedEarlyBuyers_{identifier}.txt")

        with open(f'Dragon/data/Solana/EarlyBuyers/EarlyBuyers_{identifier}.json', 'w') as tt:
            json.dump(self.allData, tt, indent=4)

        print(f"[🐲] Saved {self.totalBuyers} early buyers for {len(contractAddresses)} tokens to allTopAddresses_{identifier}.txt")
        print(f"[🐲] Saved {len(self.allAddresses)} early buyer addresses to EarlyBuyers_{identifier}.json")

        return
