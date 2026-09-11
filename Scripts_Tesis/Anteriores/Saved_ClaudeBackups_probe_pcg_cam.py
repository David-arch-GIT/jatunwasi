import unreal, json

info = {}
# --- PCG API introspection ---
info['pcg_classes'] = [n for n in dir(unreal) if 'PCG' in n]
try:
    info['PCGGraph_methods'] = [m for m in dir(unreal.PCGGraph) if not m.startswith('_')]
except Exception as e:
    info['PCGGraph_methods'] = 'ERR:'+str(e)
for cls in ['PCGGraphFactory','PCGComponent','PCGSettings','PCGGraphInstance','PCGGraphInterface']:
    info['has_'+cls] = hasattr(unreal, cls)
# node/settings types available
info['pcg_settings_types'] = [n for n in dir(unreal) if n.startswith('PCG') and ('Settings' in n or 'Sampler' in n or 'Difference' in n or 'Data' in n or 'Spawner' in n)]

# --- set top-down viewport camera over plaza center (0,-1000) ---
cam_ok = False
try:
    ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    loc = unreal.Vector(0.0, -1000.0, 4200.0)
    rot = unreal.Rotator(0.0, -90.0, 0.0)  # roll,pitch,yaw -> look straight down
    ues.set_level_viewport_camera_info(loc, rot)
    cam_ok = True
except Exception as e:
    info['cam_err'] = str(e)
info['cam_ok'] = cam_ok

with open(r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/pcg_probe.json","w",encoding="utf-8") as f:
    json.dump(info, f, indent=1)
unreal.log("PCG_PROBE_DONE")
