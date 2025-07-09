import subprocess

# List of known large file hashes
hashes = [
    "e2521622",
    "cd87adef",
    "af982892",
    "f163b153"
]

# Run git command to list all objects
output = subprocess.check_output(["git", "rev-list", "--objects", "--all"], text=True)

# Print matching objects
for line in output.splitlines():
    if any(h in line for h in hashes):
        print(line)