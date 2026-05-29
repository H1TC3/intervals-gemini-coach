import os
from datetime import datetime
import json
from google import genai
from google.genai import types
import requests

# ... (kod pobierania danych z Intervals.icu zostaje bez zmian) ...

def main():
    # Pobieranie i analiza AI (kod zostaje ten sam co poprzednio)
    # ...
    
    # ZAPIS DO PLIKU
    dzis = datetime.now().strftime("%Y-%m-%d")
    raport_sciezka = f"raport_{dzis}.txt"
    with open(raport_sciezka, "w", encoding="utf-8") as f:
        f.write(response.text)

if __name__ == "__main__":
    main()
