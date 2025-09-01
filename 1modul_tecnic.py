
import json
import requests
import datetime
import numpy as np
import talib
from binance.client import Client

# Carrega claus Binance
with open("config.json") as f:
    config = json.load(f)
api_key = config["api_key"]
api_secret = config["api_secret"]

# Connecta amb Binance (mode lectura)
client = Client(api_key, api_secret)

# Paràmetres inicials
SYMBOL = "ETHUSDT"
INTERVAL = Client.KLINE_INTERVAL_1HOUR
LIMIT = 100

# Obtenir dades OHLCV
klines = client.get_klines(symbol=SYMBOL, interval=INTERVAL, limit=LIMIT)
closes = np.array([float(k[4]) for k in klines])
volumes = np.array([float(k[5]) for k in klines])
highs = np.array([float(k[2]) for k in klines])
lows = np.array([float(k[3]) for k in klines])

# Marcador 1: Volum creixent
volum_punts = 1 if volumes[-1] > np.mean(volumes[-10:-1]) * 1.2 else 0

# Marcador 2: Activitat de trading (volum i variació % últimes 3 vetes)
variacio = (closes[-1] - closes[-4]) / closes[-4]
activitat_punts = 1 if volumes[-1] > np.mean(volumes[-4:]) and abs(variacio) > 0.01 else 0

# Marcador 3: RSI / VWAP favorables
rsi = talib.RSI(closes, timeperiod=14)
rsi_punts = 1 if 45 <= rsi[-1] <= 65 else 0

vwap = np.sum((highs + lows + closes) / 3 * volumes) / np.sum(volumes)
vwap_punts = 1 if closes[-1] > vwap else 0

indicadors_punts = 1 if rsi_punts + vwap_punts >= 1 else 0

# Marcador 4: Patrons de preu (breakout simple)
canal_maxim = np.max(highs[-20:-1])
breakout_punts = 1 if closes[-1] > canal_maxim else 0

# Puntuació total
punts_totals = volum_punts + activitat_punts + indicadors_punts + breakout_punts

# Resultat final
resultat = {
    "cripto": SYMBOL,
    "punts_tecnics": punts_totals,
    "detall": {
        "volum_creixent": volum_punts,
        "activitat_trading": activitat_punts,
        "rsi_vwap": indicadors_punts,
        "patro_breakout": breakout_punts
    },
    "timestamp": datetime.datetime.now().isoformat()
}

# Guarda resultat a fitxer
with open("resultat_tecnic.json", "w") as f:
    json.dump(resultat, f, indent=4)

# Mostra per pantalla
print(json.dumps(resultat, indent=4))
