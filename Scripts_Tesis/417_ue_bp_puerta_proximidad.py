# 417_ue_bp_puerta_proximidad.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: crear BP_PuertaProximidad (/Game/JWN/Blueprints): puerta colonial de DOS HOJAS que se
#   abre sola cuando el visitante se acerca y se cierra cuando se aleja.
#   Componentes: Zona (Sphere r=380, solo overlap con Pawn), HojaIzq / HojaDer (StaticMesh con el
#   ORIGEN EN LA BISAGRA; HojaIzq en x=-AnchoHoja, HojaDer en x=+AnchoHoja; sin malla hasta tener los
#   modelos de Tripo), colision BlockAll en hojas, sin efecto en NavMesh, sin sombra.
#   Variable Abrir (bool). Importa el sonido SW_Puerta_Crujido + ATT_Puerta (300/1500).
#   El grafo (overlap -> MoveComponentTo de cada hoja + sonido) se cablea por HTTP aparte.
import unreal, json, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/bp_puerta.json"
BP = "/Game/JWN/Blueprints/BP_PuertaProximidad"
res = {"err": None}
try:
    t = unreal.AssetImportTask()
    t.set_editor_property("filename", r"C:/UnrealProjects/JatunWasiNawpakay/Saved/SynthAudio/SW_Puerta_Crujido.wav")
    t.set_editor_property("destination_path", "/Game/JWN/Audio/Puertas")
    t.set_editor_property("automated", True); t.set_editor_property("replace_existing", True); t.set_editor_property("save", True)
    at = unreal.AssetToolsHelpers.get_asset_tools()
    at.import_asset_tasks([t])
    p = "/Game/JWN/Audio/Puertas/ATT_Puerta"
    att = unreal.load_asset(p) if unreal.EditorAssetLibrary.does_asset_exist(p) else at.create_asset("ATT_Puerta", "/Game/JWN/Audio/Puertas", unreal.SoundAttenuation, unreal.SoundAttenuationFactory())
    s = att.get_editor_property("attenuation")
    s.set_editor_property("attenuation_shape_extents", unreal.Vector(300, 0, 0)); s.set_editor_property("falloff_distance", 1500.0)
    s.set_editor_property("spatialize", True); att.set_editor_property("attenuation", s)
    unreal.EditorAssetLibrary.save_loaded_asset(att, False)
    res["sound"] = unreal.EditorAssetLibrary.does_asset_exist("/Game/JWN/Audio/Puertas/SW_Puerta_Crujido")

    if unreal.EditorAssetLibrary.does_asset_exist(BP):
        bp = unreal.load_asset(BP)
    else:
        f = unreal.BlueprintFactory(); f.set_editor_property("parent_class", unreal.Actor)
        bp = at.create_asset("BP_PuertaProximidad", "/Game/JWN/Blueprints", unreal.Blueprint, f)
    sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    lib = unreal.SubobjectDataBlueprintFunctionLibrary
    handles = sds.k2_gather_subobject_data_for_blueprint(bp)
    names = {str(lib.get_variable_name(lib.get_data(h))): h for h in handles}
    root = handles[0]
    def add(cls, name):
        if name in names:
            return lib.get_object(lib.get_data(names[name]))
        hh, fail = sds.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root, new_class=cls, blueprint_context=bp))
        sds.rename_subobject(hh, unreal.Text(name))
        return lib.get_object(lib.get_data(hh))
    zona = add(unreal.SphereComponent, "Zona")
    zona.set_editor_property("sphere_radius", 380.0)
    zona.set_collision_profile_name("Trigger")
    zona.set_editor_property("generate_overlap_events", True)
    zona.set_editor_property("can_ever_affect_navigation", False)
    zona.set_editor_property("relative_location", unreal.Vector(0, 0, 100))
    for nm, x in (("HojaIzq", -200.0), ("HojaDer", 200.0)):
        c = add(unreal.StaticMeshComponent, nm)
        c.set_editor_property("relative_location", unreal.Vector(x, 0, 0))
        c.set_collision_profile_name("BlockAll")
        c.set_editor_property("can_ever_affect_navigation", False)
        c.set_editor_property("cast_shadow", False)
        c.set_mobility(unreal.ComponentMobility.MOVABLE)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    unreal.EditorAssetLibrary.save_loaded_asset(bp, False)
    res["components"] = [str(lib.get_variable_name(lib.get_data(h))) for h in sds.k2_gather_subobject_data_for_blueprint(bp)]
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res, indent=1))
