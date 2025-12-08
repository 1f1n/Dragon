from Dragon import (
    BundleFinder, ScanAllTx, BulkWalletChecker, TopTraders, TimestampTransactions,
    CopyTradeWalletFinder, TopHolders, EarlyBuyers,
    EthBulkWalletChecker, EthTopTraders, EthTimestampTransactions, EthScanAllTx,
    utils, checkProxyFile, updateDragon,
    BscBulkWalletChecker, BscTopTraders,
    gmgnTools, GMGN
)

purgeFilesUtil = utils.purgeFiles
clearScreen = utils.clear
bannerText = utils.banner()

"""
Dragon is a comprehensive blockchain analysis tool that provides a modular, interactive command-line interface for 
exploring blockchain data across multiple cryptocurrencies (Solana, Ethereum, Binance Smart Chain, and GMGN). The script offers a 
centralized entry point for various blockchain-specific analytical tools, featuring robust user interaction 
mechanisms with key functions like:

1. User Input Handling:
- Thread configuration (getThreads())
- Proxy settings management (getProxiesSetting())
- File selection (selectFile())
- Contract address validation (getContractAddress())
- Wallet filtering options (promptSkipWallets())

2. Blockchain-Specific Modules:
- GMGN: Supports token data collection across different categories (new, completing, soaring, bonded tokens)
- Ethereum: Provides wallet checking, top trader analysis, timestamp transactions, and transaction scanning
- Solana: Offers comprehensive tools including timestamp transactions, bundle finding, transaction scanning, wallet checking, copy trade detection, top holders, and early buyer identification
- Binance Smart Chain: Supports wallet checking and top trader analysis

The script serves as a centralized hub for blockchain research and analysis, allowing users to interactively select chains and perform various analytical 
tasks with customizable settings like thread count and proxy usage. Its design emphasizes user-friendliness through intuitive menus, input validation, and error handling.
"""

def getThreads(defaultThreads=40, maxAllowed=100):
    while True:
        threadsInput = input("[❓] Threads > ")
        try:
            threads = int(threadsInput)
            if threads > maxAllowed:
                print(f"[🐲] Using a maximum of {maxAllowed} threads. Automatically set to {defaultThreads}.")
                return defaultThreads
            return threads
        except ValueError:
            print(f"[🐲] Invalid input. Defaulting to {defaultThreads} threads.")
            return defaultThreads

def getProxiesSetting():
    while True:
        proxiesInput = input("[❓] Use Proxies? (Y/N) > ").strip().lower()
        proxyCheck = checkProxyFile()
        if not proxyCheck and proxiesInput != "n":
            print("[🐲] Dragon/data/Proxies/proxies.txt is empty. Continuing without proxies.")
            return False
        if proxiesInput == "y":
            print("[🐲] Using proxies.")
            return True
        elif proxiesInput == "n":
            return False
        else:
            print("[🐲] Invalid input. Please enter Y or N.")

def getSolanaContracts():
    utils.selectContractAddressInput()

    while True:
        try:
            method = int(input("[❓] Choice > ").strip())

            if method == 1:
                entry = input("[🐲] Enter contract address(es), comma separated > ").strip()
                items = [e.strip() for e in entry.split(",") if len(e.strip()) > 0]
                if items:
                    print(f"[🐲] Loaded {len(items)} contract(s).")
                    return items
                print("[🐲] No valid contracts entered.")

            elif method == 2:
                return selectFile("Solana")

            elif method == 3:
                filePath = input("[🐲] Enter full file path > ").strip()
                try:
                    with open(filePath, "r") as f:
                        items = f.read().splitlines()
                    if items:
                        print(f"[🐲] Loaded {len(items)} contract(s).")
                        return items
                    print("[🐲] File is empty.")
                except Exception as e:
                    print(f"[🐲] Error loading file: {e}")

            else:
                print("[🐲] Invalid choice.")

        except ValueError:
            print("[🐲] Invalid input, try again.")


