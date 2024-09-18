
import requests
import time
import urllib3
import json
from colorama import init, Fore, Style
from fake_useragent import UserAgent
import os
import asyncio
import telegram

CONFIG_FILE = "config.json"

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

def get_proxies(config):
    # Check if proxy settings exist in the config file
    if 'proxy' in config and config['proxy']:
        proxies = {
            'http': config['proxy'],
            'https': config['proxy']
        }
        return proxies
    return None

def make_request(url, config):
    proxies = get_proxies(config)
    
    try:
        response = requests.get(url, proxies=proxies)
        if response.status_code == 200:
            print(f"{Fore.GREEN}[✓] Success! Response received from {url}{Style.RESET_ALL}")
            return response.text
        else:
            print(f"{Fore.RED}[X] Error: Failed to fetch data from {url}. Status code: {response.status_code}{Style.RESET_ALL}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}[X] Error: {e}{Style.RESET_ALL}")
        return None

if __name__ == "__main__":
    config = read_config()
    
    # Example of making a request with proxy handling
    url = "https://example.com"
    response = make_request(url, config)
