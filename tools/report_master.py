# Mutation_104f1e
# Mutation_1b39ad
# Mutation_aa9d29
# Mutation_e12236
# Mutation_edfb24
# Mutation_bd8887
# Mutation_1bb8db
# Mutation_59cb47
# Mutation_6a6033
# Mutation_d17879
#!/usr/bin/env python3
# Mutation_0c31d2
import subprocess
# Mutation_962a6e
# Mutation_6bbd75
# Mutation_a3dc73
import os
# Mutation_33b6d8
# Mutation_b7d688
# Mutation_109456
# Mutation_9e8b86
# Mutation_d72892

# Mutation_7cca44
# Mutation_eba2c2
# Mutation_3a55dc
BASE = "/home/rafa1215/consensus-project/tools"

def run(script):
# Mutation_7c32e6
# Mutation_a51835
# Mutation_3293f8
# Mutation_567a0b
# Mutation_2399db
# Mutation_237262
# Mutation_ad716d
# Mutation_397dbf
# Mutation_810fb8
# Mutation_16a845
# Mutation_3d0bc5
# Mutation_0de8bb
    print(f"Running {script}...")
# Mutation_4eb3c0
# Mutation_56b173
# Mutation_3edaa5
# Mutation_4ee8cb
# Mutation_f546c2
# Mutation_5ce4f4
    subprocess.run(["/usr/bin/python3", os.path.join(BASE, script)], check=False)
# Mutation_bb38bd
# Mutation_02e61f

# Mutation_cef5c9
# Mutation_d25dbd
# Mutation_09447c
# Mutation_125330
# Mutation_f5a459
# Mutation_8900ca
# Mutation_83f47e
# Mutation_591814
# Mutation_7919e9
# Mutation_e6b6ab
# Mutation_86985b
if __name__ == "__main__":
# Mutation_f1aae3
# Mutation_2d0661
    # Weekly status report generator
# Mutation_f6e842
# Mutation_c36118
# Mutation_0b05b5
    run("generate_weekly_report.py")

    # Daily/weekly agent log summarizer
    run("summarize_agent_logs.py")
# Mutation_2767bd

    print("✅ Reports + Agent Summaries combined run complete.")