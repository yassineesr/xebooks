import os
import hashlib
import json
from urllib.request import urlretrieve, ProxyHandler, build_opener
from argparse import ArgumentParser

def sha256sum(filename: str) -> str:
    sha256 = hashlib.sha256()
    with open(filename, "rb") as f:
        while True:
            data = f.read(8192)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()

def download_file(url: str, destination_filename: str, proxy: str = None) -> None:
    if proxy:
        proxy_support = ProxyHandler({'http': proxy, 'https': proxy})
        opener = build_opener(proxy_support)
        os.environ['http_proxy'] = proxy
        os.environ['https_proxy'] = proxy
        path, _ = opener.retrieve(url, destination_filename)
    else:
        path, _ = urlretrieve(url, destination_filename)

def MainCheck(json_file: str, proxy: str = None) -> None:
    allowed_filenames = ["manifest-8.json", "manifest.json"]

    if json_file not in allowed_filenames:
        print(f"Error: Invalid filename. Allowed filenames are {', '.join(allowed_filenames)}")
        return

    with open(json_file, "r") as f:
        manifest = json.load(f)

    for entry in manifest:
        destination_dir = os.path.join("roles", entry["role"], "files")
        os.makedirs(destination_dir, exist_ok=True)
        destination_filename = os.path.join(destination_dir, entry["name"])

        if os.path.exists(destination_filename):
            if sha256sum(destination_filename) != entry["checksum"]:
                print(f"Checksum mismatch for {entry['name']}")
                return
            else:
                print(f"Exists ✅ Checksum matches for {os.path.join('roles', entry['role'], 'files', entry['name'])}")
        else:
            print(f"Downloading {os.path.join(destination_dir, entry['name'])}...", end="\r")
            download_file(entry["url"], destination_filename, proxy)
            if sha256sum(destination_filename) != entry["checksum"]:
                print(f"Checksum mismatch for {entry['name']}")
                return
            print(f"✅ Checksum matches for {destination_filename}")

    print("All files downloaded and validated successfully.")


parser = ArgumentParser(description="Download and validate files specified in a manifest JSON.")
parser.add_argument("json_file", type=str, choices=["manifest-8.json", "manifest.json"],help="JSON file.")
parser.add_argument("-p", "--proxy", type=str, default=None,help="Proxy address and port to use for downloads. Optional.")

args = parser.parse_args()
MainCheck(args.json_file, args.proxy)
