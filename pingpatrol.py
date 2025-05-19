import os
import time
import threading
import logging
import json
import csv
import smtplib
from email.mime.text import MIMEText
from ping3 import ping
from flask import Flask, render_template, request, redirect, url_for, jsonify
from dotenv import load_dotenv

translations = {
    "de": {
        "dashboard": "Dashboard",
        "settings": "Einstellungen",
        "status": "E-Mail versenden",
        "active": "Aktiv",
        "inactive": "Inaktiv",
        "send_test": "Test-E-Mail senden",
        "start": "Start",
        "stop": "Stop",
        "log_loading": "Lade Logs...",
        "interval": "Ping-Intervall (Sekunden):",
        "devices": "Geräte (IP,Hostname):",
        "font": "Schriftart:",
        "fontsize": "Schriftgröße:",
        "language": "Sprache:",
        "save": "Speichern",
        "small": "Klein",
        "medium": "Mittel",
        "large": "Groß",
        "space": "Space Mono",
        "jersey": "Jersey 10",
        "german": "Deutsch",
        "english": "Englisch"
    },
    "en": {
        "dashboard": "Dashboard",
        "settings": "Settings",
        "status": "Send email",
        "active": "Active",
        "inactive": "Inactive",
        "send_test": "Send test email",
        "start": "Start",
        "stop": "Stop",
        "log_loading": "Loading logs...",
        "interval": "Ping interval (seconds):",
        "devices": "Devices (IP,Hostname):",
        "font": "Font:",
        "fontsize": "Font size:",
        "language": "Language:",
        "save": "Save",
        "small": "Small",
        "medium": "Medium",
        "large": "Large",
        "space": "Space Mono",
        "jersey": "Jersey 10",
        "german": "German",
        "english": "English"
    }
}

device_status = []

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
DEVICE_FILE = os.getenv("DEVICE_FILE", "devices.csv")
CONFIG_FILE = "config.json"

logging.basicConfig(filename="log.csv", level=logging.INFO, format="%(asctime)s,%(message)s")

app = Flask(__name__)

def load_devices():
    try:
        with open(DEVICE_FILE, newline='') as f:
            reader = csv.reader(f)
            return [row for row in reader if len(row) == 2]
    except FileNotFoundError:
        return []

def save_devices(devices_text):
    with open(DEVICE_FILE, "w", newline='') as f:
        f.write(devices_text.strip())

def load_config():
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        # Standardwert: Deutsch, Intervall in Sekunden
        return {"interval_seconds": 10, "language": "de"}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def send_email(subject, body):
    msg = MIMEText(body)
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = subject
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        logging.error(f"Email error: {e}")

is_running = False
ping_thread = None

def ping_loop():
    global is_running, device_status
    while is_running:
        config = load_config()
        devices = load_devices()
        unreachable = []
        status_list = []

        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for row in devices:
            if len(row) != 2:
                logging.warning(f"Ungültige Zeile: {row}")
                continue
            ip, name = row
            result = ping(ip, timeout=2)
            status = "OK" if result else "FAIL"
            logging.info(f"{ip} ({name}): {status}")
            status_list.append(f"{now} {ip} ({name}): {status}")
            if not result:
                unreachable.append(f"{name} ({ip})")

        device_status = status_list

        if unreachable:
            send_email("PingPatrol: Geräte nicht erreichbar", "\n".join(unreachable))

        sleep_total = config.get("interval_seconds", 10)
        for _ in range(sleep_total):
            if not is_running:
                break
            time.sleep(1)

@app.route("/", methods=["GET"])
def index():
    config = load_config()
    interval = config.get("interval_seconds", 10)
    language = config.get("language", "de")
    devices = load_devices()
    devices_text = "\n".join([",".join(row) for row in devices])
    texts = translations.get(language, translations["de"])
    return render_template(
        "index.html",
        interval=interval,
        devices=devices_text,
        language=language,
        texts=texts
    )

@app.route("/update", methods=["POST"])
def update():
    try:
        interval = int(request.form.get("interval", 10))
        devices_text = request.form.get("devices", "")
        language = request.form.get("language", "de")
        lines = [line for line in devices_text.strip().split("\n") if "," in line]
        save_config({"interval_seconds": interval, "language": language})
        save_devices("\n".join(lines))
    except Exception as e:
        logging.error(f"Update Error: {e}")
    return redirect(url_for("index"))

@app.route("/send-test", methods=["POST"])
def send_test():
    config = load_config()
    devices = load_devices()
    interval = config.get("interval_seconds", 10)
    body_lines = [f"Aktuelles Ping-Intervall: {interval} Sekunden", "", "Geräteliste:"]
    for ip, name in devices:
        body_lines.append(f"{name} ({ip})")
    send_email("PingPatrol Test", "\n".join(body_lines))
    return redirect(url_for("index"))

@app.route("/start", methods=["POST"])
def start():
    global is_running, ping_thread
    if not is_running:
        is_running = True
        ping_thread = threading.Thread(target=ping_loop, daemon=True)
        ping_thread.start()
    return redirect(url_for("index"))

@app.route("/stop", methods=["POST"])
def stop():
    global is_running
    is_running = False
    return redirect(url_for("index"))

@app.route("/debug-log", methods=["GET"])
def debug_log():
    global device_status
    return jsonify(lines=device_status)
    
@app.route("/status", methods=["GET"])
def status():
    return jsonify(running=is_running)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)