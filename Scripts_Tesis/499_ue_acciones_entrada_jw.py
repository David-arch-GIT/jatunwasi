# 499_ue_acciones_entrada_jw.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: BUG BLOQUEANTE en visor (no deja moverse / boton A / gatillo del pozo): en UE 5.7 con Enhanced
#   Input, OpenXR solo inyecta valores en ACCIONES; el estado de teclas sueltas (GetInputAnalogKeyState,
#   WasInputKeyJustPressed) queda en 0. Se crean acciones propias y se mapean en IMC_Default (que esta en
#   DefaultMappingContexts -> OpenXR las construye):
#     IA_JW_Mover   (Axis2D)  <- OculusTouch_Right_Thumbstick_2D
#     IA_JW_BotonA  (Boolean) <- OculusTouch_Right_A_Click
#     IA_JW_Gatillo (Boolean) <- OculusTouch_Right_Trigger_Click
#   consume_input = False (no le quitan la entrada a otras acciones). Las lee la libreria C++ UJWEntradaVR.
#   Respaldo de IMC_Default. Re-ejecutable (no duplica mapeos).
import unreal, json, traceback, shutil
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/acciones_jw.json"
ROOT = r"C:/UnrealProjects/JatunWasiNawpakay"
res = {"err": None}
try:
    shutil.copy2(ROOT + "/Content/XRFramework/Input/IMC_Default.uasset", ROOT + "/Saved/ClaudeBackups/IMC_Default_pre_jw.uasset")
    at = unreal.AssetToolsHelpers.get_asset_tools(); eal = unreal.EditorAssetLibrary
    D = "/Game/JWN/Input"
    defs = [("IA_JW_Mover", unreal.InputActionValueType.AXIS2D, "OculusTouch_Right_Thumbstick_2D"),
            ("IA_JW_BotonA", unreal.InputActionValueType.BOOLEAN, "OculusTouch_Right_A_Click"),
            ("IA_JW_Gatillo", unreal.InputActionValueType.BOOLEAN, "OculusTouch_Right_Trigger_Click")]
    imc = unreal.load_asset("/Game/XRFramework/Input/IMC_Default")
    existentes = set()
    for m in imc.get_editor_property("default_key_mappings").get_editor_property("mappings"):
        a = m.get_editor_property("action")
        existentes.add((a.get_name() if a else None, str(m.get_editor_property("key").get_editor_property("key_name"))))
    for nombre, tipo, tecla in defs:
        p = D + "/" + nombre
        ia = unreal.load_asset(p) if eal.does_asset_exist(p) else at.create_asset(nombre, D, unreal.InputAction, unreal.InputAction_Factory())
        ia.set_editor_property("value_type", tipo)
        ia.set_editor_property("consume_input", False)
        eal.save_asset(p, False)
        if (nombre, tecla) not in existentes:
            k = unreal.Key(); k.set_editor_property("key_name", tecla)
            imc.map_key(ia, k)
        res[nombre] = [str(ia.get_editor_property("value_type")), tecla]
    res["imc_guardado"] = eal.save_asset("/Game/XRFramework/Input/IMC_Default", False)
    res["verif"] = [[m.get_editor_property("action").get_name(), str(m.get_editor_property("key").get_editor_property("key_name"))]
                    for m in imc.get_editor_property("default_key_mappings").get_editor_property("mappings")
                    if m.get_editor_property("action") and m.get_editor_property("action").get_name().startswith("IA_JW_")]
except Exception:
    res["err"] = traceback.format_exc()[:1500]
open(OUT, "w").write(json.dumps(res, indent=1))
