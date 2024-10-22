import datetime

from Dragon import (utils, BundleFinder, ScanAllTx, BulkWalletChecker, TopTraders, TimestampTransactions,
                    purgeFiles, CopyTradeWalletFinder, TopHolders, checkProxyFile, WalletScan)
from Dragon import TronTopTraders, TronBulkWalletChecker, TronTimestampTransactions
from Dragon import EthBulkWalletChecker, EthTopTraders, EthTimestampTransactions, EthScanAllTx
import time
purgeFiles = utils.purgeFiles
clear = utils.clear

def eth():
    walletCheck = EthBulkWalletChecker()
    topTraders = EthTopTraders()
    timestamp = EthTimestampTransactions()
    scan = EthScanAllTx()

    filesChoice, files = utils.searchForTxt(chain="Ethereum")
    options, optionsChoice = utils.choices(chain="Ethereum")

    print(f"{optionsChoice}\n")

    while True:
        try:
            while True:
                optionsInput = int(input("[❓] Choice > "))
                if optionsInput in [1, 2, 3, 4, 5, 6, 7, 8]:
                    print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Selected {options[optionsInput - 1]}")
                    break 
                else:
                    print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Invalid choice.")
            if optionsInput == 1:
                print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  This is a placeholder.")
                print(f"\n{optionsChoice}\n")
            elif optionsInput == 2:
                if len(files) < 2:
                    print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No files available.")
                    print(f"\n{optionsChoice}\n")
                    continue
                print(f"\n{filesChoice}\n")

                try:
                    while True:
                        fileSelectionOption = int(input("[❓] File Choice > "))
                        if fileSelectionOption > len(files):
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Invalid input.")
                        elif files[fileSelectionOption - 1] == "Select Own File":
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Selected {files[fileSelectionOption - 1]}")
                            while True:
                                fileDirectory = input("[🐲] Enter filename/path > ")
                                try:
                                    with open(fileDirectory, 'r') as f:
                                        wallets = f.read().splitlines()
                                    if wallets and wallets != []:
                                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Loaded {len(wallets)} wallets") 
                                        break
                                    else:
                                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Error occurred, file may be empty. Go to the ")
                                        continue
                                except Exception as e:
                                    print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  File directory not found.")
                                    continue
                            break
                        else:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Selected {files[fileSelectionOption - 1]}")
                            fileDirectory = f"Dragon/data/Ethereum/{files[fileSelectionOption - 1]}"

                            with open(fileDirectory, 'r') as f:
                                wallets = f.read().splitlines()
                            if wallets and wallets != []:
                                print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Loaded {len(wallets)} wallets")
                                break 
                            else:
                                print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Error occurred, file may be empty.")
                                continue 
                    while True:
                        threads = input("[❓] Threads > ")
                        try:
                            threads = int(threads)
                            if threads > 100:
                                print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Do not use more than 100 threads. Automatically set threads to 40.")
                                threads = 40
                        except ValueError:
                            threads = 40
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid input. Defaulting to 40 threads.")
                            break
                        break
                    while True:
                        skipWallets = False
                        skipWalletsInput = input("[❓] Skip wallets with no buys in 30d (Y/N)> ")

                        if skipWalletsInput.upper() not in ["Y", "N"]:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Invalid input.")
                            continue 
                        if skipWalletsInput.upper() == "N":
                            skipWallets = False
                        else:
                            skipWallets = True
                        walletData = walletCheck.fetchWalletData(wallets, threads=threads, skipWallets=skipWallets)
                        print(f"\n{optionsChoice}\n")
                        break  
                except IndexError as e:
                    print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] File choice out of range.")
                    print(f"\n{optionsChoice}\n")
                except ValueError:
                    print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Invalid input.")
                    print(f"\n{optionsChoice}\n")
                continue
            elif optionsInput == 3:
                while True:
                    threads = input("[❓] Threads > ")
                    try:
                        threads = int(threads)
                        if threads > 100:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Do not use more than 100 threads. Automatically set threads to 40.")
                            threads = 40
                    except ValueError:
                        threads = 40
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid input. Defaulting to 40 threads.")
                    break
                with open('Dragon/data/Ethereum/TopTraders/tokens.txt', 'r') as fp:
                    contractAddresses = fp.read().splitlines()
                    if contractAddresses and contractAddresses != []:
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Loaded {len(contractAddresses)} contract addresses")
                    else:
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Error occurred, file may be empty. Go to the file here: Draon/data/Ethereum/tokens.txt")
                        print(f"\n{optionsChoice}\n")
                        continue
                    data = topTraders.topTraderData(contractAddresses, threads)

                print(f"\n{optionsChoice}\n")
            elif optionsInput == 4:
                while True:
                    contractAddress = input("[❓] Contract Address > ")

                    if len(contractAddress) not in [40, 41, 42]:
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid length.")
                    else:
                        break

                while True:
                    threads = input("[❓] Threads > ")

                    try:
                        threads = int(threads)
                        if threads > 100:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Do not use more than 100 threads. Automatically set threads to 40.")
                            threads = 40
                    except ValueError:
                        threads = 40 
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid input. Defaulting to 40 threads.")
                        break
                    break

                go = scan.getAllTxMakers(contractAddress, threads)
                print(f"\n{optionsChoice}\n")
            elif optionsInput == 5:
                while True:
                    contractAddress = input("[❓] Contract Address > ")

                    if len(contractAddress) not in [40, 41, 42]:
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid length.")
                    else:
                        break
                while True:
                    threads = input("[❓] Threads > ")
                    try:
                        threads = int(threads)
                        if threads > 100:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Do not use more than 100 threads. Automatically set threads to 40.")
                            threads = 40
                    except ValueError:
                        threads = 40 
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid input. Defaulting to 40 threads.")
                        break
                    break
                print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Get UNIX Timetstamps Here > https://www.unixtimestamp.com")
                print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  This token was minted at {timestamp.getMintTimestamp(contractAddress)}")
                while True:
                    start = input("[❓] Start UNIX Timestamp > ")
                    try:
                        start = int(start)
                    except ValueError:
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid input.")
                        break
                    break
                while True:
                    end = input("[❓] End UNIX Timestamp > ")
                    try:
                        start = int(start)
                    except ValueError:
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid input.")
                        break
                    break
                timestampTxns = timestamp.getTxByTimestamp(contractAddress, threads, start, end)
                print(f"\n{optionsChoice}\n")
            elif optionsInput == 6:
                purgeFiles(chain="Ethereum")
                print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Successfully purged files.")   
                print(f"\n{optionsChoice}\n")
            elif optionsInput == 7:
                print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Thank you for using Dragon.")
                break
        except ValueError as e:
            clear()
            print(banner)
            print(f"\n{optionsChoice}\n")
            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Invalid input.")
        except ValueError as e:
            utils.clear()
            print(banner)
            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Error occured. Please retry or use a VPN/Proxy. {e}")
            print(f"\n{optionsChoice}\n")
            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Invalid input.")
    


