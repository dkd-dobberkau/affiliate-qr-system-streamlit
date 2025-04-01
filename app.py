# app.py - Streamlit Affiliate QR-System
import streamlit as st
import sqlite3
import qrcode
import io
import base64
import uuid
import os
from datetime import datetime
from PIL import Image
import time

# Seitenkonfiguration und Titel
st.set_page_config(page_title="Affiliate QR-System", page_icon="🔍", layout="centered")

# Datenbank-Setup
def init_db():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'affiliate.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS affiliates (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS purchases (
        id TEXT PRIMARY KEY,
        affiliate_id TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (affiliate_id) REFERENCES affiliates (id)
    )
    ''')
    conn.commit()
    conn.close()
    return db_path

# Hilfsfunktion für Datenbankverbindungen
def get_db_connection():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'affiliate.db')
    return sqlite3.connect(db_path)

# QR-Code generieren
def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Bild für Streamlit aufbereiten
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    buffered.seek(0)
    return buffered

# Funktion zum Registrieren eines Kaufs
def register_purchase(affiliate_id):
    if not affiliate_id:
        return False, "Kein Affiliate angegeben"
    
    purchase_id = str(uuid.uuid4())
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO purchases (id, affiliate_id) VALUES (?, ?)',
                  (purchase_id, affiliate_id))
    conn.commit()
    conn.close()
    
    return True, purchase_id

# Funktion zum Abrufen der Affiliate-Daten und Statistiken
def get_affiliate_data(affiliate_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Affiliate-Daten abrufen
    cursor.execute('SELECT name, email FROM affiliates WHERE id = ?', (affiliate_id,))
    affiliate = cursor.fetchone()
    
    # Käufe zählen
    cursor.execute('SELECT COUNT(*) FROM purchases WHERE affiliate_id = ?', (affiliate_id,))
    purchase_count = cursor.fetchone()[0]
    
    conn.close()
    
    if affiliate:
        return {
            'name': affiliate[0],
            'email': affiliate[1],
            'purchase_count': purchase_count
        }
    return None

# Affiliate registrieren
def register_affiliate(name, email):
    affiliate_id = str(uuid.uuid4())
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO affiliates (id, name, email) VALUES (?, ?, ?)',
                      (affiliate_id, name, email))
        conn.commit()
        conn.close()
        return True, affiliate_id
    except sqlite3.IntegrityError:
        # E-Mail bereits vorhanden
        return False, "Diese E-Mail-Adresse ist bereits registriert."
    except Exception as e:
        return False, str(e)

# Affiliate-Login
def login_affiliate(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM affiliates WHERE email = ?', (email,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return True, result[0]
    return False, "E-Mail nicht gefunden."

# Datenbank initialisieren
init_db()

# Streamlit Session State initialisieren
if 'view' not in st.session_state:
    st.session_state.view = 'home'
if 'affiliate_id' not in st.session_state:
    st.session_state.affiliate_id = None

# Navigation mit automatischem Rerun
def navigate_to(view):
    st.session_state.view = view
    st.rerun()

# Logout
def logout():
    st.session_state.affiliate_id = None
    navigate_to('home')

# Haupttitel
st.title("Affiliate QR-System")

# URL-Parameter für direkten Zugriff überprüfen
query_params = st.query_params
if "view" in query_params:
    st.session_state.view = query_params["view"]
    # Wenn ein Affiliate-Parameter vorhanden ist, speichern
    if "ref" in query_params:
        st.session_state.ref_affiliate_id = query_params["ref"]

# Seiten-Routing basierend auf Session State
if st.session_state.view == 'home':
    st.subheader("Willkommen beim Affiliate QR-System")
    st.write("Dieses System ermöglicht es dir, QR-Codes zu scannen und als Affiliate Provisionen zu erhalten.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("QR-Code scannen", use_container_width=True):
            navigate_to('scanner')
    with col2:
        if st.button("Als Affiliate anmelden", use_container_width=True):
            navigate_to('affiliate_login')
    
    st.markdown("---")
    st.write("Noch kein Affiliate?")
    if st.button("Als Affiliate registrieren"):
        navigate_to('affiliate_register')

elif st.session_state.view == 'scanner':
    st.subheader("QR-Code Scanner")
    st.write("Da Streamlit keinen direkten Kamerazugriff hat, gib bitte die QR-Code-Daten manuell ein:")
    
    qr_data = st.text_input("QR-Code-Inhalt (z.B. URL mit ref-Parameter)")
    
    if st.button("Weiterleiten"):
        if qr_data:
            # URL Parameter extrahieren
            if "?ref=" in qr_data:
                affiliate_id = qr_data.split("?ref=")[1].split("&")[0]
                st.session_state.ref_affiliate_id = affiliate_id
                navigate_to('shop')
            else:
                st.error("Ungültiger QR-Code: Kein Affiliate-Parameter gefunden.")
        else:
            st.warning("Bitte gib den QR-Code-Inhalt ein.")
    
    if st.button("Zurück zur Startseite"):
        navigate_to('home')

elif st.session_state.view == 'affiliate_register':
    st.subheader("Als Affiliate registrieren")
    st.write("Registriere dich als Affiliate, um deinen eigenen QR-Code zu erhalten.")
    
    with st.form("register_form"):
        name = st.text_input("Name")
        email = st.text_input("E-Mail", type="default")
        submit = st.form_submit_button("Registrieren")
        
        if submit:
            if name and email:
                success, result = register_affiliate(name, email)
                if success:
                    st.session_state.affiliate_id = result
                    st.session_state.show_success = True
                    navigate_to('affiliate_dashboard')
                else:
                    st.error(f"Fehler bei der Registrierung: {result}")
            else:
                st.warning("Bitte fülle alle Felder aus.")
    
    if st.button("Zurück zur Startseite"):
        navigate_to('home')

elif st.session_state.view == 'affiliate_login':
    st.subheader("Als Affiliate anmelden")
    
    with st.form("login_form"):
        email = st.text_input("E-Mail", type="default")
        submit = st.form_submit_button("Anmelden")
        
        if submit:
            if email:
                success, result = login_affiliate(email)
                if success:
                    st.session_state.affiliate_id = result
                    st.session_state.show_success = True
                    navigate_to('affiliate_dashboard')
                else:
                    st.error(result)
            else:
                st.warning("Bitte gib deine E-Mail ein.")
    
    if st.button("Zurück zur Startseite"):
        navigate_to('home')

elif st.session_state.view == 'affiliate_dashboard':
    if not st.session_state.affiliate_id:
        st.warning("Bitte melde dich zuerst an.")
        navigate_to('affiliate_login')
    else:
        affiliate_data = get_affiliate_data(st.session_state.affiliate_id)
        
        if affiliate_data:
            # Erfolgsmeldung anzeigen, falls vorhanden
            if st.session_state.get('show_success', False):
                st.success("Anmeldung erfolgreich!")
                # Zurücksetzen, damit die Meldung beim nächsten Laden nicht mehr angezeigt wird
                st.session_state.show_success = False
            
            st.subheader(f"Affiliate Dashboard")
            st.write(f"Willkommen zurück, **{affiliate_data['name']}**!")
            
            st.markdown("### Dein QR-Code")
            st.write("Teile diesen QR-Code, damit Kunden deinen Affiliate-Link scannen können.")
            
            # QR-Code mit der Base-URL und Affiliate-ID generieren
            # Konfigurierbare Base-URL für verschiedene Umgebungen
            base_url = st.secrets.get("base_url", "http://localhost:8501")
            
            # Stelle sicher, dass die URL das Schema (http:// oder https://) enthält
            if not base_url.startswith("http://") and not base_url.startswith("https://"):
                base_url = "https://" + base_url
                
            # Füge /shop-Pfad hinzu oder verwende query parameter
            shop_url = f"{base_url}/?view=shop"
            
            qr_data = f"{shop_url}&ref={st.session_state.affiliate_id}"
            qr_img = generate_qr_code(qr_data)
            
            st.image(qr_img, caption="Dein Affiliate QR-Code", width=300)
            
            st.markdown(f"**Dein Affiliate-Link:**")
            st.code(qr_data)
            
            st.markdown("### Deine Statistiken")
            st.metric("Anzahl der Käufe über deinen Link", affiliate_data['purchase_count'])
            
            if st.button("Abmelden"):
                logout()
        else:
            st.error("Affiliate-Daten konnten nicht gefunden werden.")
            if st.button("Zurück zur Anmeldung"):
                navigate_to('affiliate_login')

elif st.session_state.view == 'shop':
    st.subheader("Unser Shop")
    st.write("Hier ist unser Produkt - einfach auf den Button klicken, um es zu kaufen.")
    
    # Erfolgsmeldung anzeigen
    if st.session_state.get('purchase_success', False):
        st.success("Vielen Dank für deinen Kauf! Die Provision wurde dem Affiliate gutgeschrieben.")
        st.session_state.purchase_success = False
    elif st.session_state.get('purchase_success_no_affiliate', False):
        st.success("Vielen Dank für deinen Kauf!")
        st.session_state.purchase_success_no_affiliate = False
    
    # Platzhalter-Bild
    st.image("https://via.placeholder.com/400x300?text=Produktbild", caption="Super Artikel")
    
    st.markdown("### Produkt: Super Artikel")
    st.write("Ein fantastisches Produkt, das du unbedingt haben solltest!")
    
    # Affiliate-ID aus der URL oder Session State holen
    affiliate_id = None
    query_params = st.query_params
    if "ref" in query_params:
        affiliate_id = query_params["ref"]
        st.session_state.ref_affiliate_id = affiliate_id
    elif "ref_affiliate_id" in st.session_state:
        affiliate_id = st.session_state.ref_affiliate_id
    
    if affiliate_id:
        if st.button("Jetzt kaufen"):
            success, result = register_purchase(affiliate_id)
            if success:
                st.session_state.purchase_success = True
                st.rerun()
            else:
                st.error(f"Beim Kauf ist ein Fehler aufgetreten: {result}")
    else:
        st.warning("Kein Affiliate-Parameter gefunden. Der Kauf wird keinem Affiliate zugeordnet.")
        if st.button("Jetzt kaufen (ohne Affiliate)"):
            st.session_state.purchase_success_no_affiliate = True
            st.rerun()
    
    if st.button("Zurück zur Startseite"):
        navigate_to('home')
