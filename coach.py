import os
import requests
import time
from google import genai
from google.genai import types
from datetime import datetime, timedelta
import json

# Pobieranie danych
INTERVALS_ID = os.environ.get('INTERVALS_ATHLETE_ID')
INTERVALS_API_KEY = os.environ.get('INTERVALS_API_KEY')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GH_TOKEN = os.environ.get('GH_TOKEN') # Twój nowy token
REPO = os.environ.get('GITHUB_REPOSITORY') # Automatycznie pobierane przez GitHub Actions

client = genai.Client(api_key=GEMINI_API_KEY)

def get_wellness_data(days=3):
    url = f"https://intervals.icu/api/v1/athlete/{INTERVALS_ID}/wellness?oldest={(datetime.now()-timedelta(days=days)).strftime('%Y-%m-%d')}"
    return requests.get(url, auth=('API_KEY', INTERVALS_API_KEY)).json()

def create_issue(title, body):
    url = f"https://api.github.com/repos/{REPO}/issues"
    headers = {"Authorization": f"token {GH_TOKEN}"}
    payload = {"title": title, "body": body}
    requests.post(url, json=payload, headers=headers)

def main():
    wellness = get_wellness_data()
    # Zakładamy, że bierzemy najświeższy wpis
    latest = wellness[-1] if wellness else {}
    
    system_instruction = (
        "Jesteś trenerem. Podopieczny: 46 lat, 83 kg, FTP 180W. "
        "Wypisz w tabeli: HRV, Tętno spoczynkowe, Czas snu, TSS. "
        "Napisz żołnierską analizę regeneracji i zalecenie na dziś."
    )

    user_prompt = f"Dane Wellness: {json.dumps(latest)}\nCo robimy dzisiaj?"

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=user_prompt,
        config=types.GenerateContentConfig(system_instruction=system_instruction)
    )
    
    create_issue(f"Raport Treningowy {datetime.now().strftime('%Y-%m-%d')}", response.text)
    print("Raport wysłany do Issues!")

if __name__ == "__main__":
    main()
