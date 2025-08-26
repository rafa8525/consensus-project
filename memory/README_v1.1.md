# 🤖 AI Consensus System (Personal Build)

This is a **private AI automation system** that powers scheduling, agent control, memory tracking, email digests, insights, and a real-time dashboard — all fully offline and secure.

---

## ✅ Features

- 🧠 Multi-agent automation (planner, executor, etc.)
- 📅 Scheduled daily tasks + manual override
- 📋 Editable goals, emailed daily digest
- 🔍 Keyword search across memory logs
- 🕹 “Run Agent Now” button on dashboard
- 📊 Agent insights: usage, errors, goal counts
- ⬇ Download logs or memory as ZIP
- 🌗 Dark mode + 📱 mobile support
- 🔁 Auto-refresh dashboard (60 sec)
- 📦 Weekly local backup script

---

## 🖼 Screenshots

Your live dashboard:

```
![](docs/screenshots/dashboard.png)
```

(You can add more screenshots in `/docs/screenshots/` and duplicate this format.)

---

## 📂 File Structure

```plaintext
consensus-project/
├── agents/              # Digest, email, insights, backups
├── consensus/           # Scheduler, main loop
├── memory/              # Agent memory logs
├── logs/                # Agent execution logs
├── web/                 # Frontend (HTML + JS)
├── docs/screenshots/    # 📸 Screenshot folder (added in v1.1)
├── .env                 # Gmail app password config
├── dashboard.py         # Web UI server
├── scheduler.py         # Daily runner
├── README.md            # Original
└── README_v1.1.md       # This file
```

---

## ⚙ Setup Instructions

1. Install requirements:

```bash
pip install python-dotenv schedule
```

2. Add `.env` file:

```
EMAIL_ADDRESS=youremail@gmail.com
EMAIL_PASSWORD=your_app_password
```

3. Run the dashboard:

```bash
python dashboard.py
```

4. Optionally start the daily scheduler:

```bash
python consensus/scheduler.py
```

---

## 🧪 Features Added in v1.1

- 🌗 Dark mode + toggle
- 📱 Mobile viewport support
- 🕹 Manual “Run Agent Now” button
- 📊 Log insights (agent usage, errors, goal mentions)
- 📦 Export logs/memory as ZIP files
- 🧠 Weekly backup script (`agents/weekly_backup.py`)
- 🖼 Screenshot support + public docs folder

---

## 🛡 Privacy & Scope

This project is:
- 🔐 100% local and offline
- 🔧 Personal automation only (not for public use)
- 🗃 Stored privately on GitHub with ZIP archives optional

---

**Built for personal use. Not for public distribution.**
