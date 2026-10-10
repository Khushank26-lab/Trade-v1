# Weekly Bullish Scanner (Scorecard v6 website)

Type a **profit target %** and a **time frame**; the site scans every NSE + BSE stock it has data for, applies the Scorecard v6
technical rules, and shortlists the setups that *historically* reached that target within that time frame most often,
with sample sizes, entry/stop/targets, risk-based quantity, live prices and a best-effort fundamentals/news check.

**There is no 99% guarantee.** The site shows the real historical frequency (usually far below 99% for 3-5% weekly targets).
If you set "Min historical hit rate" to 99 it will honestly report that nothing qualifies and show the closest matches.

## How it works
1. `app/universe.py` merges the NSE equity list and the BSE "List of Scrips" (target 7,500+ listings; de-duplicated by ISIN by default).
2. `app/ingest.py` downloads ~5 years of daily OHLCV per ticker (Yahoo Finance, `.NS` / `.BO`) into SQLite; the worker refreshes it daily at 17:30 IST.
3. `app/scoring.py` computes the 12-point technical score for every day of history (market filter, EMA stack, RSI, MACD, volume, 52W high, ADX, stochastic, relative strength, structure, ATR, entry trigger/pattern).
4. `app/engine.py` answers your query: takes stocks scoring high enough *today*, checks the target is realistic for the stock's volatility and time frame, and measures how often that stock (and all stocks, blended) hit +target before the stop in the past. Ranked by a conservative lower bound.
5. `app/enrich.py` checks ROE, growth, debt, cash flow, analyst view and recent headlines for the shortlist (Yahoo data; missing data = "unverified").
6. `app/live.py` + the front end poll live prices every 30 s (about 15 min delayed on the free feed).

## Deploy (Ubuntu VPS + Docker + free HTTPS)
1. **Server:** Ubuntu 22.04/24.04, 2 vCPU, 4 GB RAM, 30 GB disk (DigitalOcean, Hetzner, AWS Lightsail ...; Mumbai region is nice for latency).
2. **Domain:** add an `A` record (e.g. `scanner.yourdomain.com`) pointing to the server IP.
3. **Install Docker:** `curl -fsSL https://get.docker.com | sh`
4. **Copy the project:** `scp -r weekly-bullish-scanner user@SERVER:~/` then `ssh user@SERVER` and `cd weekly-bullish-scanner`.
5. **Configure:** `cp .env.example .env` and edit `DOMAIN`, `ADMIN_TOKEN`.
6. **Stock universe files** (put in `./data/`):
   - NSE: `EQUITY_L.csv` is auto-downloaded; if that fails, download "Securities available for trading - Equity" from nseindia.com and save it as `data/EQUITY_L.csv`.
   - BSE: bseindia.com -> Markets -> Equity -> List of Scrips -> download CSV -> save as `data/bse_scrips.csv`.
7. **Start:** `docker compose up -d --build`
8. **First data load** runs automatically (30-60+ minutes for the full universe): `docker compose logs -f worker`. The site shows "initial data load" until done.
9. **Open** `https://scanner.yourdomain.com`.
10. **Operate:** force a refresh with `curl -X POST https://scanner.yourdomain.com/api/admin/refresh -H "X-Admin-Token: YOUR_TOKEN"`; back up `./data`; update with `git pull && docker compose up -d --build`.

Quick local test without Docker: `pip install -r requirements.txt`, put the universe files in `data/`, then
`python -m app.ingest --limit 200 && python -m app.build && uvicorn app.main:app --reload`.
Offline logic test (synthetic data): `python tests/test_core.py`.

## Going from "delayed" to real-time
Replace `_one()` in `app/live.py` with a call to a broker/vendor API (Upstox, Angel One SmartAPI, Zerodha Kite Connect, Dhan, TrueData...).
Free broker APIs usually need a funded account and per-user login tokens. Showing exchange data publicly can require a vendor/redistribution licence.

## Important limits & compliance
- Hit rates are historical frequencies; markets change. Signals from the same period are correlated; thinning is applied, but sample sizes can still be small.
- Fundamentals, growth and news are NOT part of the historical hit rate (no point-in-time data). They only filter the final shortlist.
- Yahoo data can have gaps, wrong splits/adjustments or missing tickers. For serious use buy NSE/BSE-grade data.
- In India, publicly recommending specific securities can fall under SEBI research-analyst / investment-adviser rules. Keep this an educational screener with prominent disclaimers and take legal advice before opening it to the public or charging for it.
