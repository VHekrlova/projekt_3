Scraper výsledků voleb do PS 2017.

Použití: python main.py <start_url> <výstup.csv>

Popis:
    - Stáhne stránku se seznamem obcí pro daný okres/kraj.
    - Najde odkazy na stránky jednotlivých obcí.
    - Pro každou obec zjistí počet voličů, vydaných obálek, platných hlasů a hlasy pro strany.
    - Uloží do CSV.

Např. okres Benešov: python main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101" "vysledky_benesov.csv"
