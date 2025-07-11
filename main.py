from flask import Flask, render_template, request
from config import EMAIL_MITTENTE, EMAIL_DESTINATARIO, EMAIL_PASSWORD
import smtplib, ssl
from email.message import EmailMessage

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    messaggio = None
    if request.method == "POST":
        # Email di test
        msg = EmailMessage()
        msg['Subject'] = "✔️ Test notifica voli Ryanair"
        msg['From'] = EMAIL_MITTENTE
        msg['To'] = EMAIL_DESTINATARIO
        msg.set_content("La configurazione email è corretta.")

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(EMAIL_MITTENTE, EMAIL_PASSWORD)
            smtp.send_message(msg)
        messaggio = "✅ Email inviata con successo!"
    return render_template("index.html", messaggio=messaggio)
