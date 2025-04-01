# Deployment-Anleitung

## Konfiguration der Base-URL

Beim Deployment musst du die Base-URL aktualisieren, damit die QR-Codes auf deine tatsächliche App-URL verweisen.

### Option 1: Secrets.toml aktualisieren

1. Öffne die Datei `.streamlit/secrets.toml`
2. Ändere den Wert von `base_url` zur URL deiner gehosteten App
   ```
   base_url = "https://deine-app-url.streamlit.app"
   ```

### Option 2: Bei Streamlit Cloud

Wenn du Streamlit Cloud verwendest:

1. Gehe zu deinem App-Dashboard
2. Klicke auf ⚙️ (Einstellungen) > Secrets
3. Füge folgendes hinzu:
   ```
   base_url = "https://deine-app-url.streamlit.app"
   ```

### Option 3: Umgebungsvariable (für Heroku, Railway, etc.)

Setze die Umgebungsvariable `STREAMLIT_BASE_URL`:

```
STREAMLIT_BASE_URL=https://deine-app-url.herokuapp.com
```

## Streamlit Cloud Deployment

1. Lade deinen Code in ein GitHub-Repository hoch
2. Gehe zu [share.streamlit.io](https://share.streamlit.io)
3. Melde dich an und klicke auf "New app"
4. Wähle dein Repository, Branch und die Datei `app.py`
5. Klicke auf "Deploy!"
6. **Wichtig**: Nach dem Deployment, füge die App-URL als Secret hinzu:
   - Klicke auf ⚙️ > Secrets
   - Füge `base_url = "https://[deine-app-id].streamlit.app"` hinzu

## Heroku Deployment

1. Erstelle eine `Procfile`:
   ```
   web: streamlit run app.py --server.port=$PORT
   ```

2. Setze die Umgebungsvariable:
   ```
   heroku config:set STREAMLIT_BASE_URL=https://deine-app.herokuapp.com
   ```

3. Deploye deine App:
   ```
   git push heroku main
   ```

## Lokale URLs für Entwicklung

Während der Entwicklung können QR-Codes auf `localhost` verweisen. Du kannst dies testen, indem du:

1. Die App auf deinem Computer startest
2. Den QR-Code mit einem Smartphone scannst, während dein Computer und Smartphone im selben Netzwerk sind
3. Die IP-Adresse deines Computers anstelle von `localhost` verwendest, z.B. `http://192.168.1.100:8501`

Aktualisiere dafür den Wert in `.streamlit/secrets.toml`:
```
base_url = "http://192.168.1.100:8501"  # Ersetze mit deiner lokalen IP
```
