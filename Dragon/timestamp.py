import random
import tls_client

from fake_useragent import UserAgent
import concurrent.futures
import time
import random

ua = UserAgent(os='linux', browsers=['firefox'])

class TimestampTransactions:

    def __init__(self):
        self.sendRequest = tls_client.Session(client_identifier='chrome_103')
        
        self.shorten = lambda s: f"{s[:4]}...{s[-5:]}" if len(s) >= 9 else s
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
            time.sleep(1)
        
        print(f"[🐲] Failed to fetch data after {retries} attempts.")
        return {}

    def getMintTimestamp(self, contractAddress, useProxies):
        url = f"https://gmgn.ai/defi/quotation/v1/tokens/sol/{contractAddress}"
        retries = 3

        for attempt in range(retries):
            self.randomise()
            try:
                proxy = self.getNextProxy() if useProxies else None
                self.configureProxy(proxy)
                response = self.sendRequest.get(url, headers=self.headers, allow_redirects=True).json()['data']['token']['creation_timestamp']
                return response
            except Exception:
                print(f"[🐲] Error fetching data, trying backup...")
            time.sleep(1)
        
        print(f"[🐲] Failed to fetch data after {retries} attempts.")
        return None

    def getTxByTimestamp(self, contractAddress, threads, start, end, useProxies):
        base_url = f"https://gmgn.ai/vas/api/v1/token_trades/sol/{contractAddress}"
        paginator = None
        urls = []
        all_trades = []
        
        print(f"[🐲] Starting... please wait.")

        start = int(start)
        end = int(end)

        while True:
            self.randomise()
            url = f"{base_url}&cursor={paginator}" if paginator else base_url
            urls.append(url)
            
            response = self.fetch_url(url, useProxies)
            trades = response.get('data', {}).get('history', [])
            
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
