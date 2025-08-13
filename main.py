"""
main.py: třetí projekt do Engeto Online Python Akademie
author: Veronika Hekrlová
email: vhekrlova@seznam.cz
"""
import sys
import requests
from bs4 import BeautifulSoup
import csv

def zkontroluj_argumenty():
    """Zkontroluje spravny pocet argumentu a validitu odkazu"""
    if len(sys.argv) != 3:
        print("Chyba: zadej 2 argumenty - odkaz a nazev souboru")
        sys.exit(1)
    odkaz = sys.argv[1]
    if "https://www.volby.cz/pls/ps2017nss/" not in odkaz:
        print("Chyba: spatny odkaz")
        sys.exit(1)
    return odkaz, sys.argv[2]

def stahni_stranku(url):
    """Stahne HTML stranku a vrati objekt BeautifulSoup"""
    odpoved = requests.get(url)
    odpoved.encoding = "utf-8"
    return BeautifulSoup(odpoved.text, "html.parser")

def najdi_odkazy_obce(soup):
    """Najde odkazy na vysledky obce (jen ps311)"""
    odkazy = []
    for a in soup.find_all("a"):
        href = a.get("href", "")
        if "ps311" in href and "xobec" in href:
            plny_odkaz = "https://www.volby.cz/pls/ps2017nss/" + href
            odkazy.append(plny_odkaz)
    return odkazy

def ziskej_data_obce(url):
    """Ziska data o obci vcetne hlasu pro strany"""
    soup = stahni_stranku(url)

    try:
        # zakladni udaje
        kod = soup.find("td", {"class": "cislo"}).text.strip()
        nazev = soup.find("td", {"class": "overflow_name"}).text.strip()

        # volici, obalky, platne hlasy
        tds = [td.text.replace("\xa0", "") for td in soup.find_all("td", {"class": "cislo"})]
        volici = tds[3]
        obalky = tds[4]
        platne = tds[7]

        # hlasy pro vsechny strany (ve dvou tabulkach)
        hlasy_strany = []
        for table in soup.find_all("table", {"class": "table"}):
            for row in table.find_all("tr"):
                cislo_td = row.find_all("td", {"class": "cislo"})
                if len(cislo_td) >= 2:
                    # druhe cislo v radku je pocet hlasu
                    hlasy_strany.append(cislo_td[1].text.replace("\xa0", ""))

        return [kod, nazev, volici, obalky, platne] + hlasy_strany

    except AttributeError:
        print(f"Preskakuji {url} - neocekavana struktura")
        return None

def uloz_csv(data, soubor):
    """Ulozi data do csv souboru"""
    with open(soubor, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for radek in data:
            writer.writerow(radek)

def hlavni():
    odkaz, vystup = zkontroluj_argumenty()
    print("Stahuji hlavni stranku...")
    soup = stahni_stranku(odkaz)

    print("Hledam odkazy na obce...")
    odkazy = najdi_odkazy_obce(soup)

    vsechna_data = []
    for link in odkazy:
        print(f"Zpracovavam {link}")
        data_obec = ziskej_data_obce(link)
        if data_obec:
            vsechna_data.append(data_obec)

    uloz_csv(vsechna_data, vystup)
    print(f"Hotovo! Data ulozena do {vystup}")

if __name__ == "__main__":
    hlavni()
