import os
import requests
import time
from google import genai
from google.genai import types
from datetime import datetime, timedelta
import json

# Konfiguracja
INTERVALS_ID = os.environ.get('INTERVALS_ATHLETE_ID')
INTERVALS_API_KEY = os.environ.get('INTERVALS_API_KEY')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GH_TOKEN = os.environ.get('GH_TOKEN')
REPO = os.environ.get('GITHUB_REPOSITORY')

client = genai.Client(api_key=GEMINI_API_KEY)

def get_wellness_data():
    url = f"https://intervals.icu/api/v1/athlete/{INTERVALS_ID}/wellness?oldest={(datetime.now()-timedelta(days=3)).strftime('%Y-%m-%d')}"
    return requests.get(url, auth=('API_KEY', INTERVALS_API_KEY)).json()

def create_issue(title, body):
    url = f"https://api.github.com/repos/{REPO}/issues"
    headers = {"Authorization": f"token {GH_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    payload = {"title": title, "body": body}
    requests.post(url, json=payload, headers=headers)

def main():
    wellness = get_wellness_data()
    latest = wellness[-1] if wellness else {}
    
    # Używamy modelu "gemini-2.0-flash-lite", który jest bardziej stabilny
    model_name = "gemini-2.0-flash-lite"
    system_instruction = "Jesteś trenerem. Podopieczny: 46 lat, 83 kg, FTP 180W. Wypisz tabelę: HRV, Tętno spoczynkowe, Czas snu, TSS. Napisz żołnierską analizę i zalecenie na dziś."

    # Mechanizm ponawiania (do 5 prób co 15 sekund)
    for attempt in range(5):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=f"Dane: {json.dumps(latest)}. Co robimy?",
                config=types.GenerateContentConfig(system_instruction=system_instruction)
            )
            create_issue(f"Raport {datetime.now().strftime('%Y-%m-%d')}", response.text)
            print("Raport utworzony!")
            return # Sukces
        except Exception as e:
            print(f"Błąd (próba {attempt+1}/5): {e}")
            time.sleep(15) 
            
    print("Nie udało się połączyć z AI po 5 próbach.")

if __name__ == "__main__":
    main()
