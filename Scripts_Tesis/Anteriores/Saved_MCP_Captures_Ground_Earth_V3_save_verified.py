import json
import os
import unreal

paths=["/Game/JWN/Environment/Materials/M_JW_Ground_Earth_V3","/Game/JWN/Environment/Materials/MI_JW_Ground_Earth_V3"]
result={p:unreal.EditorAssetLibrary.save_asset(p,only_if_is_dirty=False) for p in paths}
if not all(result.values()):raise RuntimeError("Ground Earth V3 asset save failed: "+str(result))
out=os.path.join(unreal.Paths.project_saved_dir(),"MCP_Captures","Ground_Earth_V3","save_result.json")
with open(out,"w",encoding="utf-8") as f:json.dump(result,f,indent=2)
unreal.log("GROUND_5B_ASSETS_SAVED="+json.dumps(result))
