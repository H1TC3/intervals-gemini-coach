import os
import requests
from google import genai
from google.genai import types
from datetime import datetime, timedelta
import json

# Pobieranie danych z bezpiecznych sekretów GitHuba
INTERVALS_ID = os.environ.get('INTERVALS_ATHLETE_ID')
INTERVALS_API_KEY = os.environ.get('INTERVALS_API_KEY')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

intervals_auth = ('API_KEY', INTERVALS_API_KEY)
base_url = f"https://intervals.icu/api/v1/athlete/{INTERVALS_ID}"

# Inicjalizacja klienta Gemini
client = genai.Client(api_key=GEMINI_API_KEY)

def get_wellness_data(days=3):
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    url = f"{base_url}/wellness?oldest={start_date}&newest={end_date}"
    response = requests.get(url, auth=intervals_auth)
    return response.json() if response.status_code == 200 else []

def get_recent_activities(days=5):
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    url = f"{base_url}/activities?oldest={start_date}&newest={end_date}"
    response = requests.get(url, auth=intervals_auth)
    return response.json() if response.status_code == 200 else []

def main():
    wellness = get_wellness_data(days=3)
    activities = get_recent_activities(days=5)

    wellness_summary = json.dumps(wellness, indent=2)
    activities_summary = json.dumps([
        {"Data": act.get('start_date_local'), "Typ": act.get('type'), "TSS": act.get('tss'), "Czas(s)": act.get('moving_time')} 
        for act in activities
    ], indent=2)

    system_instruction = (
        "Jesteś zaawansowanym trenerem kolarstwa i sportów siłowych. Twój podopieczny ma 46 lat, "
        "waży 83 kg, FTP 180W. Posiada trenażer, hantle i ławeczkę. "
        "Trenuje w 6-dniowym splicie. Na początku raportu wypisz w tabeli: Data, HRV, Tętno spoczynkowe, Czas snu, TSS z wczoraj. "
        "Potem napisz żołnierską analizę regeneracji i jednoznaczne zalecenie treningowe na dzisiaj."
    )

    user_prompt = f"Dane Wellness (3 dni):\n{wellness_summary}\n\nOstatnie aktywności:\n{activities_summary}\n\nCo robimy dzisiaj?"

    # Generowanie treści
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.3,
        )
    )
    
    dzis = datetime.now().strftime("%Y-%m-%d")
    
    # 1. Zapis raportu do folderu raporty (do czytania przez Ciebie)
    os.makedirs("raporty", exist_ok=True)
    with open(f"raporty/raport_{dzis}.txt", "w", encoding="utf-8") as f:
        f.write(response.text)
        
    # 2. Zapis surowych danych do folderu dane (do czytania przeze mnie)
    dane_do_zapisu = {
        "data": dzis,
        "wellness": wellness,
        "analiza_ai": response.text
    }
    os.makedirs("dane", exist_ok=True)
    with open(f"dane/dane_{dzis}.json", "w", encoding="utf-8") as f:
        json.dump(dane_do_zapisu, f, ensure_ascii=False, indent=4)
        
    print("Raport i dane zapisane pomyślnie!")

if __name__ == "__main__":
    main()
