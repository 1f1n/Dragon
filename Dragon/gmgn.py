import time
import random
import tls_client
import cloudscraper
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor, as_completed

class GMGN:

    def __init__(self):
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
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'dnt': '1',
            'priority': 'u=0, i',
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
    
    def newToken(self):
        url = "https://gmgn.ai/defi/quotation/v1/rank/sol/pump/1h?limit=100&orderby=created_timestamp&direction=desc&new_creation=true"
        return url
    
    def completingToken(self):
        url = "https://gmgn.ai/defi/quotation/v1/rank/sol/pump/1h?limit=100&orderby=progress&direction=desc&pump=true"
        return url
    
    def soaringToken(self):
        url = "https://gmgn.ai/defi/quotation/v1/rank/sol/pump/1h?limit=100&orderby=market_cap_5m&direction=desc&soaring=true"
        return url

    def bondedToken(self):
        url = "https://gmgn.ai/defi/quotation/v1/pairs/sol/new_pairs/1h?limit=100&orderby=market_cap&direction=desc&launchpad=pump&period=1h&filters[]=not_honeypot&filters[]=pump"
        return url
    
    def fetchContracts(self, urlIndicator, useProxies):
        retries = 3

        contracts = set()

        if urlIndicator == "NewToken":
            url = self.newToken()
        elif urlIndicator == "CompletingToken":
            url = self.completingToken()
        elif urlIndicator == "SoaringToken":
            url = self.soaringToken()
        else:
            url = self.bondedToken()

        for attempt in range(retries):
            try:
                self.randomise()
                proxy = self.getNextProxy() if useProxies else None
                self.configureProxy(proxy)
                response = self.sendRequest.get(url, headers=self.headers, allow_redirects=True)
                if response.status_code == 200:

                    if urlIndicator == "BondedToken":
                        data = response.json().get('data', {}).get('pairs', [])
                    else:
                        data = response.json().get('data', {}).get('rank', [])
                        
                    for item in data:
                        if item.get('address') and item.get('address') != "":
                            contract = item.get('address')
                            contracts.add(contract)
            except Exception as e:
                print(f"[🐲] Error fetching data on attempt, trying backup... {e}")
            finally:
                self.randomise()
                try:
                    proxy = self.getNextProxy() if useProxies else None
                    proxies = {'http': proxy, 'https': proxy} if proxy else None
                    response = self.cloudScraper.get(url, headers=self.headers, proxies=proxies, allow_redirects=True)

                    if response.status_code == 200:                        
                        if urlIndicator == "BondedToken":
                            data = response.json().get('data', {}).get('pairs', [])
                        else:
                            data = response.json().get('data', {}).get('rank', [])
                        for item in data:
                            if item.get('address') and item.get('address') != "":
                                contract = item.get('address')
                                contracts.add(contract)
                except Exception as e:
                    print(f"[🐲] Backup scraper failed, retrying... {e}")
        time.sleep(1)

        return list(contracts)

    def contractsData(self, urlIndicator, threads, useProxies):
        contract_addresses = set()

        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(self.fetchContracts, urlIndicator, useProxies) for _ in range(threads)]
            for future in as_completed(futures):
                contract_addresses.update(future.result())
        
        identifier = self.shorten(list(contract_addresses)[0])

        with open(f"Dragon/data/GMGN/{urlIndicator}/contracts_{identifier}.txt", "w") as file:
            for address in contract_addresses:
                file.write(f"{address}\n")
        print(f"[🐲] {len(contract_addresses)} contract addresses have been written to Dragon/data/GMGN/{urlIndicator}/contracts_{identifier}.txt")
