import os
import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
from multiprocessing import Pool
from random import choice

# Работа с Proxy и User-Agent
WORKED_PROXY = None
WORKED_USER_AGENT = None
PROXIES = open("Proxies_Valid.txt").read().split("\n")
USER_AGENT = open("ua.txt").read().split("\n")

# Ссылки
HOST_DOTABUFF = "https://www.dotabuff.com"


def get_html(url, headers, proxies):
    try:
        response = requests.get(url, headers=headers, proxies=proxies, timeout = 3)
        if response.status_code == 200:
            return response
        else:
            return None
    except Exception as ex:
        return None


def get_main_html(url, print_text):
    global WORKED_PROXY
    global WORKED_USER_AGENT
    while True:
        if WORKED_PROXY:
            result = get_html(url, WORKED_USER_AGENT, WORKED_PROXY)
            if result:
                break
            else:
                WORKED_PROXY = None
                WORKED_USER_AGENT = None
        else:
            proxy = choice(PROXIES)
            proxies = {'http': 'http://' + proxy,
                       'https': 'http://' + proxy}
            ua = choice(USER_AGENT)
            headers = {'User-Agent': ua}
            result = get_html(url, headers, proxies)
            if result:
                WORKED_PROXY = proxies
                WORKED_USER_AGENT = headers
                break
    print(print_text)
    return result


def get_match_links(url, print_text):
    result = []
    html = get_main_html(url, print_text)
    soup = BeautifulSoup(html.text, 'lxml')
    links = soup.find_all('a', rel = "noreferrer noopener")
    links_sum = []
    for link in links:
        links_sum.append(link.get('href'))
    for el in links_sum:
        if el.count(HOST_DOTABUFF):
            result.append(el)
    return result


def create_csv():
    if os.path.isdir("Results"):
        pass
    else:
        os.mkdir("Results")
    try:
        matchs = open("Results/matchs.csv").read()
    except Exception as ex:
        matchs = open("Results/matchs.csv", "w+")
        matchs.write("id,First team,Second team, Winner")
        matchs.close()
    try:
        teams = open("Results/teams.csv").read()
    except Exception as ex:
        teams = open("Results/teams.csv", "w+")
        teams.write("id_match,Team,Core,Mid,Hard,Hard support,Easy support")
        teams.close()
    try:
        heros = open("Results/heros.csv").read()
    except Exception as ex:
        heros = open("Results/heros.csv", "w+")
        heros.write("id_match,Team,1 pos.,2 pos.,3 pos.,4 pos.,5 pos.")
        heros.close()
    try:
        players = open("Results/players.csv").read()
    except Exception as ex:
        players = open("Results/players.csv", "w+")
        players.write("Player,Kill,Dead,Assists,Net Worth,Last hit,Denies hit,GPM,XPM")
        players.close()
    try:
        allhero = open("Results/allhero.csv").read()
    except Exception as ex:
        allhero = open("Results/allhero.csv", "w+")
        allhero.write("Hero,Win rate, Pick rate")
        allhero.close()


def get_information_player(player_links):
    result = {}
    for index, player in enumerate(player_links):
        # Ссылка на игрока в дотабаффе
        link = HOST_DOTABUFF + player.find('a',class_="esports-player").get("href")
        html = get_main_html(link, f"Получаем информацию о игроке: {link} ...")
        soup = BeautifulSoup(html.text, "lxml")

        # Имя игрока
        full_name = soup.find("div", class_ = "header-content-title").find("h1").get_text(strip=True)
        part_skip = soup.find("div", class_ = "header-content-title").find("small").get_text(strip=True)
        name = full_name.replace(part_skip, "")

        # Роль игрока
        role = player.find("i").get("title")+ " " +player.find("i").find_next("i").get("title")

        # Герой
        hero = player.find("img", class_="image-hero").get("title")
        # Статистика игрока за матч
        temp_inf_1 = player.find_all("td", class_ = "tf-r")
        temp_inf_2 = player.find_all("td", class_ = "tf-pl r-tab r-group-2 cell-minor")
        k = temp_inf_1[0].text.strip()
        if k == "-":
            k = "0"
        d = temp_inf_1[1].text.strip()
        if d == "-":
            d = "0"
        a = temp_inf_1[2].text.strip()
        if a == "-":
            a = "0"
        net = temp_inf_1[3].text.strip().replace("k", "")
        if net == "-":
            net = "0"
        lh = temp_inf_1[4].text.strip()
        if lh == "-":
            lh = "0"
        dh = temp_inf_2[0].text.strip()
        if dh == "-":
            dh = "0"
        gpm = temp_inf_1[5].text.strip()
        if gpm == "-":
            gpm = "0"
        xpm = temp_inf_2[1].text.strip()
        if xpm == "-":
            xpm = "0"
        result[index] = [name, hero, int(k), int(d), int(a), float(net), int(lh), int(dh), int(gpm), int(xpm), role]
    result = get_result(result)
    print(result)
    return result