def tron():
    topTraders = TronTopTraders()
    walletCheck = TronBulkWalletChecker()
    timestamp = TronTimestampTransactions()
    filesChoice, files = utils.searchForTxt(chain="Tron")

    options, optionsChoice = utils.choices(chain="Tron")
    print(f"{optionsChoice}\n")
    while True:
        try:
            while True:
                optionsInput = int(input("[❓] Choice > "))
                if optionsInput in [1, 2, 3, 4, 5, 6, 7, 8]:
                    print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Selected {options[optionsInput - 1]}")
                    break 
                else:
                    print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Invalid choice.")
            if optionsInput == 1:
                print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  This is a placeholder.")
                print(f"\n{optionsChoice}\n")
            elif optionsInput == 2:
                if len(files) < 2:
                    print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No files available.")
                    print(f"\n{optionsChoice}\n")
                    continue 

                print(f"\n{filesChoice}\n")

                try:
                    while True:
                        fileSelectionOption = int(input("[❓] File Choice > "))
                        if fileSelectionOption > len(files):
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Invalid input.")
                        elif files[fileSelectionOption - 1] == "Select Own File":
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Selected {files[fileSelectionOption - 1]}")
                            while True:
                                fileDirectory = input("[🐲] Enter filename/path > ")
                                try:
                                    with open(fileDirectory, 'r') as f:
                                        wallets = f.read().splitlines()
                                    if wallets and wallets != []:
                                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Loaded {len(wallets)} wallets") 
                                        break
                                    else:
                                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Error occurred, file may be empty. Go to the ")
                                        continue
                                except Exception as e:
                                    print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  File directory not found.")
                                    continue
                            break
                                    
                        else:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Selected {files[fileSelectionOption - 1]}")
                            fileDirectory = f"Dragon/data/Tron/{files[fileSelectionOption - 1]}"

                            with open(fileDirectory, 'r') as f:
                                wallets = f.read().splitlines()
                            if wallets and wallets != []:
                                print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Loaded {len(wallets)} wallets")
                                break 
                            else:
                                print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Error occurred, file may be empty.")
                                continue 

                    while True:
                        threads = input("[❓] Threads > ")
                        try:
                            threads = int(threads)
                            if threads > 100:
                                print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Do not use more than 100 threads. Automatically set threads to 40.")
                                threads = 40
                        except ValueError:
                            threads = 40
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid input. Defaulting to 40 threads.")
                            break
                        break

                    while True:
                        skipWallets = False
                        skipWalletsInput = input("[❓] Skip wallets with no buys in 30d (Y/N)> ")

                        if skipWalletsInput.upper() not in ["Y", "N"]:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Invalid input.")
                            continue 
                        if skipWalletsInput.upper() == "N":
                            skipWallets = False
                        else:
                            skipWallets = True
                        walletData = walletCheck.fetchWalletData(wallets, threads=threads, skipWallets=skipWallets)
                        print(f"\n{optionsChoice}\n")
                        break  

                except IndexError as e:
                    print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] File choice out of range.")
                    print(f"\n{optionsChoice}\n")
                except ValueError:
                    print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Invalid input.")
                    print(f"\n{optionsChoice}\n")
                continue 
            elif optionsInput == 3:
                while True:
                    threads = input("[❓] Threads > ")
                    try:
                        threads = int(threads)
                        if threads > 100:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Do not use more than 100 threads. Automatically set threads to 40.")
                            threads = 40
                    except ValueError:
                        threads = 40
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid input. Defaulting to 40 threads.")
                    break
                with open('Dragon/data/Tron/TopTraders/tokens.txt', 'r') as fp:
                    contractAddresses = fp.read().splitlines()
                    if contractAddresses and contractAddresses != []:
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Loaded {len(contractAddresses)} contract addresses")
                    else:
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Error occurred, file may be empty. Go to the file here: Draon/data/TopTraders/tokens.txt")
                        print(f"\n{optionsChoice}\n")
                        continue
                    data = topTraders.topTraderData(contractAddresses, threads)

                print(f"\n{optionsChoice}\n")
            elif optionsInput == 3:
                print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  This is a placeholder.")
                print(f"\n{optionsChoice}\n")
            elif optionsInput == 4:
                print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  This is a placeholder.")
                print(f"\n{optionsChoice}\n")
            elif optionsInput == 5:
                while True:
                    contractAddress = input("[❓] Contract Address > ")

                    if len(contractAddress) not in [33, 34]:
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid length.")
                    else:
                        break
                while True:
                    threads = input("[❓] Threads > ")
                    try:
                        threads = int(threads)
                        if threads > 100:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Do not use more than 100 threads. Automatically set threads to 40.")
                            threads = 40
                    except ValueError:
                        threads = 40 
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid input. Defaulting to 40 threads.")
                        break
                    break
                print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Get UNIX Timetstamps Here > https://www.unixtimestamp.com")
                print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  This token was minted at {timestamp.getMintTimestamp(contractAddress)}")
                while True:
                    start = input("[❓] Start UNIX Timestamp > ")
                    try:
                        start = int(start)
                    except ValueError:
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid input.")
                        break
                    break
                while True:
                    end = input("[❓] End UNIX Timestamp > ")
                    try:
                        start = int(start)
                    except ValueError:
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid input.")
                        break
                    break
                timestampTxns = timestamp.getTxByTimestamp(contractAddress, threads, start, end)
                print(f"\n{optionsChoice}\n")
            elif optionsInput == 6:
                purgeFiles(chain="Tron")
                print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Successfully purged files.")   
                print(f"\n{optionsChoice}\n")
            elif optionsInput == 7:
                print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Thank you for using Dragon.")
                break
        except ValueError as e:
            clear()
            print(banner)
            print(f"\n{optionsChoice}\n")
            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Invalid input.")


