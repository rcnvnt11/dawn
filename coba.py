import requests
import time
import urllib3
import json
from colorama import init, Fore, Style
from fake_useragent import UserAgent
import os
import asyncio
import telegram
import socks
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

CONFIG_FILE = "config.json"
PROXY_FILE = "socks.txt"

def read_config(filename=CONFIG_FILE):
    try:
        with open(filename, 'r') as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        print(f"{Fore.RED}[X] Error: Configuration file '{filename}' not found.{Style.BRIGHT}")
        return {}
    except json.JSONDecodeError:
        print(f"{Fore.RED}[X] Error: Invalid JSON format in '{filename}'.{Style.BRIGHT}")
        return {}

def read_proxies(filename=PROXY_FILE):
    proxies = []
    try:
        with open(filename, 'r') as file:
            for line in file:
                proxy = line.strip()
                if proxy:
                    proxies.append(proxy)
    except FileNotFoundError:
        print(f"{Fore.RED}[X] Error: Proxy file '{filename}' not found.{Style.BRIGHT}")
    return proxies

def create_session(proxy=None):
    session = requests.Session()
    if proxy:
        session.proxies = {
            'http': proxy,
            'https': proxy,
        }
    return session

config = read_config(CONFIG_FILE)
bot_token = config.get("telegram_bot_token")
chat_id = config.get("telegram_chat_id")

if not bot_token or not chat_id:
    print(f"{Fore.RED}[X] Error: Missing 'bot_token' or 'chat_id' in 'config.json'.{Style.BRIGHT}")
    exit(1)

bot = telegram.Bot(token=bot_token)
keepalive_url = "https://www.aeropres.in/chromeapi/dawn/v1/userreward/keepalive"
get_points_url = "https://www.aeropres.in/api/atom/v1/userreferral/getpoint"
extension_id = "fpdkjdnhkakefebpekbdhillbhonfjjp"
_v = "1.0.7"

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = read_proxies(PROXY_FILE)
if not proxies:
    print(f"{Fore.RED}[X] Error: No proxies found in '{PROXY_FILE}'.{Style.BRIGHT}")
    exit(1)

def rotate_proxies(proxies):
    while True:
        for proxy in proxies:
            yield proxy

proxy_pool = rotate_proxies(proxies)

async def main():
    total_points_all_users = 0
    ua = UserAgent()
    
    while True:
        for account_index, account in enumerate(config.get("accounts", [])):
            email = account.get("email")
            token = account.get("token")

            if not email or not token:
                continue

            current_proxy = next(proxy_pool)
            session = create_session(current_proxy)

            headers = {
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9",
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": ua.random
            }

            print(f"{Fore.CYAN}━━━━━━━━━━━━━[ DAWN Validator | Account {account_index + 1} ]━━━━━━━━━━━━━{Style.BRIGHT}")
            print(f"{Fore.MAGENTA}[@] Email: {email}{Style.BRIGHT}")
            
            points = total_points(headers, session)
            total_points_all_users += points 
            
            success, status_message = keep_alive(headers, email, session)

            if success:
                message = f"""✴️ DAWN VALIDATOR NOTIFICATION ✴️

👤 Account: {email}
ℹ️ Status: Keep alive ✅
💰 Point: +{points:,.0f}

GG! Your account successfully "Keep Alive", See you on the next loop. 👋"""
                await telegram_message(message)
                print(f"{Fore.GREEN}[✓] Status: Keep alive recorded{Style.BRIGHT}")
                print(f"{Fore.GREEN}[✓] Request for {email} successful.{Style.BRIGHT}\\n")
            else:
                message = f"""🚨 DAWN VALIDATOR NOTIFICATION 🚨

👤 Account: {email}
ℹ️ Status: Failed ❌
⚠️ Error: {status_message}

Oops! There was an error in the "Keep Alive" process. Don't worry, it won't take long. 👌"""
                await telegram_message(message)
                print(f"{Fore.RED}[X] Status: Keep alive failed!{Style.BRIGHT}")
                print(f"{Fore.RED}[X] Error: {status_message}{Style.BRIGHT}\\n")

        print(f"{Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.BRIGHT}")
        print(f"{Fore.MAGENTA}[@] All accounts processed.{Style.BRIGHT}")
        print(f"{Fore.GREEN}[+] Total points from all users: {total_points_all_users}{Style.BRIGHT}")

        countdown(181)
        print(f"\\n{Fore.GREEN}[✓] Restarting the process...{Style.BRIGHT}\\n")

if __name__ == "__main__":
    asyncio.run(main())
