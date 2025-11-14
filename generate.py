import os
import sys
import json
import subprocess

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    root = os.path.dirname(os.path.abspath(__file__))
    roleinfo_path = os.path.join(root, "data", "BinData", "role", "roleinfo.json")
    textmaps_dir = os.path.join(root, "data", "Textmaps")
    roleinfo = load_json(roleinfo_path)
    role_ids = [it.get("Id") for it in roleinfo if isinstance(it, dict) and it.get("Id") is not None and it.get("Id") < 2000]
    all_langs = [d for d in os.listdir(textmaps_dir) if os.path.isdir(os.path.join(textmaps_dir, d))]
    langs = sys.argv[1:] if len(sys.argv) > 1 else all_langs
    for lang in langs:
        for rid in role_ids:
            out_dir = os.path.join(root, "resource", lang, str(rid))
            os.makedirs(out_dir, exist_ok=True)
            subprocess.run([sys.executable, os.path.join(root, "cli.py"), str(rid), lang], check=True)

if __name__ == "__main__":
    main()