import os
import sys
import json

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def find_by_id(items, key, value):
    for it in items:
        if it.get(key) == value:
            return it
    return None

def filter_by(items, key, value):
    return [it for it in items if it.get(key) == value]

def main():
    if len(sys.argv) < 2:
        print("usage: python cli.py <role_id> [lang_code]")
        sys.exit(1)
    try:
        role_id = int(sys.argv[1])
    except Exception:
        print("invalid role_id")
        sys.exit(1)
    lang_code = sys.argv[2] if len(sys.argv) >= 3 else "zh-Hans"
    root = os.path.dirname(os.path.abspath(__file__))
    role_dir = os.path.join(root, "data", "BinData", "role")
    data_root = os.path.join(root, "data", "BinData")
    textmaps_root = os.path.join(root, "data", "Textmaps", lang_code)
    roleinfo = load_json(os.path.join(role_dir, "roleinfo.json"))
    roletag = load_json(os.path.join(role_dir, "roletag.json"))
    roleskin = load_json(os.path.join(role_dir, "roleskin.json"))
    rolequalityinfo = load_json(os.path.join(role_dir, "rolequalityinfo.json"))
    rolemorph = load_json(os.path.join(role_dir, "rolemorph.json"))
    roleanimaudio = load_json(os.path.join(role_dir, "roleanimaudio.json"))
    autorole = load_json(os.path.join(role_dir, "autorole.json"))
    specialenergybar = load_json(os.path.join(role_dir, "specialenergybar.json"))
    role = find_by_id(roleinfo, "Id", role_id)
    if not role:
        print(json.dumps({"error": "role not found", "role_id": role_id}, ensure_ascii=False, indent=2))
        sys.exit(2)
    quality = find_by_id(rolequalityinfo, "Id", role.get("QualityId"))
    tag_ids = role.get("Tag") or []
    tags = [find_by_id(roletag, "Id", t) for t in tag_ids]
    tags = [t for t in tags if t]
    skin_default = find_by_id(roleskin, "Id", role.get("SkinId"))
    skins_all = filter_by(roleskin, "RoleId", role_id)
    seb = find_by_id(specialenergybar, "Id", role.get("SpecialEnergyBarId"))
    morphs = filter_by(rolemorph, "RoleId", role_id)
    audios = filter_by(roleanimaudio, "RoleId", role_id)
    auto = find_by_id(autorole, "Id", role_id)

    def load_items(rel_path):
        return load_json(os.path.join(data_root, rel_path))

    element = None
    if role.get("ElementId") is not None:
        element = find_by_id(load_items(os.path.join("element_info", "elementinfo.json")), "Id", role.get("ElementId"))

    base_property = None
    if role.get("PropertyId") is not None:
        base_property = find_by_id(load_items(os.path.join("KSCProperty", "kscbaseproperty.json")), "Id", role.get("PropertyId"))

    skill = []
    # 技能按 SkillGroupId 归属角色
    skills_all = load_items(os.path.join("skill", "skill.json"))
    if role.get("Id") is not None:
        skill = [it for it in skills_all if it.get("SkillGroupId") == role.get("Id")]

    damage_items = load_items(os.path.join("damage", "damage.json"))
    damage_text_items = load_items(os.path.join("damage_text", "damagetext.json"))
    payload_items = load_items(os.path.join("DamagePayload", "damagepayload.json"))
    damage_by_id = {d.get("Id"): d for d in damage_items}
    damagetext_by_id = {t.get("Id"): t for t in damage_text_items}
    payload_by_id = {p.get("Id"): p for p in payload_items}
    for s in skill:
        details = []
        for did in s.get("DamageList", []):
            d = damage_by_id.get(did)
            dt = None
            pl = None
            if d:
                dt = damagetext_by_id.get(d.get("DamageTextType")) or damagetext_by_id.get(d.get("Element"))
                pl = payload_by_id.get(d.get("PayloadId"))
            details.append({"id": did, "damage": d, "damage_text": dt, "payload": pl})
        s["damage_details"] = details

    weapon = None
    if role.get("InitWeaponItemId") is not None:
        weapon_items = load_items(os.path.join("weapon", "weaponconf.json"))
        for it in weapon_items:
            if it.get("ItemId") == role.get("InitWeaponItemId"):
                weapon = it
                break

    lockon_default = None
    if role.get("LockOnDefaultId") is not None:
        lockon_default = find_by_id(load_items(os.path.join("LockOn", "lockonconfig.json")), "Id", role.get("LockOnDefaultId"))

    lockon_look = None
    if role.get("LockOnLookOnId") is not None:
        lockon_look = find_by_id(load_items(os.path.join("LockOn", "lockonconfig.json")), "Id", role.get("LockOnLookOnId"))

    skill_tree_nodes = []
    if role.get("SkillTreeGroupId") is not None:
        st_items = load_items(os.path.join("skillTree", "skilltree.json"))
        skill_tree_nodes = [it for it in st_items if it.get("NodeGroup") == role.get("SkillTreeGroupId")]

    resonant_chain_nodes = []
    if role.get("ResonantChainGroupId") is not None:
        rc_items = load_items(os.path.join("resonate_chain", "resonantchain.json"))
        resonant_chain_nodes = [it for it in rc_items if it.get("GroupId") == role.get("ResonantChainGroupId")]

    trial_role = None
    if role.get("TrialRole") is not None:
        trial_role = find_by_id(load_items(os.path.join("trial_role", "trialroleinfo.json")), "Id", role.get("TrialRole"))

    # 将 SkillTree 节点中的 SkillId 关联到技能对象
    skill_by_id = {s.get("Id"): s for s in (skill or []) if isinstance(s, dict)}
    for node in skill_tree_nodes:
        sid = node.get("SkillId")
        if sid in skill_by_id:
            node["Skill"] = skill_by_id[sid]
    result = {
        "role": role,
        "quality": quality,
        "tags": tags,
        "skins": {
            "default": skin_default,
            "all": skins_all
        },
        "special_energy_bar": seb,
        "morph": morphs,
        "audio": audios,
        "autorole": auto,
        "element": element,
        "base_property": base_property,
        "skill": skill,
        "weapon": weapon,
        "lockon_default": lockon_default,
        "lockon_look": lockon_look,
        "skill_tree_nodes": skill_tree_nodes,
        "resonant_chain_nodes": resonant_chain_nodes,
        "trial_role": trial_role
    }
    def build_textmap():
        mt_path = os.path.join(textmaps_root, "multi_text", "MultiText.json")
        if os.path.exists(mt_path):
            items = load_json(mt_path)
            return {it.get("Id"): it.get("Content") for it in items if isinstance(it.get("Id"), str)}
        return {}

    textmap = build_textmap()

    def apply_textmap(v):
        if isinstance(v, str):
            return textmap.get(v, v)
        if isinstance(v, list):
            return [apply_textmap(x) for x in v]
        if isinstance(v, dict):
            return {k: apply_textmap(val) for k, val in v.items()}
        return v

    localized = apply_textmap(result)

    out_dir = os.path.join(root, "resource", lang_code, str(role_id))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "item.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(localized, f, ensure_ascii=False, indent=2)

    print(json.dumps(localized, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()