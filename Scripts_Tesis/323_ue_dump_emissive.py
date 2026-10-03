# Extrae el color emissive de M_JW_LampEmissive (Material) y M_Emis_FarolCalido (MIC).
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/dump_emissive.json"
res={}
EAL=unreal.EditorAssetLibrary

# --- M_JW_LampEmissive : Material base, leer Constant3Vector / Constant / Multiply ---
m=EAL.load_asset("/Game/JWN/Architecture/Hacienda_Kit_V1/M_JW_LampEmissive")
lamp={"consts3":[], "consts":[], "mult":[]}
try:
    exprs=m.get_expressions()
    for e in exprs:
        cn=e.get_class().get_name()
        try:
            if cn=="MaterialExpressionConstant3Vector":
                c=e.get_editor_property("constant")
                lamp["consts3"].append([round(c.r,3),round(c.g,3),round(c.b,3)])
            elif cn=="MaterialExpressionConstant":
                lamp["consts"].append(round(e.get_editor_property("r"),3))
            elif cn=="MaterialExpressionConstant4Vector":
                c=e.get_editor_property("constant")
                lamp["consts3"].append([round(c.r,3),round(c.g,3),round(c.b,3),round(c.a,3)])
            elif cn=="MaterialExpressionMultiply":
                lamp["mult"].append({"A":e.get_editor_property("const_a"),"B":e.get_editor_property("const_b")})
        except Exception as ex:
            lamp.setdefault("dbg",[]).append(cn+":"+str(ex)[:30])
except Exception as e:
    lamp["err"]=str(e)[:80]
res["LampEmissive_hacienda"]=lamp

# --- M_Emis_FarolCalido : MIC, leer vector/scalar param values ---
mi=EAL.load_asset("/Game/JWN/Lighting/M_Emis_FarolCalido")
farol={"vectors":[], "scalars":[]}
try:
    for vp in mi.get_editor_property("vector_parameter_values"):
        info=vp.get_editor_property("parameter_info")
        c=vp.get_editor_property("parameter_value")
        farol["vectors"].append({"name":str(info.get_editor_property("name")),"rgb":[round(c.r,3),round(c.g,3),round(c.b,3)]})
    for sp in mi.get_editor_property("scalar_parameter_values"):
        info=sp.get_editor_property("parameter_info")
        farol["scalars"].append({"name":str(info.get_editor_property("name")),"val":round(sp.get_editor_property("parameter_value"),3)})
    par=mi.get_base_material()
    farol["parent"]=par.get_name() if par else "None"
except Exception as e:
    farol["err"]=str(e)[:80]
res["FarolCalido_bueno"]=farol
open(OUT,"w").write(json.dumps(res,indent=1))
