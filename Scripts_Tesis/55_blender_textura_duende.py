# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-27
# Que hace este script: (BLENDER headless) Crea una textura solida de color verde-tierra para el duende (para usarla como ApparitionTex en el material de aparicion).
# Por que se necesito: El duende no tenia textura; el material de aparicion necesita una textura para mostrar color.
# Resultado obtenido: (pendiente) T_Duende_Green.png en processed/.
# ------------------------------------------------------------
import bpy
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/processed/T_Duende_Green.png"
N = 16
img = bpy.data.images.new("T_Duende_Green", N, N, alpha=True)
col = (0.20, 0.27, 0.18, 1.0)
img.pixels = list(col) * (N * N)
img.filepath_raw = OUT
img.file_format = 'PNG'
img.save()
print("GREEN TEX OK")
