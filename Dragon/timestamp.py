import random
import tls_client
import cloudscraper
from fake_useragent import UserAgent
import concurrent.futures
import time
import random

ua = UserAgent(os='linux', browsers=['firefox'])

class TimestampTransactions:

    def __init__(self):
        self.sendRequest = tls_client.Session(client_identifier='chrome_103')
        self.cloudScraper = cloudscraper.create_scraper()
        self.shorten = lambda s: f"{s[:4]}...{s[-5:]}" if len(s) >= 9 else s
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

    def fetch_url(self, url, useProxies):
        retries = 3
        for attempt in range(retries):
            try:
                proxy = self.getNextProxy() if useProxies else None
                self.configureProxy(proxy)
                response = self.sendRequest.get(url, headers=self.headers, allow_redirects=True).json()
                return response
            except Exception:
                print(f"[🐲] Error fetching data, trying backup...")
            finally:
                self.randomise()
                try:
                    proxy = self.getNextProxy() if useProxies else None
                    proxies = {'http': proxy, 'https': proxy} if proxy else None
                    response = self.cloudScraper.get(url, headers=self.headers, allow_redirects=True, proxies=proxies).json()
                    return response
                except Exception:
                    print(f"[🐲] Backup scraper failed, retrying...")
            
            time.sleep(1)
        
        print(f"[🐲] Failed to fetch data after {retries} attempts.")
        return {}

    def getMintTimestamp(self, contractAddress, useProxies):
        url = f"https://gmgn.ai/defi/quotation/v1/tokens/sol/{contractAddress}"
        retries = 3

        for attempt in range(retries):
            try:
                proxy = self.getNextProxy() if useProxies else None
                self.configureProxy(proxy)
                response = self.sendRequest.get(url, headers=self.headers, allow_redirects=True).json()['data']['token']['creation_timestamp']
                return response
            except Exception:
                print(f"[🐲] Error fetching data, trying backup...")
            finally:
                self.randomise()
                try:
                    proxy = self.getNextProxy() if useProxies else None
                    proxies = {'http': proxy, 'https': proxy} if proxy else None
                    response = self.cloudScraper.get(url, headers=self.headers, allow_redirects=True, proxies=proxies).json()['data']['token']['creation_timestamp']
                    return response
                except Exception:
                    print(f"[🐲] Backup scraper failed, retrying...")
            
            time.sleep(1)
        
        print(f"[🐲] Failed to fetch data after {retries} attempts.")
        return None

    def getTxByTimestamp(self, contractAddress, threads, start, end, useProxies):
        base_url = f"https://gmgn.ai/defi/quotation/v1/trades/sol/{contractAddress}?limit=100"
        paginator = None
        urls = []
        all_trades = []
        
        print(f"[🐲] Starting... please wait.")

        start = int(start)
        end = int(end)

        while True:
            url = f"{base_url}&cursor={paginator}" if paginator else base_url
            urls.append(url)
            
            response = self.fetch_url(url, useProxies)
            trades = response.get('data', {}, headers=self.headers, allow_redirects=True).get('history', [])
            
            if not trades or trades[-1]['timestamp'] < start:
                break

            paginator = response['data'].get('next')
            if not paginator:
                break
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            future_to_url = {executor.submit(self.fetch_url, url, useProxies): url for url in urls}
            for future in concurrent.futures.as_completed(future_to_url):
                response = future.result()
                trades = response.get('data', {}).get('history', [])
                filtered_trades = [trade for trade in trades if start <= trade['timestamp'] <= end]
                all_trades.extend(filtered_trades)

        wallets = []
        filename = f"Dragon/data/Solana/TimestampTxns/txns_{self.shorten(contractAddress)}__{random.randint(1111, 9999)}.txt"

        for trade in all_trades:
            wallets.append(trade.get("maker"))

        with open(filename, 'a') as f:
            for wallet in wallets:
                f.write(f"{wallet}\n")
        
        print(f"[🐲] {len(wallets)} trades successfully saved to {filename}")
