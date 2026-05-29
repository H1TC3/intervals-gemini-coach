import os
import json
import requests
from datetime import datetime, timedelta
from google import genai

# Konfiguracja - pobieranie z secrets
INTERVALS_ID = os.environ.get('INTERVALS_ATHLETE_ID')
INTERVALS_API_KEY = os.environ.get('INTERVALS_API_KEY')

def main():
    # Pobierz dane z Intervals
    url = f"https://intervals.icu/api/v1/athlete/{INTERVALS_ID}/wellness?oldest={(datetime.now()-timedelta(days=1)).strftime('%Y-%m-%d')}"
    wellness = requests.get(url, auth=('API_KEY', INTERVALS_API_KEY)).json()
    latest = wellness[-1] if wellness else {}
    
    # Zapisz do stałego pliku
    os.makedirs("dane", exist_ok=True)
    with open("dane/dzisiaj.json", "w", encoding="utf-8") as f:
        json.dump(latest, f, ensure_ascii=False, indent=4)
        
    print("Dane zapisane w dane/dzisiaj.json")

if __name__ == "__main__":
    main()
