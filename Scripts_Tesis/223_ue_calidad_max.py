import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/calidad_max.json"
res = {"ok": [], "err": []}
DEST = "/Game/FotosAntano/Encuadradas"
for a in unreal.EditorAssetLibrary.list_assets(DEST, recursive=False):
    base = a.split(".")[0]
    t = unreal.EditorAssetLibrary.load_asset(base)
    if not isinstance(t, unreal.Texture2D): continue
    try:
        t.set_editor_property("never_stream", True)          # siempre a full resolucion, sin bajar mips
        t.set_editor_property("lod_bias", 0)
        try: t.set_editor_property("filter", unreal.TextureFilter.TF_TRILINEAR)
        except Exception: pass
        try: t.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_SHARPEN3)
        except Exception: pass
        unreal.EditorAssetLibrary.save_asset(base, only_if_is_dirty=False)
        res["ok"].append(t.get_name())
    except Exception as e:
        res["err"].append(t.get_name()[:14]+":"+str(e)[:40])
res["n"] = len(res["ok"])
open(OUT,"w").write(json.dumps(res, indent=1))
