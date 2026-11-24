# 453_creditos_legibles.ps1
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: regenerar creditos_finales.png (2048x1152) con las lineas secundarias mas grandes y claras
#   (Postulante, Tutor, Universidad, Cochabamba) para que se lean en la resolucion del Quest 2.
#   Mismo contenido que 442 (solo cambia tamano/brillo/espaciado). No toca la voz.
Add-Type -AssemblyName System.Drawing
$W = 2048; $H = 1152
$bmp = New-Object System.Drawing.Bitmap($W, $H); $g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = 'AntiAlias'; $g.TextRenderingHint = 'AntiAliasGridFit'
$g.Clear([System.Drawing.Color]::Black)
$gold = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(240, 201, 128))
$cream = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(240, 232, 214))
$soft = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(214, 200, 172))
$ce = New-Object System.Drawing.StringFormat; $ce.Alignment = 'Center'
$pen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(170, 140, 86), 3)
function Draw-Line2($txt, $font, $size, $style, $brush, $y, $h) { $f = New-Object System.Drawing.Font($font, $size, $style); $g.DrawString($txt, $f, $brush, (New-Object System.Drawing.RectangleF(100, $y, ($W - 200), $h)), $ce); $f.Dispose() }
$Bo = [System.Drawing.FontStyle]::Bold; $Re = [System.Drawing.FontStyle]::Regular; $It = [System.Drawing.FontStyle]::Italic
Draw-Line2 "JATUN WASI" "Georgia" 84 $Bo $gold 90 130
Draw-Line2 "Experiencia de turismo cultural en realidad virtual para el patrimonio histórico y las tradiciones orales de Cochabamba, Bolivia" "Georgia" 30 $It $cream 240 130
$g.DrawLine($pen, 724, 410, 1324, 410)
Draw-Line2 "Postulante" "Segoe UI" 28 $Re $soft 445 50
Draw-Line2 "David Alan Fernandez Imaca" "Segoe UI" 44 $Bo $cream 495 70
Draw-Line2 "Tutor" "Segoe UI" 28 $Re $soft 605 50
Draw-Line2 "Ing. Richard Jiménez Velasco" "Segoe UI" 38 $Bo $cream 655 64
$g.DrawLine($pen, 724, 760, 1324, 760)
Draw-Line2 "Universidad Privada Franz Tamayo · Facultad de Ingeniería · Carrera de Ingeniería de Sistemas" "Segoe UI" 28 $Re $cream 790 50
Draw-Line2 "Cochabamba – Bolivia · 2026" "Segoe UI" 28 $Re $soft 850 50
Draw-Line2 "Gracias por tu visita" "Georgia" 52 $It $gold 960 90
$png = "C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/creditos_finales.png"
$bmp.Save($png, [System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $bmp.Dispose()
"creditos: $png"
