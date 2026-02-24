from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

# ===================== USGS =====================
USGS = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"

# ===================== IRIS =====================
IRIS = "https://service.iris.edu/fdsnws/event/1/query?format=geojson&limit=1"

# ===================== JMA (Japón) =====================
JMA = "https://api.p2pquake.net/v2/history?limit=1"

# ===================== SSN MÉXICO =====================
SSN = "https://www.ssn.unam.mx/rss/ultimos-sismos.xml"

# ---------------------------------------------------
def get_usgs():
    r = requests.get(USGS, timeout=5).json()
    s = r["features"][0]
    p = s["properties"]
    c = s["geometry"]["coordinates"]
    return {
        "fuente": "USGS",
        "magnitud": p["mag"],
        "lugar": p["place"],
        "hora": datetime.utcfromtimestamp(p["time"]/1000).isoformat(),
        "lat": c[1],
        "lon": c[0],
        "profundidad": c[2]
    }

# ---------------------------------------------------
def get_iris():
    r = requests.get(IRIS, timeout=5).json()
    s = r["features"][0]
    p = s["properties"]
    c = s["geometry"]["coordinates"]
    return {
        "fuente": "IRIS",
        "magnitud": p["mag"],
        "lugar": p["place"],
        "hora": p["time"],
        "lat": c[1],
        "lon": c[0],
        "profundidad": c[2]
    }

# ---------------------------------------------------
def get_jma():
    r = requests.get(JMA, timeout=5).json()[0]
    return {
        "fuente": "JMA Japón",
        "magnitud": r.get("magnitude"),
        "lugar": r.get("hypocenter", {}).get("name"),
        "hora": r.get("time"),
        "lat": r.get("hypocenter", {}).get("latitude"),
        "lon": r.get("hypocenter", {}).get("longitude"),
        "profundidad": r.get("hypocenter", {}).get("depth")
    }

# ---------------------------------------------------
def get_ssn():
    r = requests.get(SSN, timeout=5)
    soup = BeautifulSoup(r.text, "xml")
    item = soup.find("item")
    title = item.title.text
    desc = item.description.text

    return {
        "fuente": "SSN México",
        "magnitud": title.split("M ")[1].split(",")[0],
        "lugar": title,
        "hora": datetime.utcnow().isoformat(),
        "lat": None,
        "lon": None,
        "profundidad": None
    }

# ===================== COMBINADO =====================
@app.route("/api/sismo")
def sismo():
    data = []
    try: data.append(get_usgs())
    except: pass
    try: data.append(get_iris())
    except: pass
    try: data.append(get_jma())
    except: pass
    try: data.append(get_ssn())
    except: pass

    return jsonify(data)

# ===================== SIMULACRO =====================
@app.route("/api/simulacro")
def simulacro():
    return jsonify({
        "fuente": "SIMULACRO",
        "magnitud": 8.2,
        "lugar": "Ciudad de México",
        "hora": datetime.utcnow().isoformat(),
        "lat": 19.4326,
        "lon": -99.1332,
        "profundidad": 10
    })

# ===================== TICKER =====================
@app.route("/api/ticker")
def ticker():
    s = get_usgs()
    return jsonify({"mensaje": f"Sismo M{s['magnitud']} en {s['lugar']} (USGS)"})

@app.route("/")
def home():
    return "MONITOREO SISMICO MULTI-RED ACTIVO"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
