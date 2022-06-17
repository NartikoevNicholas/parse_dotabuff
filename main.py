import parse_proxies
import get_valid_proxies
from multiprocessing import Pool

if __name__ == '__main__':
    proxies_invalid = open("Proxies_No_Valid.txt").read().strip().split("\n")
    proxies_valid = open("Proxies_Valid.txt", "w")
    proxies_valid.close()
    print("next step")
    with Pool(8) as pool:
        pool.map(get_valid_proxies.handler, proxies_invalid)
    print("Скрипт get_valid_proxies.py завершил работу")
else:
    print("Ошибка 1")