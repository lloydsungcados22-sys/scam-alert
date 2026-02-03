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
