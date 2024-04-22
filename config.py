import os
import hashlib
import json
from urllib.request import urlretrieve
from sys import exit, stdout
import sys

def sha256sum(filename: str) -> str:
    sha256 = hashlib.sha256()
    with open(filename, "rb") as f:
        while True:
            data = f.read(8192)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()

allowed_filenames = ["manifest-8.json", "manifest.json"]
json_file = sys.argv[1]

if json_file not in allowed_filenames:
    print(f"Error: Invalid filename. Allowed filenames are {', '.join(allowed_filenames)}")
    sys.exit(1)

with open(json_file, "r") as f:
    manifest = json.load(f)

for entry in manifest:
    destination_dir = os.path.join("roles", entry["role"], "files")
    os.makedirs(destination_dir, exist_ok=True)
    destination_filename = os.path.join(destination_dir, entry["name"])

    if os.path.exists(destination_filename):
        if sha256sum(destination_filename) != entry["checksum"]:
            print(f"Checksum mismatch for {entry['name']}")
            exit(1)
        else:
            print(f"Exists ✅ Checksum matches for {os.path.join('roles', entry['role'], 'files', entry['name'])}")
    else:  
        print('not found') 
        print(f"Downloading {os.path.join(destination_dir, entry['name'])}...", end="\r")
        path, _ = urlretrieve(entry["url"], os.path.join("roles", entry["role"], "files", entry["name"]))
        if sha256sum(destination_filename) != entry["checksum"]:
            print(f"Checksum mismatch for {entry['name']}")
            exit(1)
        print(f"✅ Checksum matches for {destination_filename}")

    stdout.write("\r\033[K")  

print("All files downloaded and validated successfully.")