# Affiliate QR-System mit Streamlit

Ein einfacher Proof of Concept für ein Affiliate-System, das QR-Codes verwendet, um Einkäufe Affiliates zuzuordnen.

## Funktionen

- Simulierter QR-Code Scanner (manueller Texteingabe, da Streamlit keinen direkten Kamerazugriff hat)
- Affiliate-Registrierung und -Dashboard
- Vereinfachter Shop ohne Warenkorb/Checkout
- Automatische Zuordnung von Käufen zu Affiliates

## Installation

1. Stelle sicher, dass Python (3.7 oder höher) installiert ist

2. Installiere die erforderlichen Pakete:
```
pip install -r requirements.txt
```

## Lokale Ausführung

Starte die Anwendung mit:
```
streamlit run app.py
```

Die App wird automatisch im Browser unter `http://localhost:8501` geöffnet.

## Deployment

### Streamlit Community Cloud (kostenlos)

1. Lade deinen Code in ein öffentliches GitHub-Repository hoch
2. Registriere dich bei Streamlit Community Cloud
3. Wähle dein GitHub-Repository aus
4. Setze `app.py` als Hauptdatei
5. Klicke auf "Deploy"

### Alternative Hosting-Optionen

- Heroku
- Railway
- Digital Ocean
- AWS/GCP/Azure mit Docker

## Struktur

```
affiliate-qr-system-streamlit/
├── app.py                  # Hauptanwendung mit Streamlit
├── affiliate.db            # SQLite-Datenbank (wird automatisch erstellt)
└── requirements.txt        # Benötigte Python-Pakete
```

## Anmerkungen zur Streamlit-Version

Da Streamlit keine native Kamera-Integration bietet, wurde der QR-Code Scanner durch eine manuelle Eingabemöglichkeit ersetzt. In einer produktiven Umgebung könntest du:

1. Eine hybride Lösung mit Flask für den QR-Scanner und Streamlit für das Dashboard entwickeln
2. Eine progressive Web-App für den Scanner entwickeln, die auf Streamlit weiterleitet
3. Ein Framework wie Dash oder Gradio verwenden, das bessere Kamera-Integration bietet

## Anpassungen

Um die App für den Produktiveinsatz vorzubereiten, empfehlen wir:

1. Sichere Benutzerauthentifizierung hinzufügen
2. Produktdatenbank erstellen
3. Zahlungsabwicklung integrieren
4. Admin-Dashboard für die Verwaltung von Affiliates und Provisionen entwickeln
