import os
import io
import glob
import zipfile
import requests
from typing import List, Tuple, Union

from colorama import Fore, init

init(autoreset=True)

def clear() -> None:
    os.system("cls||clear")

def banner() -> str:
    return f"""{Fore.RED}
WELCOME TO..

   (  )   /\   _                 (     
    \ |  (  \ ( \.(               )                      _____
  \  \ \  `  `   ) \             (  ___                 / _   \\
 (_`    \+   . x  ( .\\            \\/   \\____-----------/ (o)   \\_
- .-               \\+  ;          (  O                           \\____
        DRAGON           )        \\_____________  `              \\  /
(__                +- .( -'.- <. - _  VVVVVVV VV V\\                 \\/
(_____            ._._: <_ - <- _  (--  _AAAAAAA__A_/                  |
  .    /./.+-  . .- /  +--  - .     \\______________//_              \\_______
  (__ ' /x  / x _/ (                                  \\___'          \\     /
 , x / ( '  . / .  /                                      |           \\   /
    /  /  _/ /    +                                      /              \\/
   '  (__/                                             /                  \\
{Fore.WHITE}"""


def checkProxyFile() -> bool:
    proxyPath = os.path.join("Dragon", "data", "Proxies", "proxies.txt")
    with open(proxyPath, "r", encoding="utf-8") as fileObj:
        return bool(fileObj.readlines())


def chains() -> Tuple[List[str], str]:
    options = ["Solana", "Ethereum", "Binance Smart Chain", "GMGN Tools", "Update"]
    optionsChoice = "[🐲] Please select a chain:\n\n" + "\n".join(
        [f"[{Fore.RED}{index + 1}{Fore.WHITE}] {option}" for index, option in enumerate(options)]
    )
    return options, optionsChoice


def gmgnTools(site: str) -> Union[Tuple[List[str], str], str]:
    siteLower = site.lower()
    if siteLower == "pump.fun":
        options = [
            "Pump.Fun New Token Scraper",
            "Pump.Fun Completing Token Scraper",
            "Pump.Fun Soaring Token Scraper",
            "Pump.Fun Bonded Token Scraper",
        ]
    elif siteLower == "moonshot":
        options = [
            "Moonshot New Token Scraper",
            "Moonshot Completing Token Scraper",
            "Moonshot Soaring Token Scraper",
            "Moonshot Bonded Token Scraper",
        ]
    else:
        return f"[🐲] Error, Dragon does not support the site '{site}'"

    optionsChoice = "[🐲] Please select a module:\n\n" + "\n".join(
        [f"[{Fore.RED}{index + 1}{Fore.WHITE}] {option}" for index, option in enumerate(options)]
    )
    return options, optionsChoice


def choices(chain: str) -> Union[Tuple[List[str], str], str]:
    chainLower = chain.lower()
    if chainLower == "solana":
        options = [
            "Bundle Checker",
            "Bulk Wallet Checker",
            "Top Traders Scraper",
            "All Transaction Scan",
            "Get Transaction By Timestamp",
            "Copy Wallet Finder",
            "Top Holders Scraper",
            "Early Buyers Scraper",
            "Purge All Files",
            "Quit",
        ]
    elif chainLower == "ethereum":
        options = [
            "Placeholder",
            "Bulk Wallet Checker",
            "Top Traders Scraper",
            "All Transaction Scan",
            "Get Transaction By Timestamp",
            "Purge All Files",
            "Quit",
        ]
    elif chainLower == "binance smart chain":
        options = ["Bulk Wallet Checker", "Top Traders Scraper", "Purge All Files", "Quit"]
    elif chainLower == "gmgn":
        options = ["Pump.Fun", "Moonshot", "Purge All Files", "Quit"]
    else:
        return f"[🐲] Error, Dragon does not support the chain '{chain}'"

    optionsChoice = "[🐲] Please select a module:\n\n" + "\n".join(
        [f"[{Fore.RED}{index + 1}{Fore.WHITE}] {option}" for index, option in enumerate(options)]
    )
    return options, optionsChoice