def get_result(dict):

    result = {}
    for key in dict:
        role = dict[key][-1]

        if role == "Core Role Safe Lane" and result.get("1") == None:
            result["1"] = dict[key]
            continue
        elif role == "Core Role Safe Lane" and result.get("1") != None:
            result["2"] = dict[key]
            continue

        if role == "Core Role Mid Lane" and result.get("2") == None:
            result["2"] = dict[key]
            continue
        elif role == "Core Role Mid Lane" and result.get("3") != None:
            result["3"] = dict[key]
            continue

        if role == "Core Role Off Lane" and result.get("3") == None:
            result["3"] = dict[key]
            continue
        elif role == "Core Role Off Lane" and result.get("3") != None:
            result["4"] = dict[key]
            continue
        else:
            if result.get("4") == None:
                result["4"] = dict[key]
                continue
            else:
                result["5"] = dict[key]
                continue
    return result


def get_content(match_links):
    html = get_main_html(match_links, f"Парсим матч: {match_links} ...")
    soup = BeautifulSoup(html.text, "lxml")
    content = soup.find("div", class_="team-results")

    radiant = content.find("section", class_="radiant")
    dire = content.find("section", class_="dire")

    # Получаем основную информацию
    id_match = match_links.replace(HOST_DOTABUFF + "/matches/", "").strip()
    radiant_name = radiant.find("span", class_="team-text team-text-full").get_text(strip=True)
    dire_name = dire.find("span", class_="team-text team-text-full").get_text(strip=True)
    winner = (soup.find("div", class_="match-result").text.strip()).replace("Victory!", "")

    # Первая таблица
    first_table = id_match + ',' + radiant_name + ',' + dire_name + ',' + winner
    # Вторая таблица
    tbodys = content.find_all("tbody")
    player_links_radiant = tbodys[0].find_all("tr", class_="col-hints")
    player_links_dire = tbodys[1].find_all("tr", class_="col-hints")

    players_radiant = get_information_player(player_links_radiant)
    players_dire = get_information_player(player_links_dire)
    second_table = id_match + "," + radiant_name + "," + players_radiant["1"][0] + "," + players_radiant["2"][0] + "," + \
                   players_radiant["3"][0] + "," + players_radiant["4"][0] + "," + players_radiant["5"][
                       0] + "\n" + id_match + "," + dire_name + "," + players_dire["1"][0] + "," + players_dire["2"][
                       0] + "," + players_dire["3"][0] + "," + players_dire["4"][0] + "," + players_dire["5"][0]
    # третья таблица
    third_table = id_match + "," + radiant_name + "," + players_radiant["1"][1] + "," + players_radiant["2"][1] + "," + \
                  players_radiant["3"][1] + "," + players_radiant["4"][1] + "," + players_radiant["5"][
                      1] + "\n" + id_match + "," + dire_name + "," + players_dire["1"][1] + "," + players_dire["2"][
                      1] + "," + players_dire["3"][1] + "," + players_dire["4"][1] + "," + players_dire["5"][1]

    # Четвертая таблица
    fourth_table = ""
    for i, player in enumerate(players_dire):
        fourth_table = fourth_table + f"{players_dire[str(i + 1)][0]}," \
                                      f"{players_dire[str(i + 1)][2]}," \
                                      f"{players_dire[str(i + 1)][3]}," \
                                      f"{players_dire[str(i + 1)][4]}," \
                                      f"{players_dire[str(i + 1)][5]}," \
                                      f"{players_dire[str(i + 1)][6]}," \
                                      f"{players_dire[str(i + 1)][7]}," \
                                      f"{players_dire[str(i + 1)][8]}," \
                                      f"{players_dire[str(i + 1)][9]}" + "\n"
    for i, player in enumerate(players_radiant):
        fourth_table = fourth_table + f"{players_radiant[str(i + 1)][0]}," \
                                      f"{players_radiant[str(i + 1)][2]}," \
                                      f"{players_radiant[str(i + 1)][3]}," \
                                      f"{players_radiant[str(i + 1)][4]}," \
                                      f"{players_radiant[str(i + 1)][5]}," \
                                      f"{players_radiant[str(i + 1)][6]}," \
                                      f"{players_radiant[str(i + 1)][7]}," \
                                      f"{players_radiant[str(i + 1)][8]}," \
                                      f"{players_radiant[str(i + 1)][9]}" + "\n"
    save(first_table, second_table, third_table, fourth_table)


def save(first_table, second_table, third_table, fourth_table):
    matchs = open("Results/matchs.csv", "a", encoding='utf-8')
    matchs.write("\n" + first_table)
    matchs.close()

    teams = open("Results/teams.csv", "a", encoding='utf-8')
    teams.write("\n" + second_table)
    teams.close()

    heros = open("Results/heros.csv", "a", encoding='utf-8')
    heros.write("\n" + third_table)
    heros.close()


def main(url):
    link = url
    match_links = get_match_links(link, f"HTML страница полученна по ссылке: {link} ...")
    print(len(match_links))
    create_csv()
    print("Начало")
    skip = 0
    for link in match_links:
        try:
            get_content(link)
        except Exception as ex:
            skip = skip + 1
            print(f"{ex}\nCкип")
    print("Конец.\nСкипнуто:"+ str(skip))



tournaments = open("tournaments.txt").read().split("\n")

if __name__ == "__main__":
    with Pool(8) as P:
        P.map(main, tournaments)

