Add-Type -AssemblyName System.Speech
$dir = "C:\UnrealProjects\JatunWasiNawpakay\Content\Cartelas\Audio"
New-Item -ItemType Directory -Force -Path $dir | Out-Null
$jsonPath = "C:\UnrealProjects\JatunWasiNawpakay\Scripts_Tesis\cartelas.json"
$items = Get-Content $jsonPath -Raw -Encoding UTF8 | ConvertFrom-Json
$sp = New-Object System.Speech.Synthesis.SpeechSynthesizer
try { $sp.SelectVoice("Microsoft Sabina Desktop") } catch { }
$sp.Rate = -1
$sp.Volume = 100
foreach($it in $items){
  $wav = Join-Path $dir ($it.file+".wav")
  $sp.SetOutputToWaveFile($wav)
  # leer titulo + cuerpo
  $texto = $it.title + ". " + $it.body
  $sp.Speak($texto)
  $sp.SetOutputToNull()
  $len = (Get-Item $wav).Length
  "OK $($it.file) -> $([math]::Round($len/1024)) KB"
}
$sp.Dispose()