def selectFile(chainName):
    filesChoice, files = utils.searchForTxt(chain=chainName)
    print("\n[🐲] Available files:\n" + filesChoice)

    chainDirectory = {
        "Solana": "Solana",
        "Ethereum": "Ethereum",
        "Binance Smart Chain": "BSC",
        "BSC": "BSC",
        "GMGN": "GMGN",
    }.get(chainName, chainName)

    while True:
        try:
            fileSelection = int(input("\n[❓] File Choice > "))
            if fileSelection > len(files):
                print("[🐲] Invalid input.")
                continue

            if files[fileSelection - 1] == "Select Own File":
                print(f"[🐲] Selected {files[fileSelection - 1]}")
                filePath = input("[🐲] Enter filename/path > ").strip()
            else:
                filePath = f"Dragon/data/{chainDirectory}/{files[fileSelection - 1]}"
            with open(filePath, 'r') as f:
                items = f.read().splitlines()

            if items:
                print(f"[🐲] Loaded {len(items)} items.")
                return items
            else:
                print("[🐲] File is empty. Try another file.")
        except Exception as e:
            print(f"[🐲] File error: {e}")


def getContractAddress(expectedLengths):
    while True:
        address = input("[❓] Contract Address > ").strip()
        if len(address) in expectedLengths:
            return address
        print(f"[🐲] Invalid length. Expected one of: {expectedLengths}")

def promptSkipWallets():
    while True:
        choice = input("[❓] Skip wallets with no buys in 30d (Y/N)> ").strip().upper()
        if choice in ["Y", "N"]:
            return choice == "Y"
        print("[🐲] Invalid input.")

def gmgn():
    gmgnInstance = GMGN()
    options, optionsChoice = utils.choices(chain="GMGN")
    print(optionsChoice)
    while True:
        try:
            optInput = int(input("\n[❓] Choice > "))
            if optInput == 4:
                print("[🐲] Thank you for using Dragon.")
                break
            elif optInput == 3:
                purgeFilesUtil(chain="GMGN")
                print("[🐲] Successfully purged files.")
                print(optionsChoice)
            elif optInput in [1, 2, 3]:
                siteChoice = options[optInput - 1]
                print(f"[🐲] Selected {siteChoice}")
                gmgnOptions, gmgnOptionsChoice = gmgnTools(siteChoice) 
                print(gmgnOptionsChoice)
                optSub = int(input("\n[❓] Choice > "))
                if optSub not in [1, 2, 3, 4]:
                    print("[🐲] Invalid choice.")
                    continue
                threads = getThreads()
                useProxies = getProxiesSetting()
                if optSub == 1:
                    urlIndicator = "NewToken"
                elif optSub == 2:
                    urlIndicator = "CompletingToken"
                elif optSub == 3:
                    urlIndicator = "SoaringToken"
                else:
                    urlIndicator = "BondedToken"
                gmgnInstance.contractsData(urlIndicator, threads, useProxies, siteChoice)
                print(optionsChoice)
            else:
                print("[🐲] Invalid choice.")
        except ValueError as e:
            clearScreen()
            print(e)
            print(bannerText, optionsChoice, "[🐲] Invalid input.")

