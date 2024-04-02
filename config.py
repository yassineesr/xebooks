import os
import hashlib
import json
from urllib.request import urlretrieve
from sys import exit, stdout

def sha256sum(filename: str) -> str:
    sha256 = hashlib.sha256()
    with open(filename, "rb") as f:
        while True:
            data = f.read(8192)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()


with open("manifest.json", "r") as f:
    manifest = json.load(f)

for entry in manifest:
    os.makedirs(os.path.join("roles", entry["role"], "files"), exist_ok=True)
    print(f"Downloading {os.path.join('roles', entry['role'], 'files', entry['name'])}...", end="\r")
    path, _ = urlretrieve(entry["url"], os.path.join("roles", entry["role"], "files", entry["name"]))
    if sha256sum(path) != entry["checksum"]:
        print(f"Checksum mismatch for {entry['name']}")
        exit(1)
    stdout.write("\r\033[K")
    print(f"✅ Checksum matches for {os.path.join('roles', entry['role'], 'files', entry['name'])}")