def searchForTxt(chain: str) -> Tuple[str, List[str]]:
    chainMap = {
        "solana": "Solana",
        "ethereum": "Ethereum",
        "binance smart chain": "BSC",
        "gmgn": "GMGN",
    }
    chainKey = chain.lower()
    if chainKey not in chainMap:
        raise ValueError(f"[🐲] Error, Dragon does not support the chain '{chain}'")
    
    searchDirectory = os.path.normpath(os.path.join(os.getcwd(), "Dragon", "data", chainMap[chainKey]))
    additionalDirectory = os.path.normpath(os.path.join(os.getcwd(), "Dragon", "data", "GMGN"))
    txtFiles = glob.glob(os.path.join(searchDirectory, "**", "*.txt"), recursive=True) + \
               glob.glob(os.path.join(additionalDirectory, "**", "*.txt"), recursive=True)

    excludedFiles = set()
    files = [
        os.path.relpath(filePath, searchDirectory).replace("\\", "/")
        for filePath in txtFiles
        if os.path.basename(filePath) != "placeholder.txt" and
           os.path.relpath(filePath, searchDirectory) not in excludedFiles
    ]
    
    files.append("Select Own File")
    filesChoice = "\n".join([f"[{Fore.RED}{index + 1}{Fore.WHITE}] {filePath}" for index, filePath in enumerate(files)])
    
    return filesChoice, files


def purgeFiles(chain: str) -> None:
    chainMap = {
        "solana": "Solana",
        "ethereum": "Ethereum",
        "bsc": "BSC",
        "gmgn": "GMGN",
    }
    chainKey = chain.lower()
    if chainKey not in chainMap:
        raise ValueError(f"[🐲] Error, Dragon does not support the chain '{chain}'")
    
    baseDirectory = os.path.normpath(os.path.join("Dragon", "data", chainMap[chainKey]))
    
    if chainKey == "gmgn":
        subfolders = ["BondedToken", "NewToken", "CompletingToken", "SoaringToken"]
        for mainSubdir in os.listdir(baseDirectory):
            mainSubdirPath = os.path.join(baseDirectory, mainSubdir)
            if os.path.isdir(mainSubdirPath):
                for folder in subfolders:
                    folderPath = os.path.join(mainSubdirPath, folder)
                    if os.path.exists(folderPath):
                        for dirPath, _, fileNames in os.walk(folderPath):
                            for fileName in fileNames:
                                filePath = os.path.join(dirPath, fileName)
                                if fileName.endswith((".txt", ".csv", ".json")):
                                    if fileName in ("wallets.txt", "tokens.txt"):
                                        # Clear essential files.
                                        with open(filePath, "w", encoding="utf-8") as fileObj:
                                            pass
                                    else:
                                        os.remove(filePath)
    else:
        for dirPath, _, fileNames in os.walk(baseDirectory):
            for fileName in fileNames:
                filePath = os.path.join(dirPath, fileName)
                if fileName.endswith((".txt", ".csv", ".json")):
                    if fileName in ("wallets.txt", "tokens.txt"):
                        with open(filePath, "w", encoding="utf-8") as fileObj:
                            pass
                    else:
                        os.remove(filePath)


def updateDragon() -> None:
    zipUrl = "https://github.com/1f1n/Dragon/archive/refs/heads/main.zip"
    response = requests.get(zipUrl)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as zipObj:
        root = zipObj.namelist()[0].split("/")[0] + "/"
        for member in zipObj.namelist():
            if member.endswith("/"):
                continue
            relPath = member[len(root):]
            target = os.path.join(".", relPath)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with zipObj.open(member) as src, open(target, "wb") as dst:
                dst.write(src.read())

    print(f"[🐲] Successfully updated Dragon.")

