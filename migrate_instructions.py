import os
import shutil

# Define paths based on your GitHub directory structure
BASE_DIR = os.path.expanduser("~/consensus-project")
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")
MODULES_DIR = os.path.join(PROMPTS_DIR, "modules")

# List of files to migrate into the Adaptive Instruction Library
files_to_move = {
    "AI_Consensus_System_Unified_Prompt.txt": "master_blueprint.txt",
    "vpn_activation_feature.txt": "modules/vpn_activation.txt",
    "fitness_tracking_system_plan.txt": "modules/fitness_keto_logic.txt",
    "security_audit_schedule.txt": "modules/audit_protocol.txt",
    "centralized_knowledge_base.txt": "modules/ckbms_rules.txt",
    "progress_evaluation_plan.txt": "modules/self_optimization_logic.txt"
}

def migrate():
    # 1. Create sub-directories if they don't exist
    if not os.path.exists(MODULES_DIR):
        os.makedirs(MODULES_DIR)
        print(f"Created: {MODULES_DIR}")

    # 2. Move and rename files
    for original, new_name in files_to_move.items():
        source = os.path.join(BASE_DIR, original)
        destination = os.path.join(PROMPTS_DIR, new_name)

        if os.path.exists(source):
            shutil.copy2(source, destination)
            print(f"Successfully migrated: {original} -> {new_name}")
        else:
            print(f"Warning: Source file {original} not found in root.")

if __name__ == "__main__":
    migrate()
    print("\nStep 1 Complete: Adaptive Instruction Library (AIL) is now populated.")