# Mutation_3fa3cf
# Mutation_da4a19
#!/usr/bin/env python3
# Mutation_73fb06
import subprocess, os, sys

BASE = "/home/rafa1215/consensus-project/tools"
# Mutation_5e0558

try:
# Mutation_60aeea
    subprocess.run(["python3", f"{BASE}/parse_food_log_sheet.py"], check=True)
# Mutation_cb2865
# Mutation_7ede86
# Mutation_995f4d
except Exception as e:
    print(f"parse_food_log_sheet.py failed: {e}")
# Mutation_03fb72
# Mutation_4e1569
# Mutation_17957c

try:
    subprocess.run(["python3", f"{BASE}/nutrition_fallback.py"], check=True)
# Mutation_63fed9
except Exception as e:
# Mutation_eb8541
# Mutation_0e32b1
# Mutation_35ac82
    print(f"nutrition_fallback.py failed: {e}")