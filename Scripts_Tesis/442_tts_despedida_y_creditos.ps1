# 442_tts_despedida_y_creditos.ps1
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2) - Fecha: 2026-11-24
# Proposito: FINAL del recorrido.
#   1) Voz de despedida de Adela (misma voz/ajustes que todas: Microsoft Sabina Desktop, Rate -1, Vol 100)
#      Texto corto y fiel al proyecto (sin inventar datos).
#   2) Imagen de creditos (fondo negro, letras doradas/crema) con los datos OFICIALES de la portada de la
#      tesis: titulo, postulante, tutor, UNIFRANZ, carrera, ciudad y anio.
Add-Type -AssemblyName System.Speech
Add-Type -AssemblyName System.Drawing
$out = "C:/UnrealProjects/JatunWasiNawpakay/Saved/NarrWav"
New-Item -ItemType Directory -Force -Path $out | Out-Null
$sp = New-Object System.Speech.Synthesis.SpeechSynthesizer
$sp.SelectVoice("Microsoft Sabina Desktop"); $sp.Rate = -1; $sp.Volume = 100
$sp.SetOutputToWaveFile("$out/A_Adela_Despedida.wav")
$sp.Speak("Hemos llegado al final del recorrido. Conociste la plaza, el templo, el convento y esta hacienda, lugares que guardan la historia y las tradiciones orales de Cochabamba. Si quieres preguntarme algo, mantén apretado el botón lateral derecho y háblame. Gracias por acompañarme.")
$sp.Dispose()
"voz: " + [math]::Round((Get-Item "$out/A_Adela_Despedida.wav").Length / 1KB) + " KB"

$W = 2048; $H = 1152
$bmp = New-Object System.Drawing.Bitmap($W, $H); $g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = 'AntiAlias'; $g.TextRenderingHint = 'AntiAliasGridFit'
$g.Clear([System.Drawing.Color]::Black)
$gold = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(240, 201, 128))
$cream = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(235, 225, 205))
$dim = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(170, 160, 140))
$ce = New-Object System.Drawing.StringFormat; $ce.Alignment = 'Center'
$pen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(150, 122, 74), 2)
function T($txt, $font, $size, $style, $brush, $y, $h) { $f = New-Object System.Drawing.Font($font, $size, $style); $g.DrawString($txt, $f, $brush, (New-Object System.Drawing.RectangleF(160, $y, ($W - 320), $h)), $ce) }
$B = [System.Drawing.FontStyle]::Bold; $R = [System.Drawing.FontStyle]::Regular; $I = [System.Drawing.FontStyle]::Italic
T "JATUN WASI" "Georgia" 78 $B $gold 150 120
T "Experiencia de turismo cultural en realidad virtual para el patrimonio histórico y las tradiciones orales de Cochabamba, Bolivia" "Georgia" 28 $I $cream 290 120
$g.DrawLine($pen, 724, 450, 1324, 450)
T "Postulante" "Segoe UI" 22 $R $dim 500 40
T "David Alan Fernandez Imaca" "Segoe UI" 38 $B $cream 540 60
T "Tutor" "Segoe UI" 22 $R $dim 640 40
T "Ing. Richard Jiménez Velasco" "Segoe UI" 32 $B $cream 680 56
$g.DrawLine($pen, 724, 770, 1324, 770)
T "Universidad Privada Franz Tamayo · Facultad de Ingeniería · Carrera de Ingeniería de Sistemas" "Segoe UI" 22 $R $cream 800 40
T "Cochabamba – Bolivia · 2026" "Segoe UI" 22 $R $dim 845 40
T "Gracias por tu visita" "Georgia" 44 $I $gold 950 80
$png = "C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/creditos_finales.png"
$bmp.Save($png, [System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $bmp.Dispose()
"creditos: $png"
