import os
import json

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    root = os.path.dirname(os.path.abspath(__file__))
    base = os.path.join(root, "resource", "zh-Hans")
    out_path = os.path.join(base, "names.json")
    results = []
    if not os.path.isdir(base):
        print(json.dumps({"error": "lang_dir_missing", "path": base}, ensure_ascii=False))
        return
    for entry in os.listdir(base):
        try:
            rid_int = int(entry)
        except Exception:
            rid_int = None
        if rid_int is not None and rid_int >= 2000:
            continue
        dir_path = os.path.join(base, entry)
        item_path = os.path.join(dir_path, "item.json")
        if os.path.isdir(dir_path) and os.path.isfile(item_path):
            data = load_json(item_path)
            role = data.get("role") or {}
            rid = role.get("Id")
            name = role.get("Name")
            if rid is not None and name is not None:
                results.append({"Id": rid, "Name": name})
    results.sort(key=lambda x: x["Id"])
    os.makedirs(base, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(json.dumps({"count": len(results), "output": out_path}, ensure_ascii=False))

if __name__ == "__main__":
    main()