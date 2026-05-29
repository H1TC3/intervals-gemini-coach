import os
import requests
import google.generativeai as genai
from datetime import datetime, timedelta
import json

# Pobieranie danych z bezpiecznych sekretów GitHuba
INTERVALS_ID = os.environ.get('INTERVALS_ATHLETE_ID')
INTERVALS_API_KEY = os.environ.get('INTERVALS_API_KEY')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

intervals_auth = ('API_KEY', INTERVALS_API_KEY)
base_url = f"https://intervals.icu/api/v1/athlete/{INTERVALS_ID}"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-pro')

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
        "waży 83 kg, FTP: 180W. Trenuje kolarstwo i siłę. Przeanalizuj dzisiejsze tętno spoczynkowe, HRV oraz sen. "
        "Napisz krótką, żołnierską analizę poranną stanu regeneracji i jednoznaczne zalecenie na dzisiejszy dzień."
    )

    user_prompt = f"Dane Wellness (3 dni):\n{wellness_summary}\n\nOstatnie aktywności:\n{activities_summary}\n\nCo robimy dzisiaj?"

    response = model.generate_content(
        contents=user_prompt,
        generation_config=genai.types.GenerationConfig(
            system_instruction=system_instruction,
            temperature=0.3,
        )
    )
    
    # Zapis wyniku do pliku tekstowego (stworzy historię raportów)
    dzis = datetime.now().strftime("%Y-%m-%d")
    nazwa_pliku = f"raporty/raport_{dzis}.txt"
    os.makedirs("raporty", exist_ok=True)
    
    with open(nazwa_pliku, "w", encoding="utf-8") as f:
        f.write(f"=== RAPORT TRENINGOWY AI - {dzis} ===\n\n")
        f.write(response.text)
        
    print("Raport wygenerowany pomyślnie i zapisany w pliku!")

if __name__ == "__main__":
    main()
