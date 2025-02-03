import json
import random
import tls_client

from fake_useragent import UserAgent
import time

ua = UserAgent(os='linux', browsers=['firefox'])

class BundleFinder:

    def __init__(self):
        self.txHashes = set()
        self.formatTokens = lambda x: float(x) / 1_000_000
        self.sendRequest = tls_client.Session(client_identifier='chrome_103')
        
        self.shorten = lambda s: f"{s[:4]}...{s[-5:]}" if len(s) >= 9 else "?"
    
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
    
    def prettyPrint(self, bundleData: dict, contractAddress: str):
        isBundled = bundleData['bundleDetected']
        developerInformation = bundleData['developerInfo']
        transactions = bundleData['transactions']
        bundledAmount = developerInformation['bundledAmount']
        bundledPercentage = developerInformation['percentageOfSupply']

        text = (
            f"[🐲] Bundled: ✅\n" if isBundled else f"[🐲] Bundled: ❌\n"
            f"[🐲] Transactions: {transactions:,}"
        )

        text += f"\n[🐲] Total Amount: {bundledAmount:,.2f}\n[🐲] Total Percentage: {bundledPercentage * 100:,.2f}%"

        filename = f"bundle_{self.shorten(contractAddress)}_{random.randint(1111, 9999)}.json"

        with open(f'Dragon/data/Solana/bundleData/{filename}', 'w') as f:
            json.dump(bundleData, f, indent=4)

        text += f"\n[🐲] Saved data to {filename}\n"

        return text

    def teamTrades(self, contractAddress):
        url = f"https://gmgn.ai/defi/quotation/v1/trades/sol/{contractAddress}?limit=100&maker=&tag%5B%5D=creator&tag%5B%5D=dev_team"
        retries = 3
        
        for attempt in range(retries):
            self.randomise()
            try:
                info = self.sendRequest.get(f"https://gmgn.ai/defi/quotation/v1/tokens/sol/{contractAddress}", headers=self.headers, allow_redirects=True).json()
                response = self.sendRequest.get(url, headers=self.headers, allow_redirects=True).json()['data']['history']
                break
            except Exception:
                print(f"[🐲] Error fetching data on attempt, trying backup..")
            finally:
                self.randomise()
                try:
                    info = self.cloudScraper.get(f"https://gmgn.ai/defi/quotation/v1/tokens/sol/{contractAddress}", headers=self.headers, allow_redirects=True).json()
                    response = self.sendRequest.get(url, headers=self.headers, allow_redirects=True).json()['data']['history']
                    break
                except Exception:
                    print(f"[🐲] Backup scraper failed, retrying...")
            
            time.sleep(1)  


        totalSupply = info['total_supply']
    
        for buy in response:
            if buy['event'] == "buy":
                self.txHashes.add(buy['tx_hash'])

        return self.txHashes, totalSupply

    def checkBundle(self, txHashes: set, totalSupply: int):
        total_amount = 0.00
        transactions = 0

        data = {
            "transactions": 0,
            "totalAmount": 0.00,
            "bundleDetected": False,
            "transactionDetails": {}
        }

        for txHash in self.txHashes:
            url = f"https://api.solana.fm/v0/transfers/{txHash}"
            retries = 3
            
            for attempt in range(retries):
                try:
                    response = self.sendRequest.get(url).json().get('result', {}).get('data', [])
                    if response:
                        break
                except Exception as e:
                    print(f"[🐲] Error fetching transaction data for {txHash} on attempt {attempt + 1}.")
                time.sleep(1)

            if isinstance(response, list):
                for action in response:
                    if action.get('action') == "transfer" and action.get("token") != "":
                        amount = self.formatTokens(action.get('amount'))
                        total_amount += amount
                        transactions += 1

        data['transactions'] = transactions
        data['totalAmount'] = total_amount

        if transactions > 1:
            data['bundleDetected'] = True

        transactionsDetails = {}

        for txHash in txHashes:
            url = f"https://api.solana.fm/v0/transfers/{txHash}"
            
            for attempt in range(retries):
                try:
                    response = self.sendRequest.get(url).json().get('result', {}).get('data', [])
                    if response:
                        break
                except Exception as e:
                    print(f"Error fetching transaction data for {txHash} on attempt {attempt + 1}.")
                time.sleep(1)

            if isinstance(response, list):
                amounts = []
                for action in response:    
                    if action.get('action') == "transfer" and action.get("token") != "":
                        amount = self.formatTokens(action.get('amount'))
                        amounts.append(amount)
                if amounts:
                    amountsPercentages = [(amount / totalSupply * 100) for amount in amounts]
                    
                    transactionsDetails[txHash] = {
                        "amounts": amounts,
                        "amountsPercentages": amountsPercentages
                    }

        data['transactionDetails'] = transactionsDetails

        developerInfo = {
            "bundledAmount": total_amount,
            "percentageOfSupply": total_amount / totalSupply
        }

        data['developerInfo'] = developerInfo
        
        return data
