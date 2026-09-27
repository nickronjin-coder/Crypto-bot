# Crypto Bot v14 — Secure Bybit Demo Backend

Architecture:

iPhone PWA -> HTTPS backend -> Bybit Demo API

This backend is intentionally fail-closed:
- Demo Trading only by default
- Real-money orders disabled
- No withdrawals
- API secrets are environment variables, never frontend code
- Kill switch
- Spot symbols only
- BTCUSDT and ETHUSDT by default
- Risk capped at 0.25%

## 1. Run locally

Python 3.12+:

    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

Copy `.env.example` to `.env` and fill in the Demo API key/secret.

Then:

    uvicorn app:app --host 0.0.0.0 --port 8000

Open:

    http://127.0.0.1:8000/health

## 2. Important

Do NOT put the API key or secret into:
- index.html
- JavaScript
- GitHub Pages
- screenshots
- ChatGPT

GitHub Pages is static hosting; the secret belongs on the backend/server.

## 3. Bybit Demo

The backend uses Bybit's Demo Trading endpoint through pybit with `demo=True`.
Do not use a Testnet key with this backend.

## 4. What this version does

It can:
- check backend health
- read Bybit Demo BTC/USDT and ETH/USDT prices
- read the Demo wallet balance
- start/stop/kill the bot state
- set a small risk limit

It CANNOT place orders yet. That lock is deliberate.

## 5. Next development stage

After deployment:
1. connect the iPhone UI to this backend;
2. verify Demo balance and live market data;
3. add real historical-data validation;
4. run the strategy in Demo without order execution;
5. add order execution only after validation gates pass.
