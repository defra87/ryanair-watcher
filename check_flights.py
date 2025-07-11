import smtplib
import ssl
from email.message import EmailMessage
from datetime import datetime, timedelta
import requests
from config import TRATTE, ADULTI, BAMBINI, NEONATI, EMAIL_MITTENTE, EMAIL_DESTINATARIO, EMAIL_PASSWORD

API_URL = "https://www.ryanair.com/api/booking/v4/it-it/availability"

def cerca_volo(tratta):
    prezzi_trovati = []
    data_start = datetime.strptime(tratta['dal'], "%Y-%m-%d")
    data_end = datetime.strptime(tratta['al'], "%Y-%m-%d")

    giorno = data_start
    while giorno <= data_end:
        ritorno = giorno + timedelta(days=tratta['max_notti'])
        if ritorno > data_end:
            break

        params = {
            "ADT": ADULTI,
            "CHD": BAMBINI,
            "INF": NEONATI,
            "DateOut": giorno.strftime("%Y-%m-%d"),
            "DateIn": ritorno.strftime("%Y-%m-%d"),
            "Origin": tratta["origine"],
            "Destination": tratta["destinazione"],
            "RoundTrip": "true"
        }

        try:
            r = requests.get(API_URL, params=params)
            data = r.json()
            for trip in data.get("trips", []):
                for date in trip["dates"]:
                    for flight in date.get("flights", []):
                        for fare in flight.get("regularFare", {}).get("fares", []):
                            prezzo = fare["amount"]["value"]
                            if prezzo <= tratta['soglia']:
                                prezzi_trovati.append((giorno.strftime("%Y-%m-%d"), ritorno.strftime("%Y-%m-%d"), prezzo))
        except:
            pass

        giorno += timedelta(days=1)
    return prezzi_trovati

def invia_email(risultati):
    if not risultati:
        return
    contenuto = "Ecco le offerte trovate:\n\n"
    for r in risultati:
        contenuto += f"Andata: {r[0]} - Ritorno: {r[1]} - Prezzo: €{r[2]}\n"

    msg = EmailMessage()
    msg['Subject'] = "✈️ Offerte Ryanair trovate!"
    msg['From'] = EMAIL_MITTENTE
    msg['To'] = EMAIL_DESTINATARIO
    msg.set_content(contenuto)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(EMAIL_MITTENTE, EMAIL_PASSWORD)
        smtp.send_message(msg)

# MAIN
risultati_globali = []
for tratta in TRATTE:
    risultati = cerca_volo(tratta)
    risultati_globali.extend(risultati)

invia_email(risultati_globali)
