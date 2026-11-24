# 467_wav_intro_mas_plaza.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (Python puro, ejecutar con el Python del motor -I) unir la intro de Adela y el relato de la
#   plaza en UN solo audio: A_Adela_IntroPaced (16.1 s) + 1.5 s de silencio + A_Relato_plaza (9.6 s).
#   Motivo: el visitante aparece DENTRO del trigger del relato de la plaza y la intro (prioridad 4) lo
#   descartaba por concurrencia -> el relato de la plaza nunca sonaba.
import wave, sys
SRC = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/NarrWav/"
a = wave.open(SRC + "A_Adela_IntroPaced.wav"); b = wave.open(SRC + "A_Relato_plaza.wav")
assert a.getparams()[:3] == b.getparams()[:3], (a.getparams(), b.getparams())
ch, sw, fr = a.getnchannels(), a.getsampwidth(), a.getframerate()
da = a.readframes(a.getnframes()); db = b.readframes(b.getnframes())
sil = b"\x00" * int(fr * 1.5) * sw * ch
o = wave.open(SRC + "A_Adela_IntroPlaza.wav", "wb"); o.setnchannels(ch); o.setsampwidth(sw); o.setframerate(fr)
o.writeframes(da + sil + db); o.close()
print("ok", round((len(da) + len(sil) + len(db)) / (fr * sw * ch), 2), "s")
