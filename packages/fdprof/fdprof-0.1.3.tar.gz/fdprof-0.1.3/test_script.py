#!/usr/bin/env python3
import os
import tempfile
import time


def log_event(message: str):
    print(f"EVENT: {time.time():.9f} {message}")


print("Starting test script...")
log_event("Test script started")

# Open some files to increase FD usage
files = []
temp_dir = tempfile.gettempdir()
for i in range(5):
    temp_path = os.path.join(temp_dir, f"test_file_{i}.txt")
    f = open(temp_path, "w")
    files.append(f)
    f.write(f"Test content {i}")
    log_event(f"Opened file {i}")

time.sleep(0.5)

# Close some files
for i in range(2):
    files[i].close()
    log_event(f"Closed file {i}")

time.sleep(0.5)

# Close remaining files
for f in files[2:]:
    f.close()

log_event("All files closed")
print("Test script completed")
