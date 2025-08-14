"""
main.py: třetí projekt do Engeto Online Python Akademie
author: Veronika Hekrlová
email: vhekrlova@seznam.cz
"""
import sys
import time
import requests
from bs4 import BeautifulSoup
import csv

def zkontroluj_argumenty():
    ''' Ověří, že uživatel zadal přesně 2 argumenty (odkaz a jméno výstupního souboru)'''
    if len(sys.argv) != 3:
        print("Chyba: zadej 2 argumenty - odkaz a nazev souboru")
        sys.exit(1)

    odkaz = sys.argv[1]  #
    # Kontrola, zda odkaz obsahuje požadovanou část adresy
    if "https://www.volby.cz/pls/ps2017nss/" not in odkaz:
        print("Chyba: spatny odkaz")
        sys.exit(1)

    return odkaz, sys.argv[2]

def stahni_stranku(url, pokusy=3, prodleva=2):
    """Stáhne HTML stránku s opakováním (retry) a timeoutem."""
    for i in range(pokusy):
        try:
            odpoved = requests.get(url, timeout=10)
            odpoved.encoding = "utf-8"
            return BeautifulSoup(odpoved.text, "html.parser")
        except requests.exceptions.RequestException as e:
            print(f"Chyba při stahování {url}: {e}")
            if i < pokusy - 1:
                print(f"Opakuji pokus ({i+1}/{pokusy}) za {prodleva} s...")
                time.sleep(prodleva)
            else:
                raise

def najdi_odkazy_a_obce(soup):
    """
    Najde v hlavní tabulce okresu všechny obce.
    Vrací seznam trojic: (odkaz_na_obec, kod_obce, nazev_obce)
    """
    vysledky = []
    for row in soup.find_all("tr"):
        tds = row.find_all("td")
        if len(tds) >= 2:
            a_tag = tds[0].find("a")
            if a_tag and "xobec" in a_tag.get("href", ""):
                kod = tds[0].text.strip()   # kód obce
                nazev = tds[1].text.strip() # název obce
                plny_odkaz = "https://www.volby.cz/pls/ps2017nss/" + a_tag.get("href")
                vysledky.append((plny_odkaz, kod, nazev))
    return vysledky

def ziskej_data_obce(url, kod, nazev):
    """Získá detailní volební data pro jednu obec."""
    soup = stahni_stranku(url)
    try:
        # z tabulky s třídou "cislo" vezmeme konkrétní indexy pro: registrovaní, obálky, platné hlasy
        tds = [td.text.replace("\xa0", "") for td in soup.find_all("td", {"class": "cislo"})]
        volici = tds[3]
        obalky = tds[4]
        platne = tds[7]

        # hlasy pro strany + názvy stran
        hlasy_strany = []
        nazvy_stran = []
        for table in soup.find_all("table", {"class": "table"}):
            for row in table.find_all("tr"):
                nazev_strany_td = row.find("td", {"class": "overflow_name"})
                cisla_td = row.find_all("td", {"class": "cislo"})
                if nazev_strany_td and len(cisla_td) >= 2:
                    nazvy_stran.append(nazev_strany_td.text.strip())  # název strany
                    hlasy_strany.append(cisla_td[1].text.replace("\xa0", ""))  # počet hlasů

        # vrátíme: kód, název obce, registrovaní, obálky, platné + všechny hlasy
        return [kod, nazev, volici, obalky, platne] + hlasy_strany, nazvy_stran

    except AttributeError:
        # pokud stránka má jinou strukturu, přeskočíme ji
        print(f"Preskakuji {url} - neocekavana struktura")
        return None, None

def uloz_csv(data, hlavicka, soubor):
    """Uloží data do CSV souboru s hlavičkou."""
    with open(soubor, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(hlavicka)  # první řádek = hlavička
        writer.writerows(data)     # zbytek = data

def hlavni():
    # načteme argumenty
    odkaz, vystup = zkontroluj_argumenty()

    print("Stahuji hlavní stránku...")
    soup = stahni_stranku(odkaz)

    print("Hledám odkazy a názvy obcí...")
    odkazy_a_obce = najdi_odkazy_a_obce(soup)

    vsechna_data = []
    hlavicka = None

    # projdeme každou obec
    for i, (link, kod, nazev) in enumerate(odkazy_a_obce):
        print(f"Zpracovávám {kod} - {nazev}")
        data_obec, nazvy_stran = ziskej_data_obce(link, kod, nazev)
        if data_obec:
            if hlavicka is None:
                hlavicka = ["code", "location", "registered", "envelopes", "valid"] + nazvy_stran
            vsechna_data.append(data_obec)
        time.sleep(1)

    uloz_csv(vsechna_data, hlavicka, vystup)
    print(f"Hotovo! Data uložena do {vystup}")

if __name__ == "__main__":
    hlavni()