def eth():
    walletCheck = EthBulkWalletChecker()
    topTradersInstance = EthTopTraders()
    timestampInstance = EthTimestampTransactions()
    scanInstance = EthScanAllTx()

    filesChoice, files = utils.searchForTxt(chain="Ethereum")
    options, optionsChoice = utils.choices(chain="Ethereum")
    print(optionsChoice)
    while True:
        try:
            optInput = int(input("\n[❓] Choice > "))
            if optInput not in range(1, 10):
                print("[🐲] Invalid choice.")
                continue
            print(f"[🐲] Selected {options[optInput - 1]}")
            if optInput == 2:
                if len(files) < 2:
                    print("[🐲] No files available.")
                    print(optionsChoice)
                    continue
                wallets = selectFile("Ethereum")
                threads = getThreads()
                useProxies = getProxiesSetting()
                skipWallets = promptSkipWallets()
                walletCheck.fetchWalletData(wallets, threads=threads, skipWallets=skipWallets, useProxies=useProxies)
                print(optionsChoice)
            elif optInput == 3:
                threads = getThreads()
                useProxies = getProxiesSetting()
                with open('Dragon/data/Ethereum/TopTraders/tokens.txt', 'r') as fp:
                    contractAddresses = fp.read().splitlines()
                if contractAddresses:
                    print(f"[🐲] Loaded {len(contractAddresses)} contract addresses")
                    topTradersInstance.topTraderData(contractAddresses, threads, useProxies)
                else:
                    print("[🐲] Tokens file is empty.")
                print(optionsChoice)
            elif optInput == 4:
                contractAddress = getContractAddress("Ethereum", [40, 41, 42])
                threads = getThreads()
                useProxies = getProxiesSetting()
                scanInstance.getAllTxMakers(contractAddress, threads, useProxies)
                print(optionsChoice)
            elif optInput == 5:
                contractAddress = getContractAddress("Ethereum", [40, 41, 42])
                threads = getThreads()
                useProxies = getProxiesSetting()
                print("[🐲] Get UNIX Timestamps here > https://www.unixtimestamp.com")
                print(f"[🐲] This token was minted at {timestampInstance.getMintTimestamp(contractAddress)}")
                startTimestamp = int(input("[❓] Start UNIX Timestamp > "))
                endTimestamp = int(input("[❓] End UNIX Timestamp > "))
                timestampInstance.getTxByTimestamp(contractAddress, threads, startTimestamp, endTimestamp, useProxies)
                print(optionsChoice)
            elif optInput == 6:
                purgeFilesUtil(chain="Ethereum")
                print("[🐲] Successfully purged files.")
                print(optionsChoice)
            elif optInput == 7:
                print("[🐲] Thank you for using Dragon.")
                break
            else:
                print("[🐲] This is a placeholder.")
                print(optionsChoice)
        except ValueError as e:
            clearScreen()
            print(bannerText, optionsChoice, "[🐲] Invalid input.", e)


def solana():
    timestampInstance = TimestampTransactions()
    bundleInstance = BundleFinder()
    scanInstance = ScanAllTx()
    walletCheck = BulkWalletChecker()
    topTradersInstance = TopTraders()
    copyTradeInstance = CopyTradeWalletFinder()
    topHoldersInstance = TopHolders()
    earlyBuyersInstance = EarlyBuyers()

    options, optionsChoice = utils.choices(chain="Solana")
    print(optionsChoice)
    while True:
        try:
            optInput = int(input("\n[❓] Choice > "))
            if optInput not in range(1, 11):
                print("[🐲] Invalid choice.")
                continue

            print(f"[🐲] Selected {options[optInput - 1]}")
            if optInput == 1:
                contractAddress = getContractAddress([43, 44])
                txHashes = bundleInstance.teamTrades(contractAddress)
                bundleData = bundleInstance.checkBundle(txHashes[0], txHashes[1])
                print(bundleInstance.prettyPrint(bundleData, contractAddress))
                print(optionsChoice)
            elif optInput == 2:
                wallets = selectFile("Solana")
                threads = getThreads()
                useProxies = getProxiesSetting()
                skipWallets = promptSkipWallets()
                walletCheck.fetchWalletData(wallets, threads=threads, skipWallets=skipWallets, useProxies=useProxies)
                print(optionsChoice)
            elif optInput == 3:
                contractAddresses = getSolanaContracts()
                threads = getThreads()
                useProxies = getProxiesSetting()
                topTradersInstance.topTraderData(contractAddresses, threads, useProxies)
                print(optionsChoice)
            elif optInput == 4:
                contractAddress = getContractAddress([43, 44])
                threads = getThreads()
                useProxies = getProxiesSetting()
                scanInstance.getAllTxMakers(contractAddress, threads, useProxies)
                print(optionsChoice)
            elif optInput == 5:
                contractAddress = getContractAddress([43, 44])
                threads = getThreads()
                useProxies = getProxiesSetting()
                print("[🐲] Get UNIX Timestamps here > https://www.unixtimestamp.com")
                print(f"[🐲] This token was minted at {timestampInstance.getMintTimestamp(contractAddress, useProxies)}")
                startTimestamp = int(input("[❓] Start UNIX Timestamp > "))
                endTimestamp = int(input("[❓] End UNIX Timestamp > "))
                timestampInstance.getTxByTimestamp(contractAddress, threads, startTimestamp, endTimestamp, useProxies)
            elif optInput == 6:
                print(f"\n[🐲] Read This -> https://github.com/1f1n/Dragon#copy-wallet-finder\n")
                print(optionsChoice)
            elif optInput == 7:
                contractAddresses = getSolanaContracts()
                threads = getThreads()
                useProxies = getProxiesSetting()
                topHoldersInstance.topHolderData(contractAddresses, threads, useProxies)
                print(optionsChoice)
            elif optInput == 8:
                contractAddresses = getSolanaContracts()
                buyers = int(input("[❓] Amount of Early Buyers > "))
                if buyers > 100:
                    print("[🐲] Maximum early buyers is 100. Defaulting to 40.")
                    buyers = 40
                threads = getThreads()
                useProxies = getProxiesSetting()
                earlyBuyersInstance.earlyBuyersdata(contractAddresses, threads, useProxies, buyers)
            elif optInput == 9:
                purgeFilesUtil(chain="Solana")
                print("[🐲] Successfully purged files.")
                print(optionsChoice)
            elif optInput == 10:
                print("[🐲] Thank you for using Dragon.")
                break
        except ValueError as e:
            print(f"[🐲] Error occurred: {e}")
            print(optionsChoice)

