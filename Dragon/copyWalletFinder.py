import random
import tls_client
import cloudscraper
import concurrent.futures
from fake_useragent import UserAgent
from threading import Lock
import time
import base64

ua = UserAgent(os='linux', browsers=['firefox'])

class CopyTradeWalletFinder:

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
        headers = {
            "User-Agent": ua.random
        }
        retries = 3

        for attempt in range(retries):
            self.randomise()
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
                    response = self.cloudScraper.get(url, headers=self.headers, allow_redirects=True, proxies=proxies)
                    if response.status_code == 200:
                        data = response.json()['data']['history']
                        paginator = response.json()['data'].get('next')
                        return data, paginator
                except Exception:
                    print(f"[🐲] Backup scraper failed, retrying...")

            time.sleep(1)

        print(f"[🐲] Failed to fetch data after {retries} attempts for URL: {url}")
        return [], None

    def findWallets(self, contractAddress: str, targetMaker: str, threads: int, useProxies):
        base_url = f"https://gmgn.ai/defi/quotation/v1/trades/sol/{contractAddress}?limit=100&event=buy"
        paginator = None
        urls = []

        print(f"\n[🐲] Starting... please wait.\n")

        while True:
            self.randomise()
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
                response = self.cloudScraper.get(url, headers=self.headers, allow_redirects=True, proxies=proxies)
            paginator = response.json()['data'].get('next')

            if paginator:
                print(f"[🐲] Page: {base64.b64decode(paginator).decode('utf-8')}", end="\r")

            if not paginator:
                break

        found_target = False
        temp_makers = []  

        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            future_to_url = {executor.submit(self.request, url, useProxies): url for url in urls}

            for future in concurrent.futures.as_completed(future_to_url):
                history, _ = future.result()
        
                with self.lock:
                    for maker in history:
                        event = maker['event']
                        txns = maker.get('total_trade', 0)
                        if event == "buy" and txns < 200:                            
                            if maker['maker'] == targetMaker:
                                found_target = True
                                break
                            
                            if maker['maker'] not in temp_makers:
                                temp_makers.append(maker['maker'])

                if found_target:
                    break

        makers = temp_makers[-10:]  

        if found_target:
            print(f"[🐲] Found target maker: {targetMaker}")
            print(f"[🐲] The first 10 makers ahead of target maker:")
            for idx, maker in enumerate(makers, 1):
                print(f"{idx}. {maker}")
        else:
            print(f"[🐲] Target maker {targetMaker} not found.")

        filename = f"wallets_after_{self.shorten(targetMaker)}_{random.randint(1111, 9999)}.txt"
        with open(f"Dragon/data/Solana/CopyWallets/{filename}", "w") as file:
            for maker in makers:
                file.write(f"{maker}\n")
        print(f"[🐲] Saved the 10 makers after {targetMaker} to {filename}")
