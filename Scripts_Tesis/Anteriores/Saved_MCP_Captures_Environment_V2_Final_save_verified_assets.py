import json
import os
import unreal

assets = [
    "/Game/JWN/Environment/Materials/M_JW_Ground_PBR_V2",
    "/Game/JWN/Environment/Materials/MI_JW_Ground_PBR_V2",
]
results = {path: unreal.EditorAssetLibrary.save_asset(path, only_if_is_dirty=False) for path in assets}
if not all(results.values()):
    raise RuntimeError("Verified material asset save failed: " + str(results))
out = os.path.join(unreal.Paths.project_saved_dir(), "MCP_Captures", "Environment_V2_Final", "save_assets.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
unreal.log("ENV_V2_ASSETS_SAVED=" + json.dumps(results))
