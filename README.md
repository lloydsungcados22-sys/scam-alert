# CheckMoYan — Is this a scam? Paste it. We'll explain it.

AI-powered scam detector built for the Philippines. Paste suspicious messages (SMS, Messenger, Email) and get an explainable verdict: **Safe**, **Suspicious**, or **Scam**, with confidence score, reasons, and next-step actions.

## Features

- **Viral flow:** Paste → Analyze → Verdict card → Shareable result
- **Philippines-first:** Detects GCash/Maya/SSS/PhilHealth/bank/job/loan/romance/investment scam patterns
- **Freemium:** Free tier (limited checks/day) and Premium/Pro via GCash & Maya (manual receipt validation)
- **Admin panel:** Plan config, user management, upgrade request approval
- **Privacy:** Raw messages not stored by default; only verdict and category are saved

## Tech Stack

- **Streamlit** (single repo, multipage)
- **SQLite** (default) or **Snowflake** for persistence (see Database)
- **OpenAI API** for analysis
- Config via **Streamlit secrets** (no hard-coded payment details or limits)

## Setup

### 1. Clone and install

```bash
cd CheckMoYan
pip install -r requirements.txt
```

### 2. Configure Streamlit secrets

Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill in your values (or use Streamlit Cloud's **Settings → Secrets**):

```toml
OPENAI_API_KEY = "sk-..."
ADMIN_PASSWORD = "your-secure-admin-password"

[PAYMENTS.gcash]
number = "09XX XXX XXXX"
name = "Your Name"

[PAYMENTS.maya]
number = "09XX XXX XXXX"
name = "Your Maya Name"

[PAYMENTS.plans.premium]
price_php = 99
billing = "monthly"

[PAYMENTS.plans.pro]
price_php = 499
billing = "monthly"

# Daily limits (top-level keys)
PAYMENTS_free_daily_limit = 5
PAYMENTS_premium_daily_limit = 9999
```

**Important:** Payment details (GCash/Maya numbers, plan prices, daily limits) and `OPENAI_API_KEY` are read **only from** `secrets.toml` — there are no hardcoded values in the app.

The app supports both nested `[PAYMENTS.gcash]` / `[PAYMENTS.plans.premium]` and top-level `PAYMENTS_free_daily_limit` / `PAYMENTS_premium_daily_limit`. If limits are missing, defaults are 5 (free) and 9999 (premium).

### Monetization (plans)

| Plan    | Price (from secrets) | Features |
|---------|----------------------|----------|
| **Free** | ₱0 | Limited checks/day, basic verdict & reasons, shareable warning text, no screenshot upload |
| **Premium** | e.g. ₱99/mo | Unlimited checks, advanced explainers, downloadable Scam Report (PDF), priority support |
| **Pro** | e.g. ₱499/mo | Everything in Premium, priority verification, bulk check (coming soon), dedicated support |

Family mode, team seats, API access, and export dashboard have been removed from the plan copy; pricing and payment instructions are fully configurable via `secrets.toml`.

### 3. Run locally

```bash
streamlit run app.py
```

Open `http://localhost:8501`.

### 4. Deploy on Streamlit Cloud

1. Push the repo to GitHub.
2. In [Streamlit Community Cloud](https://share.streamlit.io), connect the repo and set the run command to `streamlit run app.py`.
3. Add the same secrets under **Settings → Secrets** (paste the contents of your `secrets.toml` or add each key).

## Project structure

```
CheckMoYan/
├── app.py                 # Main entry, multipage routing
├── requirements.txt
├── README.md
├── .streamlit/
│   └── config.toml        # Optional: theme, layout
├── db/
│   ├── __init__.py
│   ├── schema.py          # SQLite schema and init
│   └── queries.py         # CRUD for users, usage, scans, upgrade_requests
├── services/
│   ├── __init__.py
│   ├── analysis.py        # OpenAI analysis and JSON parsing
│   ├── auth.py            # Email session, admin check
│   ├── usage.py           # Rate limits (free vs premium)
│   └── payments.py        # Payment config from secrets, upgrade requests
├── components/
│   ├── __init__.py
│   ├── ui.py              # Cards, badges, CTAs, toasts
│   ├── landing.py         # Landing page sections
│   └── verdict.py         # Verdict card and share snippet
└── pages/
    ├── 1_Landing.py
    ├── 2_Scam_Checker.py
    ├── 3_Community_Alerts.py
    ├── 4_Pricing.py
    └── 5_Admin.py
```

## Database

**Default: SQLite** — file `checkmoyan.db` is created on first run.

**Optional: Snowflake** — if you add a `[SNOWFLAKE]` section to `.streamlit/secrets.toml`, the app uses Snowflake instead of SQLite. Tables are created automatically on first run. Copy the `[SNOWFLAKE]` block from `.streamlit/secrets.toml.example` and set:

- `account`, `user`, `password` (required)
- `warehouse` (default `COMPUTE_WH`), `database` (default `CHECKMOYAN`), `schema` (default `PUBLIC`)
- `role` (optional)

Create the database (and optionally warehouse/schema) in Snowflake; the app will create these tables in that database/schema:

- **users** — email, plan (free/premium/pro), premium_until, created_at
- **usage** — email, date, checks_count (for daily limits)
- **scans** — id, email, ts, verdict, confidence, category, signals_json, msg_hash
- **upgrade_requests** — id, email, plan, method, ref, receipt_path, status, ts, admin_notes, approved_until
- **community_alerts** — id, category, summary, ts

Dummy stats (messages analyzed today, scams detected, trending categories) are seeded for first-run demo.

## Security & disclaimers

- Admin page is protected by `ADMIN_PASSWORD` from secrets.
- Raw message content is not stored; only verdict, category, and hash.
- User inputs are sanitized; upgrade receipts are stored server-side for admin review.
- **Disclaimer:** AI can be wrong. Users are advised to verify with official channels (banks, GCash, Maya, SSS, PhilHealth).

## License

MIT (or your choice).
