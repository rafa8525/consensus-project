file_path = "consensus/file_io_check.txt"

try:
    # Write to the file
    with open(file_path, "a") as f:
        f.write("\nConfirmed write access.")

    # Read from the file
    with open(file_path, "r") as f:
        contents = f.read()

    print("✅ File contents:")
    print(contents)

except Exception as e:
    print("❌ File access failed:", str(e))
