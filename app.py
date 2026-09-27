import os, time, uuid
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pybit.unified_trading import HTTP

APP_VERSION = "v14-demo-backend"
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY", "")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET", "")
BYBIT_DEMO = os.getenv("BYBIT_DEMO", "true").lower() == "true"
ALLOW_LIVE = os.getenv("ALLOW_LIVE", "false").lower() == "true"
SYMBOLS = [s.strip().upper() for s in os.getenv("SYMBOLS", "BTCUSDT,ETHUSDT").split(",") if s.strip()]

state = {
    "status": "STOPPED",
    "equity": 500.0,
    "pnl": 0.0,
    "exposure": 0.0,
    "risk": 0.0025,
    "kill_switch": False,
    "mode": "DEMO",
    "version": APP_VERSION,
    "last_error": None,
}

app = FastAPI(title="Crypto Bot Secure Backend", version=APP_VERSION)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

def bybit_public():
    return HTTP(testnet=False, demo=BYBIT_DEMO)

def bybit_private():
    if not BYBIT_API_KEY or not BYBIT_API_SECRET:
        raise HTTPException(503, "Bybit API credentials are not configured on the backend.")
    return HTTP(testnet=False, demo=BYBIT_DEMO, api_key=BYBIT_API_KEY, api_secret=BYBIT_API_SECRET)

class RiskBody(BaseModel):
    risk: float

@app.get("/health")
def health():
    return {"ok": True, "version": APP_VERSION, "demo": BYBIT_DEMO, "live_orders_enabled": ALLOW_LIVE}

@app.get("/api/state")
def get_state():
    return state

@app.get("/api/bybit/ticker")
def ticker(symbol: str = "BTCUSDT"):
    symbol = symbol.upper()
    if symbol not in SYMBOLS:
        raise HTTPException(400, f"Symbol not allowed: {symbol}")
    try:
        r = bybit_public().get_tickers(category="spot", symbol=symbol)
        item = r["result"]["list"][0]
        return {
            "symbol": symbol,
            "lastPrice": float(item["lastPrice"]),
            "price24hPcnt": float(item.get("price24hPcnt", 0)),
            "time": int(time.time() * 1000),
        }
    except Exception as e:
        state["last_error"] = str(e)
        raise HTTPException(502, "Bybit market-data request failed.")

@app.get("/api/bybit/balance")
def balance():
    try:
        r = bybit_private().get_wallet_balance(accountType="UNIFIED", coin="USDT")
        return r
    except Exception as e:
        state["last_error"] = str(e)
        raise HTTPException(502, "Bybit balance request failed.")

@app.post("/api/start")
def start():
    if state["kill_switch"]:
        raise HTTPException(409, "Kill switch is active. Restart the backend before arming again.")
    state["status"] = "RUNNING"
    return state

@app.post("/api/stop")
def stop():
    state["status"] = "STOPPED"
    return state

@app.post("/api/kill")
def kill():
    state["status"] = "KILLED"
    state["kill_switch"] = True
    return state

@app.post("/api/risk")
def set_risk(body: RiskBody):
    if not (0.0005 <= body.risk <= 0.0025):
        raise HTTPException(400, "Risk must be between 0.05% and 0.25%.")
    state["risk"] = body.risk
    return state

@app.get("/api/trading-capability")
def trading_capability():
    # Deliberately fail-closed: this version never sends an order.
    return {
        "mode": "DEMO" if BYBIT_DEMO else "LIVE",
        "order_execution": "DISABLED",
        "reason": "Execution remains locked until historical validation and Demo verification are completed.",
    }
