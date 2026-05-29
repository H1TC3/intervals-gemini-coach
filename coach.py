import os
import json
import requests
from datetime import datetime, timedelta
from google import genai
from google.genai import types

# Konfiguracja
INTERVALS_ID = os.environ.get('INTERVALS_ATHLETE_ID')
INTERVALS_API_KEY = os.environ.get('INTERVALS_API_KEY')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

client = genai.Client(api_key=GEMINI_API_KEY)

def main():
    # Pobierz dane z Intervals
    url = f"https://intervals.icu/api/v1/athlete/{INTERVALS_ID}/wellness?oldest={(datetime.now()-timedelta(days=1)).strftime('%Y-%m-%d')}"
    response_data = requests.get(url, auth=('API_KEY', INTERVALS_API_KEY))
    
    if response_data.status_code == 200:
        wellness = response_data.json()
        latest = wellness[-1] if wellness else {}
        
        # Zapisz do pliku
        os.makedirs("dane", exist_ok=True)
        with open("dane/dzisiaj.json", "w", encoding="utf-8") as f:
            json.dump(latest, f, ensure_ascii=False, indent=4)
        print("Dane zapisane w dane/dzisiaj.json")
    else:
        print(f"Błąd pobierania danych: {response_data.status_code}")

if __name__ == "__main__":
    main()
