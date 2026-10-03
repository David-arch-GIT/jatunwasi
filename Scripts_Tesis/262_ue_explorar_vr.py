import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/explora_vr.json"
res={"pawns":[], "narration_bp":[], "widget_interaction":[], "objetos":[]}
EAL=unreal.EditorAssetLibrary
# 1) buscar BPs de pawn / interaccion en /Game
for a in EAL.list_assets("/Game", recursive=True):
    low=a.lower()
    nm=a.split("/")[-1].split(".")[0]
    if ("pawn" in low or "vrpawn" in low or "player" in low) and low.endswith("."+nm.lower()):
        res["pawns"].append(nm)
    if "narration" in low or "narrationpoint" in low:
        res["narration_bp"].append(nm)
res["pawns"]=sorted(set(res["pawns"]))[:20]
res["narration_bp"]=sorted(set(res["narration_bp"]))[:20]
# 2) objetos candidatos en el nivel (props figurativos)
eas=unreal.EditorActorSubsystem()
KEYS=["Maniqui","maniqui","Vitrina","Tarka","zampona","acordeon","charango","quena","Santo","Virgen","Nino","San_","Cristo","Santa_","Habito","habito","Retablo","Catre","Arcon","Lavatorio","Breviario","Crucifijo","Aparador","CamaDosel","Cartela","Pulpito","Confesionario","Altar","Bell","Pozo"]
for act in eas.get_all_level_actors():
    lbl=act.get_actor_label()
    if any(k in lbl for k in KEYS):
        loc=act.get_actor_location()
        res["objetos"].append({"lbl":lbl,"loc":[round(loc.x),round(loc.y),round(loc.z)]})
res["n_obj"]=len(res["objetos"])
open(OUT,"w").write(json.dumps(res,indent=1))
