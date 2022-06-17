import requests
from bs4 import BeautifulSoup

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
          'accept':'*/*'}
URLS = ["https://proxylist.geonode.com/api/proxy-list?limit=200&page=1&sort_by=lastChecked&sort_type=desc&country=RU&protocols=http%2Chttps",
        "https://hidemy.name/ru/proxy-list/?type=hs#list"]



def get_html_for_proxy(url):
    response = requests.get(url, headers = HEADERS)
    return response.text

def get_ip_port_site_geonode(ip):
    result = ''
    for char in ip:
        if char == "\"":
            break
        result += char
    return result

def get_proxy_site_geonode(html):
    soup = BeautifulSoup(html, "lxml").text.strip()
    ips = soup.split("\"ip\":\"")
    ports = soup.split("\"port\":\"")
    ips.pop(0)
    ports.pop(0)

    for i in range(len(ips)):
        ip = get_ip_port_site_geonode(ips[i])
        port = get_ip_port_site_geonode(ports[i])
        FILE_NO_VALID.write(f"{ip}:{port}\n")

def get_quantity_page(html):
    soup = BeautifulSoup(html,"lxml")
    items = (soup.find("div", class_="pagination")).find_all("li")
    return int(items[-2].text.strip())-1

def get_proxy_site_hidemy(html, paggination, url):
    soup = BeautifulSoup(html, "lxml")
    items = soup.find_all("tr")
    items.pop(0)
    for item in items:
        ip = item.find('td').text.strip()
        port = item.find('td').find_next().text.strip()
        FILE_NO_VALID.write(f"{str(ip)}:{str(port)}\n")

    for i in range(paggination):
        url_temp = url.replace("type=hs", f"type=hs&start={(i + 1) * 64}")
        html = get_html_for_proxy(url_temp)
        soup = BeautifulSoup(html, "lxml")
        items = soup.find_all("tr")
        items.pop(0)
        for item in items:
            ip = item.find('td').text.strip()
            port = item.find('td').find_next().text.strip()
            FILE_NO_VALID.write(f"{str(ip)}:{str(port)}\n")

def main():
    # сайт geonode
    html_geonode = get_html_for_proxy(URLS[0])
    get_proxy_site_geonode(html_geonode)

    # сайт hidemy

    # html_hidemy = get_html_for_proxy(URLS[1])
    # paggination_hidemy = get_quantity_page(html_hidemy)
    # get_proxy_site_hidemy(html_hidemy, paggination_hidemy, URLS[1])

    FILE_NO_VALID.close()
    Count_Proxies = open("Proxies_No_Valid.txt").read().split("\n")
    print(f"Завершенно!\nКоличество прокси: {len(Count_Proxies)}")


FILE_NO_VALID = open("Proxies_No_Valid.txt", "w")
main()
