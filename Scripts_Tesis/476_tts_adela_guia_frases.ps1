# 476_tts_adela_guia_frases.ps1
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2) - Fecha: 2026-11-24
# Proposito: frases CORTAS de Adela como guia que acompana (misma voz que todas las narraciones:
#   Microsoft Sabina Desktop, Rate -1, Volume 100). Salida Saved/NarrWav. Se importan con 477.
Add-Type -AssemblyName System.Speech
$out = "C:/UnrealProjects/JatunWasiNawpakay/Saved/NarrWav"
New-Item -ItemType Directory -Force -Path $out | Out-Null
function Save-Voz($name, $text) {
  $sp = New-Object System.Speech.Synthesis.SpeechSynthesizer
  $sp.SelectVoice("Microsoft Sabina Desktop"); $sp.Rate = -1; $sp.Volume = 100
  $sp.SetOutputToWaveFile("$out/$name.wav"); $sp.Speak($text); $sp.Dispose()
}
Save-Voz "A_Guia_Sigueme_Templo"   "Sígueme. Primero vamos al templo."
Save-Voz "A_Guia_Sigueme_Convento" "Ahora vamos al convento. Sígueme."
Save-Voz "A_Guia_Sigueme_Hacienda" "Nuestra última parada es la hacienda. Sígueme."
Save-Voz "A_Guia_NoTeQuedes"       "No te quedes atrás. Aquí te espero."
Save-Voz "A_Guia_Preguntas"        "¿Tienes alguna pregunta? Mantén apretado el botón lateral derecho y háblame. Recorre con calma, aquí te espero."
Save-Voz "A_Guia_Preguntas_Hacienda" "¿Tienes alguna pregunta? Mantén apretado el botón lateral derecho y háblame. Recorre la hacienda con calma; te espero en el salón de baile, en el segundo piso."
Get-ChildItem $out -Filter "A_Guia_*.wav" | % { $_.Name + " " + [math]::Round($_.Length/1KB) + " KB" }