def solana():
    timestamp = TimestampTransactions()
    filesChoice, files = utils.searchForTxt(chain="Solana")
    bundle = BundleFinder()
    scan = ScanAllTx()
    walletCheck = BulkWalletChecker()
    topTraders = TopTraders()
    copytrade = CopyTradeWalletFinder()
    topHolders = TopHolders()
    walletScan = WalletScan()

    options, optionsChoice = utils.choices(chain="Solana")
    print(f"{optionsChoice}\n")
    while True:
        try:
            while True:
                optionsInput = int(input("[❓] Choice > "))
                if optionsInput in [1, 2, 3, 4, 5, 6, 7, 8,9,10]:
                    print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Selected {options[optionsInput - 1]}")
                    break 
                else:
                    print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Invalid choice.")
        
        
            if optionsInput == 1:
                while True:
                    contractAddress = input("[❓] Contract Address > ")
                    
                    if len(contractAddress) not in [43, 44]:
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid length.")
                    else:
                        transactionHashes = bundle.teamTrades(contractAddress)
                        bundleData = bundle.checkBundle(transactionHashes[0], transactionHashes[1])
                        formatData = bundle.prettyPrint(bundleData, contractAddress)
                        print(f"\n{formatData}")
                        print(f"\n{optionsChoice}\n")
                        break
            elif optionsInput == 2:
                if len(files) < 2:
                    print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No files available.")
                    continue
            
                print(f"\n{filesChoice}\n")
            
                try:
                    while True:
                        fileSelectionOption = int(input("[❓] File Choice > "))
                        if fileSelectionOption > len(files):
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Invalid input.")
                        elif files[fileSelectionOption - 1] == "Select Own File":
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Selected {files[fileSelectionOption - 1]}")
                            while True:
                                fileDirectory = input("[🐲] Enter filename/path > ")
                                try:
                                    with open(fileDirectory, 'r') as f:
                                        wallets = f.read().splitlines()
                                    if wallets:
                                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Loaded {len(wallets)} wallets")
                                        break
                                    else:
                                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Error: file may be empty. Please try again.")
                                except FileNotFoundError:
                                    print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  File not found. Please check the path.")
                            break
                        else:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Selected {files[fileSelectionOption - 1]}")
                            fileDirectory = f"Dragon/data/Solana/{files[fileSelectionOption - 1]}"
            
                            with open(fileDirectory, 'r') as f:
                                wallets = f.read().splitlines()
                            if wallets:
                                print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Loaded {len(wallets)} wallets")
                                break
                            else:
                                print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Error: file may be empty.")
                                continue
            
                    # Handle threads input
                    while True:
                        try:
                            threads = int(input("[❓] Threads > "))
                            if threads > 100:
                                print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Do not use more than 100 threads. Automatically set threads to 40.")
                                threads = 40
                        except ValueError:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid input. Defaulting to 40 threads.")
                            threads = 40
                        break
            
                    # Handle proxy input
                    while True:
                        proxies = input("[❓] Use Proxies? (Y/N) > ").lower()
                        checkProxies = checkProxyFile()
            
                        if proxies == "y" and checkProxies:
                            useProxies = True
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Using proxies.")
                        elif proxies == "y" and not checkProxies:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Dragon/data/Proxies/proxies.txt is empty, please add proxies to use them.")
                            useProxies = False
                        elif proxies == "n":
                            useProxies = False
                        else:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid input.")
                            continue
                            
                        break
            
                    # Handle skip wallets input
                    while True:
                        skipWalletsInput = input("[❓] Skip wallets with no buys in 30d (Y/N) > ").upper()
                        if skipWalletsInput in ["Y", "N"]:
                            skipWallets = skipWalletsInput == "Y"
                            break
                        else:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Invalid input.")
            
                    while True:
                        try:
                            minWinRate = float(input("[❓] Minimum Win Rate [7 days] (%) > "))
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Minimum Win Rate set to {minWinRate}%")
                            break
                        except ValueError:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Invalid input. Please enter a valid percentage.")
                    
                    while True:
                        try:
                            maxWinRate = float(input("[❓] Maximum Win Rate [7 days] (%) > "))
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Maximum Win Rate set to {maxWinRate}%")
                            break
                        except ValueError:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Invalid input. Please enter a valid percentage.")
            
                    while True:
                        try:
                            minPNL = float(input("[❓] Minimum PNL [7 Days] (USD) > "))
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Minimum PNL set to ${minPNL}")
                            break
                        except ValueError:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Invalid input. Please enter a valid amount.")
                    
                    while True:
                        try:
                            maxPNL = float(input("[❓] Maximum PNL [7 Days] (USD) > "))
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Maximum PNL set to ${maxPNL}")
                            break
                        except ValueError:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Invalid input. Please enter a valid amount.")
            
                    while True:
                        try:
                            minTokensTraded = int(input("[❓] Minimum Tokens Traded [7 Days] > "))
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Minimum Tokens Traded set to {minTokensTraded}")
                            break
                        except ValueError:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Invalid input. Please enter a valid number.")
            
                    while True:
                        try:
                            maxTokensTraded = int(input("[❓] Maximum Tokens Traded [7 Days] > "))
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Maximum Tokens Traded set to {maxTokensTraded}")
                            break
                        except ValueError:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Invalid input. Please enter a valid number.")

                    while True:
                        try:
                            minAmount100 = int(input("[❓] Minimum amount of Coins the Wallet made 100%+ on [7 Days] > "))
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Minimum amount of Coins the Wallet made 100%+ set to {minAmount100}")
                            break
                        except ValueError:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Invalid input. Please enter a valid number.")

                    while True:
                        try:
                            minAmount200 = int(input("[❓] Minimum amount of Coins the Wallet made 200%+ on [7 Days] > "))
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Minimum amount of Coins the Wallet made 200%+ set to {minAmount200}")
                            break
                        except ValueError:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Invalid input. Please enter a valid number.")

                    while True:
                        try:
                            minAmount500 = int(input("[❓] Minimum amount of Coins the Wallet made 500%+ on [7 Days] > "))
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Minimum amount of Coins the Wallet made 500%+ set to {minAmount500}")
                            break
                        except ValueError:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Invalid input. Please enter a valid number.")

                    while True:
                        try:
                            minAmount1000 = int(input("[❓] Minimum amount of Coins the Wallet made 1000%+ on [7 Days] > "))
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Minimum amount of Coins the Wallet made 1000%+ set to {minAmount1000}")
                            break
                        except ValueError:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Invalid input. Please enter a valid number.")
                    

                    filters = {
                        "minWinRate": minWinRate,
                        "maxWinRate": maxWinRate,
                        "minPNL": minPNL,
                        "maxPNL": maxPNL,
                        "minTokensTraded": minTokensTraded,
                        "maxTokensTraded": maxTokensTraded,
                        "minAmount100": minAmount100,
                        "minAmount200": minAmount200,
                        "minAmount500": minAmount500,
                        "minAmount1000": minAmount1000
                    }
                    # Fetch wallet data with the newly added filters
                    walletCheck.fetchWalletData(
                        wallets,
                        threads=threads,
                        skipWallets=skipWallets,
                        useProxies=useProxies,
                        filters=filters
                    )
                    print(f"\n{optionsChoice}\n")
            
                except IndexError:
                    print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] File choice out of range.")
                    print(f"\n{optionsChoice}\n")
                # except ValueError as e:
                #     print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid input. - {e}")
                #     print(f"\n{optionsChoice}\n")
                continue

            elif optionsInput == 3:
                while True:
                    threads = input("[❓] Threads > ")
                    try:
                        threads = int(threads)
                        if threads > 100:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Do not use more than 100 threads. Automatically set threads to 40.")
                            threads = 40
                    except ValueError:
                        threads = 40
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid input. Defaulting to 40 threads.")
                    break
                
                while True:
                    proxies = input("[❓] Use Proxies? (Y/N) > ")
                
                    try:
                        useProxies = None

                        checkProxies = checkProxyFile()

                        if not checkProxies:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Dragon/data/Proxies/proxies.txt is empty, please add proxies to use them.")
                            useProxies = False
                            break

                        if proxies.lower() == "y":
                            useProxies = True
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Using proxies.")
                        else:
                            useProxies = False
                    except Exception:
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid input")
                        break
                    break

                with open('Dragon/data/Solana/TopTraders/tokens.txt', 'r') as fp:
                    contractAddresses = fp.read().splitlines()
                    if contractAddresses and contractAddresses != []:
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Loaded {len(contractAddresses)} contract addresses")
                    else:
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Error occurred, file may be empty. Go to the file here: Draon/data/TopTraders/tokens.txt")
                        print(f"\n{optionsChoice}\n")
                        continue
                        
                    data = topTraders.topTraderData(contractAddresses, threads, useProxies)

                print(f"\n{optionsChoice}\n")
            elif optionsInput == 4:
                while True:
                    contractAddress = input("[❓] Contract Address > ")

                    if len(contractAddress) not in [43, 44]:
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid length.")
                    else:
                        break

                while True:
                    threads = input("[❓] Threads > ")

                    try:
                        threads = int(threads)
                        if threads > 100:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Do not use more than 100 threads. Automatically set threads to 40.")
                            threads = 40
                    except ValueError:
                        threads = 40 
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid input. Defaulting to 40 threads.")
                        break
                    break

                while True:
                    proxies = input("[❓] Use Proxies? (Y/N) > ")
                
                    try:
                        useProxies = None

                        checkProxies = checkProxyFile()

                        if not checkProxies:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Dragon/data/Proxies/proxies.txt is empty, please add proxies to use them.")
                            useProxies = False
                            break

                        if proxies.lower() == "y":
                            useProxies = True
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Using proxies.")
                        else:
                            useProxies = False
                    except Exception:
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid input")
                        break
                    break

                go = scan.getAllTxMakers(contractAddress, threads, useProxies)
                print(f"\n{optionsChoice}\n")

            elif optionsInput == 5:
                while True:
                    contractAddress = input("[❓] Contract Address > ")

                    if len(contractAddress) not in [43, 44]:
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid length.")
                    else:
                        break
                while True:
                    threads = input("[❓] Threads > ")
                    try:
                        threads = int(threads)
                        if threads > 100:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Do not use more than 100 threads. Automatically set threads to 40.")
                            threads = 40
                    except ValueError:
                        threads = 40 
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid input. Defaulting to 40 threads.")
                        break
                    break
                while True:
                    proxies = input("[❓] Use Proxies? (Y/N) > ")
                
                    try:
                        useProxies = None

                        checkProxies = checkProxyFile()

                        if not checkProxies:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Dragon/data/Proxies/proxies.txt is empty, please add proxies to use them.")
                            useProxies = False
                            break

                        if proxies.lower() == "y":
                            useProxies = True
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Using proxies.")
                        else:
                            useProxies = False
                    except Exception:
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid input")
                        break
                    break
                print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Get UNIX Timetstamps Here > https://www.unixtimestamp.com")
                print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  This token was minted at {timestamp.getMintTimestamp(contractAddress, useProxies)}")
                while True:
                    start = input("[❓] Start UNIX Timestamp > ")
                    try:
                        start = int(start)
                    except ValueError:
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid input.")
                        break
                    break
                while True:
                    end = input("[❓] End UNIX Timestamp > ")
                    try:
                        start = int(start)
                    except ValueError:
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid input.")
                        break
                    break
                timestampTxns = timestamp.getTxByTimestamp(contractAddress, threads, start, end, useProxies)
                break
            elif optionsInput == 6:
                while True:
                    contractAddress = input("[❓] Contract Address > ")

                    if len(contractAddress) not in [43, 44]:
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid length.")
                    else:
                        break
                while True:
                    walletAddress = input("[❓] Wallet Address > ")

                    if len(walletAddress) not in [43, 44]:
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid length.")
                    else:
                        break
                while True:
                    threads = input("[❓] Threads > ")
                    try:
                        threads = int(threads)
                        if threads > 10000:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Do not use more than 100 threads. Automatically set threads to 40.")
                            threads = 40
                    except ValueError:
                        threads = 40 
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid input. Defaulting to 40 threads.")
                        break
                    break
                
                while True:
                    proxies = input("[❓] Use Proxies? (Y/N) > ")
                
                    try:
                        useProxies = None

                        checkProxies = checkProxyFile()

                        if not checkProxies:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Dragon/data/Proxies/proxies.txt is empty, please add proxies to use them.")
                            useProxies = False
                            break

                        if proxies.lower() == "y":
                            useProxies = True
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Using proxies.")
                        else:
                            useProxies = False
                    except Exception:
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid input")
                        break
                    break

                findWallets = copytrade.findWallets(contractAddress, walletAddress, threads, useProxies)

            elif optionsInput == 7:
                while True:
                    threads = input("[❓] Threads > ")
                    try:
                        threads = int(threads)
                        if threads > 100:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Do not use more than 100 threads. Automatically set threads to 40.")
                            threads = 40
                    except ValueError:
                        threads = 40
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid input. Defaulting to 40 threads.")
                    break
                while True:
                    proxies = input("[❓] Use Proxies? (Y/N) > ")
                
                    try:
                        useProxies = None

                        checkProxies = checkProxyFile()

                        if not checkProxies:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Dragon/data/Proxies/proxies.txt is empty, please add proxies to use them.")
                            useProxies = False
                            break

                        if proxies.lower() == "y":
                            useProxies = True
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Using proxies.")
                        else:
                            useProxies = False
                    except Exception:
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid input")
                        break
                    break
                with open('Dragon/data/Solana/TopHolders/tokens.txt', 'r') as fp:
                    contractAddresses = fp.read().splitlines()
                    if contractAddresses and contractAddresses != []:
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Loaded {len(contractAddresses)} contract addresses")
                    else:
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Error occurred, file may be empty. Go to the file here: Draon/data/TopTraders/tokens.txt")
                        print(f"\n{optionsChoice}\n")
                        continue
                        
                    data = topHolders.topHolderData(contractAddresses, threads, useProxies)

                print(f"\n{optionsChoice}\n")
                
            elif optionsInput == 8:
                while True:
                    walletAddress = input("[❓] Wallet Address > ")

                    if len(walletAddress) not in [43, 44]:
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid length.")
                    else:
                        break

                while True:
                    startTime = input("[❓] Start Time (0 for now) > ")

                    if startTime == "0":
                        startTime = int(time.time())
                    else:
                        startTime = int(startTime)
                        
                    break

                while True:
                    endTime = input("[❓] End Time > ")
                    endTime = int(endTime)
                    break
                        
                while True:
                    threads = input("[❓] Threads > ")
                    try:
                        threads = int(threads)
                        if threads > 10000:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Do not use more than 100 threads. Automatically set threads to 40.")
                            threads = 40
                    except ValueError:
                        threads = 40
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid input. Defaulting to 40 threads.")
                        break
                    break

                while True:
                    rpcUrl = input("[❓] RPC URL > ")

                    try:
                        if type(rpcUrl) != str:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid input")
                            break
                        if "https://" not in rpcUrl:
                            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid input")
                            break
                    except Exception:
                        print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid input")
                        break
                    break

                walletScan.getAllWallets(contractAddress=walletAddress, start_time=startTime, end_time=endTime, threads=threads, rpc=rpcUrl)
                break
            elif optionsInput == 9:
                purgeFiles(chain="Solana")
                print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Successfully purged files.")   
                print(f"\n{optionsChoice}\n")

            elif optionsInput == 10:
                print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Thank you for using Dragon.")
                break

        except ValueError as e:
            utils.clear()
            print(banner)
            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Error occured. Please retry or use a VPN/Proxy. {e}")
            print(f"\n{optionsChoice}\n")
            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Invalid input.")

banner = utils.banner()
print(banner)

chains = utils.chains()[0]
chainsChoice = utils.chains()[1]
print(f"{chainsChoice}\n")

while True:
    try:
        while True:
            chainsInput = int(input("[❓] Choice > "))
            if chainsInput in [1, 2, 3]:
                print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Selected {chains[chainsInput - 1]}")
                break
            else:
                print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Invalid choice.")
        if chainsInput == 1:
            solana()
        elif chainsInput == 2:
            tron()
        elif chainsInput == 3:
            eth()
        else:
            print(f"[🐲] [{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]  Invalid choice.")
        break
    except ValueError as e:
        utils.clear()
        print(banner)
        print(f"{chainsChoice}\n")
