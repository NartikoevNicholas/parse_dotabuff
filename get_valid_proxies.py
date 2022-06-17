import requests
import time
from multiprocessing import Pool
from random import choice


HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
          'accept':'*/*'}

def handler(proxy):
    url = "https://icanhazip.com/"
    proxies = {'http': 'http://' + proxy,
               'https': 'http://' + proxy}
    try:
        response = requests.get(url,headers = HEADERS, proxies = proxies, timeout = 3)
        if response.status_code == 200:
            print(f"IP: {response.text.strip()}")
            valid_file = open("Proxies_Valid.txt", "a")
            valid_file.write(f"{proxy}\n")
        else:
            print("Прокси не валидный!")
    except Exception as ex:
        print("Прокси не валидный!")
