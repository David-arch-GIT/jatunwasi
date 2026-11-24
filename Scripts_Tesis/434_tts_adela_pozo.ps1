# 434_tts_adela_pozo.ps1
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2) - Fecha: 2026-11-24
# Proposito: voz de Adela para el POZO DE LOS DESEOS del convento, con la MISMA voz y ajustes que todas
#   las narraciones (Microsoft Sabina Desktop, Rate -1, Volume 100). Salida Saved/NarrWav.
#   Texto prudente (regla cero invencion): tradicion general de los pozos de deseos + uso real del pozo.
Add-Type -AssemblyName System.Speech
$out = "C:/UnrealProjects/JatunWasiNawpakay/Saved/NarrWav"
New-Item -ItemType Directory -Force -Path $out | Out-Null
function Say($name, $text) {
  $sp = New-Object System.Speech.Synthesis.SpeechSynthesizer
  $sp.SelectVoice("Microsoft Sabina Desktop"); $sp.Rate = -1; $sp.Volume = 100
  $sp.SetOutputToWaveFile("$out/$name.wav"); $sp.Speak($text); $sp.Dispose()
}
Say "A_Adela_Pozo" ("Escuchaste caer la moneda al pozo. En muchos pueblos se dice que quien arroja una moneda y pide un deseo en silencio, algun dia regresa. " + `
    "En el convento, este pozo daba el agua para la cocina, el huerto y la limpieza de los frailes.")
Get-ChildItem $out -Filter "A_Adela_Pozo.wav" | % { $_.Name + " " + [math]::Round($_.Length/1KB) + " KB" }
