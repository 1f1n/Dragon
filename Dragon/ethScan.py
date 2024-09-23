import random
import tls_client
import cloudscraper
import concurrent.futures
from fake_useragent import UserAgent
from threading import Lock
import time

ua = UserAgent(os='linux', browsers=['firefox'])

class EthScanAllTx:

    def __init__(self):
        self.sendRequest = tls_client.Session(client_identifier='chrome_103')
        self.cloudScraper = cloudscraper.create_scraper()
        self.shorten = lambda s: f"{s[:4]}...{s[-5:]}" if len(s) >= 9 else s
        self.lock = Lock()

    def request(self, url: str):
        headers = {
            "User-Agent": ua.random
        }
        retries = 3
        
        for attempt in range(retries):
            try:
                response = self.sendRequest.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()['data']['history']
                    paginator = response.json()['data'].get('next')
                    return data, paginator
            except Exception:
                print(f"[🐲] Error fetching data, trying backup...")
            finally:
                try:
                    response = self.cloudScraper.get(url, headers=headers)
                    if response.status_code == 200:
                        data = response.json()['data']['history']
                        paginator = response.json()['data'].get('next')
                        return data, paginator
                except Exception:
                    print(f"[🐲] Backup scraper failed, retrying...")
            
            time.sleep(1)

        print(f"[🐲] Failed to fetch data after {retries} attempts for URL: {url}")
        return [], None

    def getAllTxMakers(self, contractAddress: str, threads: int):
        base_url = f"https://gmgn.ai/defi/quotation/v1/trades/eth/{contractAddress}?limit=100"
        paginator = None
        urls = []

        headers = {
            "User-Agent": ua.random
        }
        
        print(f"[🐲] Starting... please wait.\n")

        while True:
            url = f"{base_url}&cursor={paginator}" if paginator else base_url
            urls.append(url)
            
            try:
                response = self.sendRequest.get(url, headers=headers)
                if response.status_code != 200:
                    raise Exception("Error in initial request")
            except Exception:
                print(f"[🐲] Error fetching data, trying backup..")
                response = self.cloudScraper.get(url, headers=headers)
            paginator = response.json()['data'].get('next')

            if not paginator:
                break

        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            future_to_url = {executor.submit(self.request, url): url for url in urls}
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
        
        with open(f"Dragon/data/Ethereum/ScanAllTx/{filename}", "w") as file:
            for maker in sorted(all_makers):  
                file.write(f"{maker}\n")
        print(f"[🐲] Found and wrote {len(all_makers)} wallets from {contractAddress} to {filename}")
