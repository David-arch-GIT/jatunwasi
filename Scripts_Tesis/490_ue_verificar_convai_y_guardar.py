# 490_ue_verificar_convai_y_guardar.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: tras pruebas PIE (que apagan/encienden Convai con 400), verificar que Convai quedo ENCENDIDO
#   (Adela auto_initialize_session, pawn auto_initialize_session y microfono mute=True) y SOLO entonces
#   guardar BP_XRPawn y el nivel. Si algo no esta bien, NO guarda y lo reporta. Opcional SALIR=True cierra
#   el editor (para recompilar el plugin JWGuia).
import unreal, json
try:
    SALIR
except NameError:
    SALIR = False
r = {}
a = [x for x in unreal.EditorLevelLibrary.get_all_level_actors() if x.get_actor_label() == "Adela_Convai"][0]
for c in a.get_components_by_class(unreal.ActorComponent):
    if c.get_class().get_name() == "ConvaiChatbotComponent": r["adela_autoinit"] = c.get_editor_property("auto_initialize_session")
bp = unreal.load_asset("/Game/XRFramework/Blueprints/BP_XRPawn")
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
for h in sds.k2_gather_subobject_data_for_blueprint(bp):
    o = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(unreal.SubobjectDataBlueprintFunctionLibrary.get_data(h))
    if o and o.get_class().get_name() == "ConvaiPlayerComponent":
        r["pawn_autoinit"] = o.get_editor_property("auto_initialize_session"); r["pawn_mute"] = o.get_editor_property("mute")
r["ok"] = bool(r.get("adela_autoinit") and r.get("pawn_autoinit") and r.get("pawn_mute"))
if r["ok"]:
    r["pawn_guardado"] = unreal.EditorAssetLibrary.save_asset("/Game/XRFramework/Blueprints/BP_XRPawn", False)
    r["mapa_guardado"] = unreal.EditorLoadingAndSavingUtils.save_current_level()
    r["pendientes"] = [str(p.get_name()) for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()] + [str(p.get_name()) for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]
open(r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/presalida.json", "w").write(json.dumps(r))
if r["ok"] and SALIR and not r["pendientes"]:
    unreal.SystemLibrary.quit_editor()
