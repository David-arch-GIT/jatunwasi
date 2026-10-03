# Genera la pantalla de arranque / carga del proyecto (identidad + credito Unifranz).
Add-Type -AssemblyName System.Drawing
$W = 1920; $H = 1080
$bmp = New-Object System.Drawing.Bitmap($W, $H)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = 'AntiAlias'
$g.TextRenderingHint = 'ClearTypeGridFit'
$g.InterpolationMode = 'HighQualityBicubic'

# --- Fondo: gradiente vertical calido oscuro ---
$rect = New-Object System.Drawing.Rectangle(0, 0, $W, $H)
$c1 = [System.Drawing.Color]::FromArgb(28, 19, 12)
$c2 = [System.Drawing.Color]::FromArgb(9, 6, 4)
$lg = New-Object System.Drawing.Drawing2D.LinearGradientBrush($rect, $c1, $c2, 90)
$g.FillRectangle($lg, $rect)

# --- Resplandor calido central ---
$gp = New-Object System.Drawing.Drawing2D.GraphicsPath
$gp.AddEllipse(($W/2 - 780), ($H/2 - 560), 1560, 1120)
$pgb = New-Object System.Drawing.Drawing2D.PathGradientBrush($gp)
$pgb.CenterColor = [System.Drawing.Color]::FromArgb(120, 78, 50, 26)
$pgb.SurroundColors = @([System.Drawing.Color]::FromArgb(0, 10, 7, 4))
$g.FillPath($pgb, $gp)

# --- Colores dorados ---
$gold = [System.Drawing.Color]::FromArgb(232, 195, 122)
$goldDim = [System.Drawing.Color]::FromArgb(150, 122, 74)
$cream = [System.Drawing.Color]::FromArgb(242, 228, 200)

# --- Marco doble dorado ---
$penOuter = New-Object System.Drawing.Pen($goldDim, 3)
$penInner = New-Object System.Drawing.Pen($gold, 2)
$g.DrawRectangle($penOuter, 46, 46, ($W-92), ($H-92))
$g.DrawRectangle($penInner, 60, 60, ($W-120), ($H-120))

# --- Rombos en las esquinas ---
function Draw-Diamond($cx, $cy, $r) {
    $pts = @(
        (New-Object System.Drawing.PointF(($cx), ($cy-$r))),
        (New-Object System.Drawing.PointF(($cx+$r), ($cy))),
        (New-Object System.Drawing.PointF(($cx), ($cy+$r))),
        (New-Object System.Drawing.PointF(($cx-$r), ($cy)))
    )
    $b = New-Object System.Drawing.SolidBrush($gold)
    $g.FillPolygon($b, $pts)
    $b.Dispose()
}
Draw-Diamond 60 60 9; Draw-Diamond ($W-60) 60 9; Draw-Diamond 60 ($H-60) 9; Draw-Diamond ($W-60) ($H-60) 9

# --- Emblema: sol andino (Inti) estilizado, arriba del titulo ---
$cx = $W/2; $cy = 300
$penSun = New-Object System.Drawing.Pen($gold, 3)
# rayos
for ($i=0; $i -lt 16; $i++) {
    $ang = $i * ([Math]::PI*2/16)
    $r1 = 58; $r2 = if ($i % 2 -eq 0) { 92 } else { 78 }
    $x1 = $cx + [Math]::Cos($ang)*$r1; $y1 = $cy + [Math]::Sin($ang)*$r1
    $x2 = $cx + [Math]::Cos($ang)*$r2; $y2 = $cy + [Math]::Sin($ang)*$r2
    $g.DrawLine($penSun, $x1, $y1, $x2, $y2)
}
$g.DrawEllipse($penSun, ($cx-48), ($cy-48), 96, 96)
$penSun2 = New-Object System.Drawing.Pen($goldDim, 2)
$g.DrawEllipse($penSun2, ($cx-34), ($cy-34), 68, 68)

# --- Titulo ---
$titulo = "JatunWasi " + [char]0x00D1 + "awpaqay"
$fTitle = New-Object System.Drawing.Font("Georgia", 82, [System.Drawing.FontStyle]::Bold)
$sf = New-Object System.Drawing.StringFormat
$sf.Alignment = 'Center'; $sf.LineAlignment = 'Center'
$brGold = New-Object System.Drawing.SolidBrush($gold)
$rTitle = New-Object System.Drawing.RectangleF(0, 430, $W, 150)
$g.DrawString($titulo, $fTitle, $brGold, $rTitle, $sf)

# --- Divisor con rombo ---
$yd = 560
$g.DrawLine($penInner, ($cx-320), $yd, ($cx-40), $yd)
$g.DrawLine($penInner, ($cx+40), $yd, ($cx+320), $yd)
Draw-Diamond $cx $yd 10

# --- Subtitulo ---
$fSub = New-Object System.Drawing.Font("Georgia", 30, [System.Drawing.FontStyle]::Regular)
$brCream = New-Object System.Drawing.SolidBrush($cream)
$rSub = New-Object System.Drawing.RectangleF(0, 590, $W, 60)
$g.DrawString("Patrimonio Vivo  " + [char]0x00B7 + "  Cochabamba, Bolivia", $fSub, $brCream, $rSub, $sf)

# --- Tagline ---
$fTag = New-Object System.Drawing.Font("Georgia", 23, [System.Drawing.FontStyle]::Italic)
$brDim = New-Object System.Drawing.SolidBrush($goldDim)
$rTag = New-Object System.Drawing.RectangleF(0, 655, $W, 50)
$g.DrawString("Experiencia de Realidad Virtual", $fTag, $brDim, $rTag, $sf)

# --- Banda inferior: credito Unifranz ---
$yb = 900
$g.DrawLine($penInner, ($cx-360), $yb, ($cx+360), $yb)
$fUni = New-Object System.Drawing.Font("Georgia", 34, [System.Drawing.FontStyle]::Bold)
$rUni = New-Object System.Drawing.RectangleF(0, 918, $W, 55)
$g.DrawString("UNIFRANZ", $fUni, $brGold, $rUni, $sf)
$fUni2 = New-Object System.Drawing.Font("Georgia", 20, [System.Drawing.FontStyle]::Regular)
$rUni2 = New-Object System.Drawing.RectangleF(0, 972, $W, 40)
$g.DrawString("Universidad Privada Franz Tamayo  " + [char]0x00B7 + "  Trabajo de Grado", $fUni2, $brCream, $rUni2, $sf)

# --- Guardar ---
$out = "C:\UnrealProjects\JatunWasiNawpakay\Saved\ClaudeBackups\Splash_JatunWasi.png"
$dir = Split-Path $out
if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force $dir | Out-Null }
$bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
"OK -> $out"