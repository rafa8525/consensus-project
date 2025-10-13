#!/usr/bin/env python3
import os
import datetime
import json
import requests
import csv

BASE_DIR = "/home/rafa1215/consensus-project/memory"
FITNESS_DIR = os.path.join(BASE_DIR, "logs/fitness")
IMPORT_DIR = os.path.join(BASE_DIR, "imports/samsung")
REPORT_FILE = os.path.join(FITNESS_DIR, "fitness_daily_summary.md")
GAMIFY_FILE = os.path.join(FITNESS_DIR, "gamification.json")
HEARTBEAT_FILE = os.path.join(BASE_DIR, "logs/system/heartbeat.md")

os.makedirs(FITNESS_DIR, exist_ok=True)
os.makedirs(IMPORT_DIR, exist_ok=True)

def heartbeat_log(status: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HEARTBEAT_FILE, "a") as f:
        f.write(f"[{ts}] FITNESS: {status}\n")

# ====== Samsung Health CSV Import ======
def fetch_samsung_health_data():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    file_path = os.path.join(IMPORT_DIR, f"samsung_health_{today}.csv")

    if not os.path.exists(file_path):
        return {"steps": 0, "hr": 0, "source": "missing"}

    steps = 0
    hr = 0
    try:
        with open(file_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if "steps" in row and row["steps"].isdigit():
                    steps += int(row["steps"])
                if "heart_rate" in row and row["heart_rate"].isdigit():
                    hr = max(hr, int(row["heart_rate"]))
        return {"steps": steps, "hr": hr, "source": file_path}
    except Exception as e:
        heartbeat_log(f"ERROR: Samsung CSV parse failed — {e}")
        return {"steps": 0, "hr": 0, "source": "error"}

# ====== Fitbit ======
def fetch_fitbit_data(token: str):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        r = requests.get("https://api.fitbit.com/1/user/-/activities/date/today.json", headers=headers)
        if r.status_code == 200:
            data = r.json()
            return {
                "steps": data.get("summary", {}).get("steps", 0),
                "hr": data.get("summary", {}).get("restingHeartRate", 0)
            }
    except Exception as e:
        heartbeat_log(f"ERROR: Fitbit fetch failed — {e}")
    return {"steps": 0, "hr": 0}

# ====== Google Fit (Pixel Watch) ======
def fetch_google_fit_data(token: str):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        r = requests.post(
            "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate",
            headers=headers,
            json={
                "aggregateBy": [{"dataTypeName": "com.google.step_count.delta"}],
                "bucketByTime": {"durationMillis": 86400000},
                "startTimeMillis": int((datetime.datetime.now() - datetime.timedelta(days=1)).timestamp() * 1000),
                "endTimeMillis": int(datetime.datetime.now().timestamp() * 1000)
            }
        )
        if r.status_code == 200:
            steps = r.json()["bucket"][0]["dataset"][0]["point"][0]["value"][0]["intVal"]
            return {"steps": steps, "hr": 0}
    except Exception as e:
        heartbeat_log(f"ERROR: Google Fit fetch failed — {e}")
    return {"steps": 0, "hr": 0}

# ====== COROS ======
def fetch_coros_data(token: str):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        r = requests.get("https://open.coros.com/api/v1/activity/latest", headers=headers)
        if r.status_code == 200:
            data = r.json()
            return {"steps": data.get("steps", 0), "hr": data.get("avg_hr", 0)}
    except Exception as e:
        heartbeat_log(f"ERROR: COROS fetch failed — {e}")
    return {"steps": 0, "hr": 0}

# ====== Gamification ======
def update_gamification(total_steps):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    gamify = {"streak": 0, "badges": [], "last_date": None}

    if os.path.exists(GAMIFY_FILE):
        try:
            gamify = json.loads(open(GAMIFY_FILE).read())
        except:
            pass

    # Update streak
    last_date = gamify.get("last_date")
    if last_date:
        diff = (datetime.datetime.strptime(today, "%Y-%m-%d") - datetime.datetime.strptime(last_date, "%Y-%m-%d")).days
        if diff == 1:
            gamify["streak"] = gamify.get("streak", 0) + 1
        elif diff > 1:
            gamify["streak"] = 1
    else:
        gamify["streak"] = 1

    gamify["last_date"] = today

    # Award badges
    if total_steps >= 10000 and "10k Steps Badge" not in gamify["badges"]:
        gamify["badges"].append("10k Steps Badge")
    if gamify["streak"] >= 7 and "Weekly Streak Badge" not in gamify["badges"]:
        gamify["badges"].append("Weekly Streak Badge")

    with open(GAMIFY_FILE, "w") as f:
        json.dump(gamify, f, indent=2)

    return gamify

# ====== Main ======
def generate_daily_report(tokens: dict):
    ts = datetime.datetime.now().strftime("%Y-%m-%d")
    report_lines = [f"# Fitness Report {ts}\n"]

    fitbit = fetch_fitbit_data(tokens.get("fitbit", ""))
    google_fit = fetch_google_fit_data(tokens.get("google_fit", ""))
    coros = fetch_coros_data(tokens.get("coros", ""))
    samsung = fetch_samsung_health_data()

    report_lines.append(f"- Fitbit: {fitbit['steps']} steps, HR {fitbit['hr']}")
    report_lines.append(f"- Pixel Watch (Google Fit): {google_fit['steps']} steps, HR {google_fit['hr']}")
    report_lines.append(f"- COROS Pace 3: {coros['steps']} steps, HR {coros['hr']}")
    report_lines.append(f"- Samsung Health: {samsung['steps']} steps, HR {samsung['hr']} ({samsung['source']})")

    total_steps = fitbit["steps"] + google_fit["steps"] + coros["steps"] + samsung["steps"]
    gamify = update_gamification(total_steps)

    report_lines.append(f"\n## Gamification\n- Current streak: {gamify['streak']} days\n- Badges: {', '.join(gamify['badges']) or 'None'}")

    with open(REPORT_FILE, "w") as f:
        f.write("\n".join(report_lines))

    heartbeat_log("SUCCESS: Fitness daily report + gamification generated")
    return REPORT_FILE

if __name__ == "__main__":
    tokens = {
        "fitbit": os.environ.get("FITBIT_TOKEN", ""),
        "google_fit": os.environ.get("GOOGLE_FIT_TOKEN", ""),
        "coros": os.environ.get("COROS_TOKEN", "")
    }
    try:
        report = generate_daily_report(tokens)
        print(f"Fitness report saved: {report}")
    except Exception as e:
        heartbeat_log(f"ERROR: Fitness integration failed — {e}")
