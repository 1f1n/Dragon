import os
import glob

from colorama import Fore, init

def clear():
    os.system("cls||clear")

def banner():
    banner = f"""{Fore.RED}
WELCOME TO..

   (  )   /\   _                 (     
    \ |  (  \ ( \.(               )                      _____
  \  \ \  `  `   ) \             (  ___                 / _   \\
 (_`    \+   . x  ( .\            \\/   \____-----------/ (o)   \\_
- .-               \+  ;          (  O                           \\____
        DRAGON           )        \_____________  `              \\  /
(__                +- .( -'.- <. - _  VVVVVVV VV V\\                 \\/
(_____            ._._: <_ - <- _  (--  _AAAAAAA__A_/                  |
  .    /./.+-  . .- /  +--  - .     \______________//_              \\_______
  (__ ' /x  / x _/ (                                  \___'          \\     /
 , x / ( '  . / .  /                                      |           \\   /
    /  /  _/ /    +                                      /              \\/
   '  (__/                                             /                  \\
{Fore.WHITE}"""
    return banner

def checkProxyFile():
    with open('Dragon/data/Proxies/proxies.txt', 'r') as f:
        return bool(f.readlines())

def chains():
    options: list = ["Solana", "Ethereum", "Binance Smart Chain", "GMGN Tools"]
    optionsChoice = "[🐲] Please select a chain:\n\n" + "\n".join([f"[{Fore.RED}{index + 1}{Fore.WHITE}] {option}" for index, option in enumerate(options)])
    
    return options, optionsChoice

def gmgnTools(site: str):
    if site.lower() == "pump.fun":
        options: list = ["Pump.Fun New Token Scraper", "Pump.Fun Completing Token Scraper", "Pump.Fun Soaring Token Scraper", "Pump.Fun Bonded Token Scraper"]
        optionsChoice = "[🐲] Please select a module:\n\n" + "\n".join([f"[{Fore.RED}{index + 1}{Fore.WHITE}] {option}" for index, option in enumerate(options)])
    elif site.lower() == "moonshot":
        options: list = ["Moonshot New Token Scraper", "Moonshot Completing Token Scraper", "Moonshot Soaring Token Scraper", "Moonshot Bonded Token Scraper"]
        optionsChoice = "[🐲] Please select a module:\n\n" + "\n".join([f"[{Fore.RED}{index + 1}{Fore.WHITE}] {option}" for index, option in enumerate(options)])
    else:
        return f"[🐲] Error, Dragon does not support the site '{site}'"

    return options, optionsChoice

def choices(chain: str):
    if chain.lower() == "solana":
        options: list = ["Bundle Checker", "Bulk Wallet Checker", "Top Traders Scraper", "All Transaction Scan", "Get Transaction By Timestamp", "Copy Wallet Finder", "Top Holders Scraper", "Early Buyers Scraper", "Purge All Files", "Quit"]
    elif chain.lower() == "ethereum":
        options: list = ["Placeholder", "Bulk Wallet Checker", "Top Traders Scraper", "All Transaction Scan", "Get Transaction By Timestamp", "Purge All Files", "Quit"]
    elif chain.lower() == "binance smart chain":
        options: list = ["Bulk Wallet Checker", "Top Traders Scraper", "Purge All Files", "Quit"]
    elif chain.lower() == "gmgn":
        options: list = ["Pump.Fun", "Moonshot", "Purge All Files", "Quit"]
    else:
        return f"[🐲] Error, Dragon does not support the chain '{chain}'"
    
    optionsChoice = "[🐲] Please select a module:\n\n" + "\n".join([f"[{Fore.RED}{index + 1}{Fore.WHITE}] {option}" for index, option in enumerate(options)])
    return options, optionsChoice

def clear():
    os.system("cls||clear")

import os
import glob
from colorama import Fore

def searchForTxt(chain: str):
    if chain.lower() == "solana":
        chain = "Solana"
    elif chain.lower() == "ethereum":
        chain = "Ethereum"
    elif chain.lower() == "binance smart chain":
        chain = "BSC"
    elif chain.lower() == "gmgn":
        chain = "GMGN"
    else:
        return f"[🐲] Error, Dragon does not support the chain '{chain}'"
    
    search_directory = os.path.normpath(os.path.join(os.getcwd(), f'Dragon/data/{chain}'))
    additional_directory = os.path.normpath(os.path.join(os.getcwd(), 'Dragon/data/GMGN'))
    txtFiles = []
    
    for directory in [search_directory, additional_directory]:
        txtFiles.extend(glob.glob(os.path.join(directory, '**', '*.txt'), recursive=True))
    
    excluded_files = [
        #os.path.relpath(os.path.join(search_directory, 'TopTraders/tokens.txt'), search_directory)
    ]
    
    files = [
        os.path.relpath(file, search_directory).replace("\\", "/") 
        for file in txtFiles 
        if os.path.relpath(file, search_directory) not in excluded_files and 
           os.path.basename(file) != "placeholder.txt"
    ]
    files.append("Select Own File")
    filesChoice = "\n".join([f"[{Fore.RED}{index + 1}{Fore.WHITE}] {file}" for index, file in enumerate(files)])
    
    
    return filesChoice, files

def purgeFiles(chain: str):
    if chain.lower() == "solana":
        chain = "Solana"
    elif chain.lower() == "ethereum":
        chain = "Ethereum"
    elif chain.lower() == "bsc":
        chain = "BSC"
    elif chain.lower() == "gmgn":
        chain = "GMGN"
    else:
        return f"[🐲] Error, Dragon does not support the chain '{chain}'"
    
    base_directory = os.path.normpath(f"Dragon/data/{chain}")
    
    if chain == "GMGN":
        subfolders = ["BondedToken", "NewToken", "CompletingToken", "SoaringToken"]
        for main_subdir in os.listdir(base_directory):
            main_subdir_path = os.path.join(base_directory, main_subdir)
            if os.path.isdir(main_subdir_path):
                for folder in subfolders:
                    folder_path = os.path.join(main_subdir_path, folder)

                    if os.path.exists(folder_path):
                        for dirpath, _, filenames in os.walk(folder_path):
                            for file in filenames:
                                file_path = os.path.join(dirpath, file)
                                if file.endswith(('.txt', '.csv', '.json')):
                                    if file in ['wallets.txt', 'tokens.txt']:
                                        with open(file_path, 'w') as f:
                                            pass  
                                    else:
                                        os.remove(file_path)  
    else:
        for dirpath, _, filenames in os.walk(base_directory):
            for file in filenames:
                file_path = os.path.join(dirpath, file)
                if file.endswith(('.txt', '.csv', '.json')):
                    if file in ['wallets.txt', 'tokens.txt']:
                        with open(file_path, 'w') as f:
                            pass
                    else:
                        os.remove(file_path)
init(autoreset=True)
