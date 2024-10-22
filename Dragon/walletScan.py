import datetime

import tls_client
from fake_useragent import UserAgent
from threading import Lock
import random
import time
import base58
import concurrent.futures
import threading

from solana.rpc.api import Client
from solders.pubkey import Pubkey


ua = UserAgent(os='linux', browsers=['firefox'])


class WalletScan:

    def __init__(self):
        self.sendRequest = tls_client.Session(client_identifier='chrome_103')
        self.shorten = lambda s: f"{s[:4]}...{s[-5:]}" if len(s) >= 9 else s
        self.lock = Lock()
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

    def request(self, url: str, useProxies):
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
                    data = response.json()['data']['history']
                    paginator = response.json()['data'].get('next')
                    return data, paginator
            except Exception:
                print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Error fetching data, trying backup...")
            finally:
                try:
                    proxy = self.getNextProxy() if useProxies else None
                    proxies = {'http': proxy, 'https': proxy} if proxy else None
                    response = self.cloudScraper.get(url, headers=headers, proxies=proxies)
                    if response.status_code == 200:
                        data = response.json()['data']['history']
                        paginator = response.json()['data'].get('next')
                        return data, paginator
                except Exception:
                    print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Backup scraper failed, retrying...")

            time.sleep(1)

        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Failed to fetch data after {retries} attempts for URL: {url}")
        return [], None

    def decode_base58_address(self, address: str) -> bytes:
        decoded = base58.b58decode(address)
        if len(decoded) != 32:
            raise ValueError(f"Invalid address length: expected 32 bytes, got {len(decoded)} bytes.")
        return decoded

    def decode_base58_sig(self, sig: str) -> bytes:
        decoded = base58.b58decode(sig)
        return decoded

    def getAllWallets(self, contractAddress: str, start_time: int, end_time: int, threads: int, rpc: str):
        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Scanning all wallets for {contractAddress} between {start_time} and {end_time}")

        client = Client(
            rpc
        )
    
        try:
            target_address_bytes = self.decode_base58_address(contractAddress)
            target_pubkey = Pubkey(target_address_bytes)
        except ValueError as e:
            print(f"Error decoding target address: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error initializing Pubkey: {e}")
            return []
    
        senders = set()
        senders_lock = threading.Lock()

        def process_transactions(signatures):
            
            nonlocal senders
            for sig_info in signatures:
                block_time = sig_info.block_time
                if block_time is None:
                    continue
    
                try:
                    # Fetch transaction details
                    tx = client.get_transaction(sig_info.signature, encoding='jsonParsed',
                                                max_supported_transaction_version=0)
                except:
                    continue

                if not tx.value:
                    continue

                transaction = tx.value.transaction.transaction
                meta = tx.value.transaction.meta

                if meta.err:
                    continue

                for instr in transaction.message.instructions:
                    try:
                        if not hasattr(instr, 'parsed') or not hasattr(instr, 'program'):
                            continue

                        if isinstance(instr.parsed, dict):
                            if instr.program == 'system' and instr.parsed.get('type') == 'transfer':
                                info = instr.parsed.get('info')
                                sender = info.get('source')
                                recipient = info.get('destination')

                                if recipient == contractAddress:
                                    with senders_lock:  # Ensure thread-safe access
                                        senders.add(sender)

                        elif 'data' in instr:
                            print(f"Partially decoded instruction: {instr}")
                            continue

                    except Exception as e:
                        print(f"Error processing instruction: {e}")
                        continue

        def fetch_signatures(before):
            nonlocal senders
            runLoop = True
            signatures = []
    
            while runLoop:
                try:
                    response = client.get_signatures_for_address(target_pubkey, before=before, limit=1000)
                    if not response.value:
                        break
                except Exception as e:
                    time.sleep(2)
                    continue
                
                if response.value[-1].block_time < start_time:
                    for sig_info in response.value:
                        block_time = sig_info.block_time
                        if block_time is None:
                            continue
    
                        if block_time < end_time:
                            runLoop = False
                            break
    
                        if block_time >= end_time and block_time <= start_time:
                            signatures.append(sig_info)

                before = response.value[-1].signature
        
    
                time.sleep(0.5)
    
            return signatures
    
        signatures = fetch_signatures(None)

        def split_list(lst, n):
            k, m = divmod(len(lst), n)
            return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]
        
        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Got all signatures in the time frame. Processing...")

        signature_chunks = split_list(signatures, threads)

        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(process_transactions, chunk) for chunk in signature_chunks]
            concurrent.futures.wait(futures)
    
        filename = f"wallets_{self.shorten(contractAddress)}__{random.randint(1111, 9999)}.txt"
        with open(f"Dragon/data/Solana/ScanWallet/{filename}", "w") as file:
            for sender in sorted(senders):
                file.write(f"{sender}\n")
        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Found and wrote {len(senders)} wallets from {contractAddress} to {filename}")

