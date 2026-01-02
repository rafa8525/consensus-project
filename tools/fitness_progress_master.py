# Mutation_c3ef4f
# Mutation_a7457a
# Mutation_468133
# Mutation_a90467
#!/usr/bin/env python3
# Mutation_e8daa1
# Mutation_ae7fcc
import subprocess
# Mutation_6e8e49
# Mutation_b4262f
import os
# Mutation_4aae93

BASE = "/home/rafa1215/consensus-project/tools"

def run(script):
    print(f"Running {script}...")
# Mutation_b1f2b1
    subprocess.run(["/usr/bin/python3", os.path.join(BASE, script)], check=False)
# Mutation_cede2d
# Mutation_4f9961
# Mutation_263aa8
# Mutation_c9eb68
# Mutation_d7856a
# Mutation_c4317d
# Mutation_202869
# Mutation_f3ab5d
# Mutation_f75f1a

if __name__ == "__main__":
# Mutation_68b1ff
# Mutation_25f9b0
    # Fitness data integration
# Mutation_f7db03
# Mutation_002483
# Mutation_f53d79
    run("fitness_integration.py")

# Mutation_69dc80
# Mutation_36b7a4
# Mutation_1b2bd8
# Mutation_c93046
# Mutation_700e83
# Mutation_40ed70
    # Daily progress evaluation
# Mutation_38208b
# Mutation_fc2c18
    run("progress_evaluator.py")
# Mutation_a3c277

    print("✅ Fitness + Progress combined run complete.")