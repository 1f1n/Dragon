import json
import time
import random
import tls_client

from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from threading import Event

globalRatelimitEvent = Event()

class EarlyBuyers:

    def __init__(self):
        self.shorten = lambda s: f"{s[:4]}...{s[-5:]}" if len(s) >= 9 else s
        self.allData = {}
        self.allAddresses = set()
        self.addressFrequency = defaultdict(int)
        self.totalBuyers = 0
        self.proxyPosition = 0

    def randomise(self):
        self.identifier = random.choice(
            [browser for browser in tls_client.settings.ClientIdentifiers.__args__
             if browser.startswith(('chrome', 'safari', 'firefox', 'opera'))]
        )
        parts = self.identifier.split('_')
        identifier, version, *rest = parts
        identifier = identifier.capitalize()
        
        self.sendRequest = tls_client.Session(random_tls_extension_order=True, client_identifier=self.identifier)
        self.sendRequest.timeout_seconds = 60

        if identifier == 'Opera':
            identifier = 'Chrome'
            osType = 'Windows'
        elif version.lower() == 'ios':
            osType = 'iOS'
        else:
            osType = 'Windows'

        try:
            self.user_agent = UserAgent(os=[osType]).random
        except Exception:
            self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0"

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
        url = f"https://gmgn.ai/vas/api/v1/token_trades/sol/{contractAddress}?revert=true"
        retries = 3

        for attempt in range(retries):
            try:
                if globalRatelimitEvent.is_set():
                    print(f"[🐲] Global rate limit active. Waiting before fetching early buyers for contract {contractAddress}...")
                    globalRatelimitEvent.wait()
                    
                self.randomise()
                proxy = self.getNextProxy() if useProxies else None
                self.configureProxy(proxy)
                response = self.sendRequest.get(url, headers=self.headers, allow_redirects=True)
                
                if response.status_code == 429:
                    print(f"[🐲] Received 429 for contract {contractAddress}. Triggering global cooldown for 7.5 seconds...")
                    globalRatelimitEvent.set()
                    time.sleep(7.5)
                    globalRatelimitEvent.clear()
                    continue

                data = response.json().get('data', {}).get('history', [])
                if isinstance(data, list):
                    for item in data:
                        if item.get('event') == "buy" and "creator" not in item.get('maker_token_tags'):
                            return data
            except Exception as e:
                print(f"[🐲] Error fetching data on attempt {attempt+1} for contract {contractAddress}: {e}")
            time.sleep(1)

        print(f"[🐲] Failed to fetch data after {retries} attempts for contract {contractAddress}.")
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
                    address = earlyBuyer.get('maker')
                    if address:
                        self.addressFrequency[address] += 1
                        self.allAddresses.add(address)

                        bought_usd = f"${float(earlyBuyer['amount_usd']):,.2f}" if earlyBuyer.get('amount_usd') not in (None, "") else "?"
                        total_profit = f"${float(earlyBuyer['realized_profit']):,.2f}" if earlyBuyer.get('realized_profit') not in (None, "") else "?"
                        unrealized_profit = f"${float(earlyBuyer['unrealized_profit']):,.2f}" if earlyBuyer.get('unrealized_profit') not in (None, "") else "?"
                        trades = str(earlyBuyer.get('total_trade', "?"))

                        buyer_data = {
                            "boughtUsd": bought_usd,
                            "totalProfit": total_profit,
                            "unrealizedProfit": unrealized_profit,
                            "trades": trades,
                        }
                        self.allData[contract_address].append({address: buyer_data})

        repeatedAddresses = [address for address, count in self.addressFrequency.items() if count > 1]

        if not self.allAddresses:
            print(f"[🐲] No early buyers found for {len(contractAddresses)} token(s).")
            return

        identifier = self.shorten(next(iter(self.allAddresses)))

        with open(f'Dragon/data/Solana/EarlyBuyers/allTopAddresses_{identifier}.txt', 'w') as av:
            for address in self.allAddresses:
                av.write(f"{address}\n")

        if repeatedAddresses:
            with open(f'Dragon/data/Solana/EarlyBuyers/repeatedEarlyBuyers_{identifier}.txt', 'w') as ra:
                for address in repeatedAddresses:
                    ra.write(f"{address}\n")
            print(f"[🐲] Saved {len(repeatedAddresses)} repeated addresses to repeatedEarlyBuyers_{identifier}.txt")

        with open(f'Dragon/data/Solana/EarlyBuyers/EarlyBuyers_{identifier}.json', 'w') as tt:
            json.dump(self.allData, tt, indent=4)

        print(f"[🐲] Saved {self.totalBuyers} early buyers for {len(contractAddresses)} tokens to allTopAddresses_{identifier}.txt")
        print(f"[🐲] Saved {len(self.allAddresses)} early buyer addresses to EarlyBuyers_{identifier}.json")
