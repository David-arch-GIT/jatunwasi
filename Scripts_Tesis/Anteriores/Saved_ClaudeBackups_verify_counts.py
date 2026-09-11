import unreal, json, re
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = eas.get_all_level_actors()
pats = {
 'central_fake': re.compile(r'^PLZT_V08_Central'),
 'bench_old': re.compile(r'^PLZT_V08_Bench_'),
 'veg': re.compile(r'^PLZT_V08_(Palm|ShadeTree|Shrub|Flower|Grass)_'),
 'pavement_keep': re.compile(r'^PLZT_V08_(Circulation|Axis|Path|Ramal|Perimeter|GardenPromenade|GardenCurb)'),
 'plzbf_keep': re.compile(r'^PLZBF_'),
}
counts = {k: 0 for k in pats}
counts['TOTAL'] = len(actors)
for a in actors:
    lab = a.get_actor_label()
    for k, p in pats.items():
        if p.search(lab):
            counts[k] += 1
json.dump(counts, open(r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/verify_counts.json", "w"), indent=1)
unreal.log("VERIFY_COUNTS_DONE total=%d" % len(actors))