def bsc():
    walletCheck = BscBulkWalletChecker()
    topTradersInstance = BscTopTraders()

    filesChoice, files = utils.searchForTxt(chain="Binance Smart Chain")
    options, optionsChoice = utils.choices(chain="Binance Smart Chain")
    print(optionsChoice)
    while True:
        try:
            optInput = int(input("\n[❓] Choice > "))
            if optInput not in range(1, 5):
                print("[🐲] Invalid choice.")
                continue

            print(f"[🐲] Selected {options[optInput - 1]}")
            if optInput == 1:
                if len(files) < 2:
                    print("[🐲] No files available.")
                    print(optionsChoice)
                    continue
                wallets = selectFile("Binance Smart Chain")
                threads = getThreads()
                useProxies = getProxiesSetting()
                skipWallets = promptSkipWallets()
                walletCheck.fetchWalletData(wallets, threads=threads, skipWallets=skipWallets, useProxies=useProxies)
                print(optionsChoice)
            elif optInput == 2:
                threads = getThreads()
                useProxies = getProxiesSetting()
                with open('Dragon/data/BSC/TopTraders/tokens.txt', 'r') as fp:
                    contractAddresses = fp.read().splitlines()
                if contractAddresses:
                    topTradersInstance.topTraderData(contractAddresses, threads, useProxies)
                else:
                    print("[🐲] Tokens file is empty.")
                print(optionsChoice)
            elif optInput == 3:
                purgeFilesUtil(chain="BSC")
                print("[🐲] Successfully purged files.")
                print(optionsChoice)
            elif optInput == 4:
                print("[🐲] Thank you for using Dragon.")
                break
        except ValueError as e:
            clearScreen()
            print(bannerText, optionsChoice, "[🐲] Invalid input.", e)

if __name__ == "__main__":
    print(bannerText)
    chains, chainsChoice = utils.chains()
    print(chainsChoice)
    while True:
        try:
            choiceInput = int(input("\n[❓] Choice > "))
            if choiceInput in range(1, 6):
                print(f"[🐲] Selected {chains[choiceInput - 1]}")
                if choiceInput == 1:
                    solana()
                elif choiceInput == 2:
                    eth()
                elif choiceInput == 3:
                    bsc()
                elif choiceInput == 4:
                    gmgn()
                elif choiceInput == 5:
                    updateDragon()
                    clearScreen()
                    print(bannerText)
                    print(chainsChoice)
                    continue
                break
            else:
                print("[🐲] Invalid choice.")
        except ValueError as e:
            clearScreen()
            print(bannerText, chainsChoice, f"[🐲] Error occurred: {e}")
