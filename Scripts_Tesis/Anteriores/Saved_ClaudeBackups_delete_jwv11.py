import unreal, json
from collections import Counter
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ALLOW = {"HEDGE", "TOPIARY", "SHRUB", "FLOWER"}
deleted = Counter()
skipped = []
seen_cats = Counter()
for a in list(eas.get_all_level_actors()):
    lab = a.get_actor_label()
    if not lab.startswith("JW_V11_"):
        continue
    parts = lab.split("_")
    cat = parts[2] if len(parts) > 2 else ""
    seen_cats[cat] += 1
    if cat in ALLOW:
        eas.destroy_actor(a)
        deleted[cat] += 1
    else:
        skipped.append(lab)
res = {
    "deleted_by_cat": dict(deleted),
    "deleted_total": sum(deleted.values()),
    "seen_cats": dict(seen_cats),
    "skipped_non_veg": skipped,
}
json.dump(res, open(r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/delete_jwv11_result.json", "w"), indent=1)
unreal.log("DELETE_JWV11_DONE deleted=%d skipped=%d" % (sum(deleted.values()), len(skipped)))
