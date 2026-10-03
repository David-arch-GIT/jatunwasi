Add-Type -AssemblyName System.Drawing
$src = "C:\UnrealProjects\JatunWasiNawpakay\Content\FotosAntano"
$out = "C:\UnrealProjects\JatunWasiNawpakay\Content\FotosAntano\Encuadradas"
New-Item -ItemType Directory -Force -Path $out | Out-Null
$Ca = [double]86 / [double]69   # aspecto invertido (UV del cuadro giradas 90)
$mat = [System.Drawing.Color]::FromArgb(255, 42, 34, 27)
$target = 1600.0   # lado mayor objetivo tras reescalar
$done = @()
Get-ChildItem -Path $src -Filter *.jpg | ForEach-Object {
  try {
    $orig = [System.Drawing.Image]::FromFile($_.FullName)
    $ow = $orig.Width; $oh = $orig.Height
    # factor de reescalado (solo agrandar, max 3x para no reventar de borroso)
    $mx = [math]::Max($ow, $oh)
    $factor = $target / [double]$mx
    if ($factor -lt 1.0) { $factor = 1.0 }
    if ($factor -gt 3.0) { $factor = 3.0 }
    $uw = [int][math]::Round([double]$ow * $factor)
    $uh = [int][math]::Round([double]$oh * $factor)
    # reescalar con alta calidad
    $up = New-Object System.Drawing.Bitmap($uw, $uh)
    $gu = [System.Drawing.Graphics]::FromImage($up)
    $gu.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $gu.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
    $gu.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
    $gu.DrawImage($orig, 0, 0, $uw, $uh)
    $gu.Dispose(); $orig.Dispose()
    # rotar 90 para compensar UV del cuadro
    $up.RotateFlip([System.Drawing.RotateFlipType]::Rotate90FlipNone)
    $w = $up.Width; $h = $up.Height
    $Ia = [double]$w / [double]$h
    if ($Ia -ge $Ca) { $nw = $w; $nh = [int][math]::Round([double]$w / $Ca) }
    else { $nh = $h; $nw = [int][math]::Round([double]$h * $Ca) }
    $bmp = New-Object System.Drawing.Bitmap($nw, $nh)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.Clear($mat)
    $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $px = [int][math]::Round(([double]$nw - $w) * 0.5)
    $py = [int][math]::Round(([double]$nh - $h) * 0.5)
    $g.DrawImage($up, $px, $py, $w, $h)
    $g.Dispose(); $up.Dispose()
    $name = [System.IO.Path]::GetFileNameWithoutExtension($_.Name)
    $safe = ($name -replace '[^\w\- ]', '') -replace '\s+', '_'
    $bmp.Save((Join-Path $out ($safe + '.png')), [System.Drawing.Imaging.ImageFormat]::Png)
    $bmp.Dispose()
    $done += ("{0}: {1}x{2} -> tex {3}x{4} (x{5})" -f $name, $ow, $oh, $nw, $nh, [math]::Round($factor,2))
  } catch { $done += ("ERR " + $_.Name + " " + $_.Exception.Message) }
}
"=== $($done.Count) ==="; $done | ForEach-Object { $_ }
