import sqlite3
import os
from datetime import datetime

# Define Paths
BASE_DIR = os.path.expanduser("~/consensus-project")
DB_PATH = os.path.join(BASE_DIR, "consensus_memory.db")

def initialize_ckbms():
    """Objective 1: Create the unified memory storage system."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables for cross-platform data synchronization
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_vitals 
                      (timestamp TEXT, bmi REAL, weight REAL, keto_status TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS system_logs 
                      (timestamp TEXT, agent_name TEXT, action_taken TEXT, status TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS financial_tracker 
                      (timestamp TEXT, bill_name TEXT, amount REAL, due_date TEXT)''')
    
    conn.commit()
    conn.close()
    print(f"✅ CKBMS Initialized at {DB_PATH}")

def log_initial_state():
    """Logs the migration completion as the first system memory."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO system_logs VALUES (?, ?, ?, ?)", 
                   (datetime.now().isoformat(), "System_Architect", "AIL Migration Complete", "Success"))
    conn.commit()
    conn.close()
    print("✅ Initial system state recorded in long-term memory.")

if __name__ == "__main__":
    initialize_ckbms()
    log_initial_state()