import unreal, json

labels = set(json.load(open(r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/delete_labels.json", encoding="utf-8")))
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = eas.get_all_level_actors()
deleted = []
skipped_guard = []
GUARD = ("Circulation", "Axis", "Path", "Ramal", "Perimeter", "Promenade", "Curb", "PLZBF")
for a in actors:
    lab = a.get_actor_label()
    if lab in labels:
        # hard safety guard: never destroy pavement / PLZBF even if listed
        if any(g in lab for g in GUARD) or not lab.startswith("PLZT_V08_"):
            skipped_guard.append(lab)
            continue
        eas.destroy_actor(a)
        deleted.append(lab)
res = {"deleted_count": len(deleted), "skipped_guard": skipped_guard, "requested": len(labels)}
json.dump(res, open(r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/delete_result.json", "w", encoding="utf-8"), indent=1)
unreal.log("DELETE_LEGACY_DONE deleted=%d skipped_guard=%d" % (len(deleted), len(skipped_guard)))
