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



        
def verify_hash_or_download(file : str, entry : str,proxy: str = None):
    while sha256sum(file) != entry["checksum"] :
        print(f"❌checksum error for {file}", end="\r" )
        download_file(entry["url"], file, proxy)
    return print(f"✅checksum verified for {file}" )


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
            verify_hash_or_download(destination_filename,entry, proxy ) 
            
        else:
            print(f"Downloading {os.path.join(destination_dir, entry['name'])}...", end="\r")
            download_file(entry["url"], destination_filename, proxy)
            verify_hash_or_download(destination_filename,entry, proxy) 
          
    print("All files downloaded and validated successfully.")


       

parser = ArgumentParser(description="Download and validate files specified in a manifest JSON.")
parser.add_argument("json_file", type=str, choices=["manifest-8.json", "manifest.json"],help="JSON file.")
parser.add_argument("-p", "--proxy", type=str, default=None,help="Proxy address and port to use for downloads. Optional.")

args = parser.parse_args()
MainCheck(args.json_file, args.proxy)
