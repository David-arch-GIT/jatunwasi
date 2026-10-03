# Genera el ICONO de la app (fachada colonial dorada) distinto del splash. Multi-densidad para Quest.
Add-Type -AssemblyName System.Drawing

function RenderIcon([int]$S) {
    $bmp = New-Object System.Drawing.Bitmap($S, $S)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = 'AntiAlias'; $g.InterpolationMode = 'HighQualityBicubic'
    $u = $S / 512.0  # factor de escala respecto al diseno base 512

    # Fondo degradado calido
    $rect = New-Object System.Drawing.Rectangle(0, 0, $S, $S)
    $c1 = [System.Drawing.Color]::FromArgb(38, 26, 16); $c2 = [System.Drawing.Color]::FromArgb(14, 9, 5)
    $lg = New-Object System.Drawing.Drawing2D.LinearGradientBrush($rect, $c1, $c2, 90)
    $g.FillRectangle($lg, $rect)
    # Resplandor central
    $gp = New-Object System.Drawing.Drawing2D.GraphicsPath
    $gp.AddEllipse(($S*0.08), ($S*0.02), ($S*0.84), ($S*0.84))
    $pgb = New-Object System.Drawing.Drawing2D.PathGradientBrush($gp)
    $pgb.CenterColor = [System.Drawing.Color]::FromArgb(120, 92, 58, 28)
    $pgb.SurroundColors = @([System.Drawing.Color]::FromArgb(0, 14, 9, 5))
    $g.FillPath($pgb, $gp)

    $gold = [System.Drawing.Color]::FromArgb(235, 198, 124)
    $goldDim = [System.Drawing.Color]::FromArgb(150, 122, 74)
    $pen  = New-Object System.Drawing.Pen($gold, (7*$u)); $pen.LineJoin='Round'; $pen.StartCap='Round'; $pen.EndCap='Round'
    $penT = New-Object System.Drawing.Pen($gold, (5*$u)); $penT.LineJoin='Round'
    $brGold = New-Object System.Drawing.SolidBrush($gold)
    function P($x,$y){ New-Object System.Drawing.PointF(($x*$u),($y*$u)) }

    # Marco redondeado sutil
    $penFrame = New-Object System.Drawing.Pen($goldDim, (5*$u))
    $inset = 34*$u; $rc = 60*$u
    $path = New-Object System.Drawing.Drawing2D.GraphicsPath
    $d = 2*$rc
    $path.AddArc($inset, $inset, $d, $d, 180, 90)
    $path.AddArc(($S-$inset-$d), $inset, $d, $d, 270, 90)
    $path.AddArc(($S-$inset-$d), ($S-$inset-$d), $d, $d, 0, 90)
    $path.AddArc($inset, ($S-$inset-$d), $d, $d, 90, 90)
    $path.CloseFigure()
    $g.DrawPath($penFrame, $path)

    # --- Fachada colonial (Casa Grande) ---
    # Cruz en el apice
    $g.DrawLine($penT, (P 256 96), (P 256 130))
    $g.DrawLine($penT, (P 242 110), (P 270 110))
    # Fronton (triangulo)
    $g.DrawLines($pen, @((P 168 205), (P 256 132), (P 344 205)))
    # Cornisa
    $g.DrawLine($pen, (P 150 205), (P 362 205))
    $g.DrawLine($penT, (P 156 222), (P 356 222))
    # Roseton en el fronton
    $g.DrawEllipse($penT, (240*$u), (160*$u), (32*$u), (32*$u))
    # Pilastras
    $g.DrawLine($pen, (P 176 222), (P 176 388))
    $g.DrawLine($pen, (P 336 222), (P 336 388))
    # Portada con arco
    $g.DrawLine($pen, (P 214 388), (P 214 312))
    $g.DrawLine($pen, (P 298 388), (P 298 312))
    $g.DrawArc($pen, (214*$u), (270*$u), (84*$u), (84*$u), 180, 180)
    # Base / escalinata
    $g.DrawLine($pen, (P 150 388), (P 362 388))
    $g.DrawLine($penT, (P 138 402), (P 374 402))

    $g.Dispose()
    return $bmp
}

$master = RenderIcon 512
$base = "C:\UnrealProjects\JatunWasiNawpakay\Build\Android\res"
# densidades Android (Quest = alta densidad, agrego xxhdpi/xxxhdpi para nitidez)
$targets = @{
  "drawable\icon.png" = 96
  "drawable-ldpi\icon.png" = 36
  "drawable-mdpi\icon.png" = 48
  "drawable-hdpi\icon.png" = 72
  "drawable-xhdpi\icon.png" = 96
  "drawable-xxhdpi\icon.png" = 144
  "drawable-xxxhdpi\icon.png" = 192
}
foreach ($k in $targets.Keys) {
  $sz = $targets[$k]
  $dir = Join-Path $base (Split-Path $k)
  if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force $dir | Out-Null }
  $out = Join-Path $base $k
  $r = New-Object System.Drawing.Bitmap($sz, $sz)
  $gg = [System.Drawing.Graphics]::FromImage($r); $gg.InterpolationMode='HighQualityBicubic'
  $gg.DrawImage($master, 0, 0, $sz, $sz)
  $r.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
  $gg.Dispose(); $r.Dispose()
  "OK $k => ${sz}x${sz}"
}
# master preview
$master.Save("C:\UnrealProjects\JatunWasiNawpakay\Saved\ClaudeBackups\AppIcon_master.png", [System.Drawing.Imaging.ImageFormat]::Png)
$master.Dispose()
"MASTER 512 guardado"