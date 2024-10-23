import random
import tls_client
import cloudscraper
import concurrent.futures
from fake_useragent import UserAgent
from threading import Lock
import time

ua = UserAgent(os='linux', browsers=['firefox'])

class ScanAllTx:

    def __init__(self):
        self.sendRequest = tls_client.Session(client_identifier='chrome_103')
        self.cloudScraper = cloudscraper.create_scraper()
        self.shorten = lambda s: f"{s[:4]}...{s[-5:]}" if len(s) >= 9 else s
        self.lock = Lock()
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


    def request(self, url: str, useProxies):
        retries = 3
        
        for attempt in range(retries):
            try:
                proxy = self.getNextProxy() if useProxies else None
                self.configureProxy(proxy)
                response = self.sendRequest.get(url, headers=self.headers, allow_redirects=True)
                if response.status_code == 200:
                    data = response.json()['data']['history']
                    paginator = response.json()['data'].get('next')
                    return data, paginator
            except Exception:
                print(f"[🐲] Error fetching data, trying backup...")
            finally:
                self.randomise()
                try:
                    proxy = self.getNextProxy() if useProxies else None
                    proxies = {'http': proxy, 'https': proxy} if proxy else None
                    response = self.cloudScraper.get(url, headers=self.headers, proxies=proxies, allow_redirects=True)
                    if response.status_code == 200:
                        data = response.json()['data']['history']
                        paginator = response.json()['data'].get('next')
                        return data, paginator
                except Exception:
                    print(f"[🐲] Backup scraper failed, retrying...")
            
            time.sleep(1)

        print(f"[🐲] Failed to fetch data after {retries} attempts for URL: {url}")
        return [], None

    def getAllTxMakers(self, contractAddress: str, threads: int, useProxies):
        base_url = f"https://gmgn.ai/defi/quotation/v1/trades/sol/{contractAddress}?limit=100"
        paginator = None
        urls = []
        
        print(f"[🐲] Starting... please wait.\n")

        while True:
            url = f"{base_url}&cursor={paginator}" if paginator else base_url
            urls.append(url)
            
            try:
                proxy = self.getNextProxy() if useProxies else None
                self.configureProxy(proxy)
                response = self.sendRequest.get(url, headers=self.headers, allow_redirects=True)
                if response.status_code != 200:
                    raise Exception("Error in initial request")
            except Exception:
                self.randomise()
                print(f"[🐲] Error fetching data, trying backup..")
                proxy = self.getNextProxy() if useProxies else None
                proxies = {'http': proxy, 'https': proxy} if proxy else None
                response = self.cloudScraper.get(url, headers=self.headers, proxies=proxies, allow_redirects=True)
            
            paginator = response.json()['data'].get('next')

            if not paginator:
                break

        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            future_to_url = {executor.submit(self.request, url, useProxies): url for url in urls}
            all_makers = set()

            for future in concurrent.futures.as_completed(future_to_url):
                history, _ = future.result()
                with self.lock: 
                    for maker in history:
                        event = maker['event']
                        if event == "buy":
                            print(f"[🐲] Wallet: {maker['maker']} | Hash: {maker['tx_hash']} | Type: {event}")
                            all_makers.add(maker['maker'])
        
        filename = f"wallets_{self.shorten(contractAddress)}__{random.randint(1111, 9999)}.txt"
        
        with open(f"Dragon/data/Solana/ScanAllTx/{filename}", "w") as file:
            for maker in sorted(all_makers):  
                file.write(f"{maker}\n")
        print(f"[🐲] Found and wrote {len(all_makers)} wallets from {contractAddress} to {filename}")
