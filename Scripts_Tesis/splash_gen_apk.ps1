# Genera splash horizontal y vertical directo a Build/Android/res/drawable (los que UE mete al APK).
Add-Type -AssemblyName System.Drawing

function Render([int]$W, [int]$H, [string]$out) {
    $bmp = New-Object System.Drawing.Bitmap($W, $H)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = 'AntiAlias'; $g.TextRenderingHint = 'ClearTypeGridFit'; $g.InterpolationMode = 'HighQualityBicubic'
    $min = [Math]::Min($W, $H)

    # Fondo gradiente
    $rect = New-Object System.Drawing.Rectangle(0, 0, $W, $H)
    $c1 = [System.Drawing.Color]::FromArgb(28, 19, 12); $c2 = [System.Drawing.Color]::FromArgb(9, 6, 4)
    $lg = New-Object System.Drawing.Drawing2D.LinearGradientBrush($rect, $c1, $c2, 90)
    $g.FillRectangle($lg, $rect)
    # Resplandor central
    $gp = New-Object System.Drawing.Drawing2D.GraphicsPath
    $gp.AddEllipse(($W/2 - $W*0.42), ($H/2 - $H*0.42), $W*0.84, $H*0.84)
    $pgb = New-Object System.Drawing.Drawing2D.PathGradientBrush($gp)
    $pgb.CenterColor = [System.Drawing.Color]::FromArgb(120, 78, 50, 26)
    $pgb.SurroundColors = @([System.Drawing.Color]::FromArgb(0, 10, 7, 4))
    $g.FillPath($pgb, $gp)

    $gold = [System.Drawing.Color]::FromArgb(232, 195, 122)
    $goldDim = [System.Drawing.Color]::FromArgb(150, 122, 74)
    $cream = [System.Drawing.Color]::FromArgb(242, 228, 200)
    $penOuter = New-Object System.Drawing.Pen($goldDim, ($min*0.0028))
    $penInner = New-Object System.Drawing.Pen($gold, ($min*0.0019))
    $ins1 = [int]($min*0.043); $ins2 = $ins1 + [int]($min*0.013)
    $g.DrawRectangle($penOuter, $ins1, $ins1, ($W-2*$ins1), ($H-2*$ins1))
    $g.DrawRectangle($penInner, $ins2, $ins2, ($W-2*$ins2), ($H-2*$ins2))

    $brGold = New-Object System.Drawing.SolidBrush($gold)
    function Diamond($cx, $cy, $r) {
        $pts = @((New-Object System.Drawing.PointF(($cx),($cy-$r))),(New-Object System.Drawing.PointF(($cx+$r),($cy))),(New-Object System.Drawing.PointF(($cx),($cy+$r))),(New-Object System.Drawing.PointF(($cx-$r),($cy))))
        $g.FillPolygon($brGold, $pts)
    }
    $dr = $min*0.0083
    Diamond $ins2 $ins2 $dr; Diamond ($W-$ins2) $ins2 $dr; Diamond $ins2 ($H-$ins2) $dr; Diamond ($W-$ins2) ($H-$ins2) $dr

    # Sol andino
    $cx = $W/2; $cyS = $H*0.255
    $penSun = New-Object System.Drawing.Pen($gold, ($min*0.0028))
    for ($i=0; $i -lt 16; $i++) {
        $ang = $i * ([Math]::PI*2/16)
        $r1 = $min*0.054; $r2 = if ($i % 2 -eq 0) { $min*0.085 } else { $min*0.072 }
        $g.DrawLine($penSun, ($cx+[Math]::Cos($ang)*$r1), ($cyS+[Math]::Sin($ang)*$r1), ($cx+[Math]::Cos($ang)*$r2), ($cyS+[Math]::Sin($ang)*$r2))
    }
    $g.DrawEllipse($penSun, ($cx-$min*0.044), ($cyS-$min*0.044), ($min*0.088), ($min*0.088))
    $penSun2 = New-Object System.Drawing.Pen($goldDim, ($min*0.0019))
    $g.DrawEllipse($penSun2, ($cx-$min*0.031), ($cyS-$min*0.031), ($min*0.062), ($min*0.062))

    $sf = New-Object System.Drawing.StringFormat; $sf.Alignment='Center'; $sf.LineAlignment='Center'
    $brCream = New-Object System.Drawing.SolidBrush($cream); $brDim = New-Object System.Drawing.SolidBrush($goldDim)

    # Titulo con auto-ajuste al ancho
    $titulo = "Jatun Wasi"
    $fs = $W*0.043; $maxW = $W*0.84
    do {
        $fTitle = New-Object System.Drawing.Font("Georgia", $fs, [System.Drawing.FontStyle]::Bold)
        $sz = $g.MeasureString($titulo, $fTitle)
        if ($sz.Width -le $maxW) { break }
        $fTitle.Dispose(); $fs = $fs - 2
    } while ($fs -gt 10)
    $rTitle = New-Object System.Drawing.RectangleF(0, ($H*0.40), $W, ($H*0.12))
    $g.DrawString($titulo, $fTitle, $brGold, $rTitle, $sf)

    # Divisor
    $yd = $H*0.515
    $g.DrawLine($penInner, ($cx-$W*0.17), $yd, ($cx-$W*0.02), $yd)
    $g.DrawLine($penInner, ($cx+$W*0.02), $yd, ($cx+$W*0.17), $yd)
    Diamond $cx $yd ($min*0.0092)

    $fSub = New-Object System.Drawing.Font("Georgia", ($W*0.0156), [System.Drawing.FontStyle]::Regular)
    $g.DrawString("Patrimonio Vivo  "+[char]0x00B7+"  Cochabamba, Bolivia", $fSub, $brCream, (New-Object System.Drawing.RectangleF(0,($H*0.55),$W,($H*0.06))), $sf)
    $fTag = New-Object System.Drawing.Font("Georgia", ($W*0.012), [System.Drawing.FontStyle]::Italic)
    $g.DrawString("Experiencia de Realidad Virtual", $fTag, $brDim, (New-Object System.Drawing.RectangleF(0,($H*0.61),$W,($H*0.05))), $sf)

    # Credito Unifranz
    $yb = $H*0.83
    $g.DrawLine($penInner, ($cx-$W*0.19), $yb, ($cx+$W*0.19), $yb)
    $fUni = New-Object System.Drawing.Font("Georgia", ($W*0.0177), [System.Drawing.FontStyle]::Bold)
    $g.DrawString("UNIFRANZ", $fUni, $brGold, (New-Object System.Drawing.RectangleF(0,($H*0.85),$W,($H*0.05))), $sf)
    $fUni2 = New-Object System.Drawing.Font("Georgia", ($W*0.0104), [System.Drawing.FontStyle]::Regular)
    $g.DrawString("Universidad Privada Franz Tamayo  "+[char]0x00B7+"  Trabajo de Grado", $fUni2, $brCream, (New-Object System.Drawing.RectangleF(0,($H*0.90),$W,($H*0.04))), $sf)

    $bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose(); $bmp.Dispose()
    "OK -> $out"
}

$base = "C:\UnrealProjects\JatunWasiNawpakay\Build\Android\res\drawable"
Render 1920 1080 "$base\splashscreen_landscape.png"
Render 1080 1920 "$base\splashscreen_portrait.png"
# copia de preview para mostrar
Render 1920 1080 "C:\UnrealProjects\JatunWasiNawpakay\Saved\ClaudeBackups\Splash_final_L.png"