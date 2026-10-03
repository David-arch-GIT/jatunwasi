Add-Type -AssemblyName System.Drawing
$src = "C:\UnrealProjects\JatunWasiNawpakay\Content\FotosAntano"
$out = "C:\UnrealProjects\JatunWasiNawpakay\Content\FotosAntano\Encuadradas"
New-Item -ItemType Directory -Force -Path $out | Out-Null
# el cuadro tiene UV rotadas 90 -> destino aspecto invertido (alto/ancho fisico)
$Ca = [double]86 / [double]69
$mat = [System.Drawing.Color]::FromArgb(255, 42, 34, 27)
$done = @()
Get-ChildItem -Path $src -Filter *.jpg | ForEach-Object {
  try {
    $img = [System.Drawing.Image]::FromFile($_.FullName)
    # rotar 90 grados para compensar el giro de la UV del cuadro
    $img.RotateFlip([System.Drawing.RotateFlipType]::Rotate90FlipNone)
    $w = $img.Width; $h = $img.Height
    $Ia = [double]$w / [double]$h
    if ($Ia -ge $Ca) {
      $nw = $w
      $nh = [int][math]::Round([double]$w / $Ca)
    } else {
      $nh = $h
      $nw = [int][math]::Round([double]$h * $Ca)
    }
    $bmp = New-Object System.Drawing.Bitmap($nw, $nh)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.Clear($mat)
    $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $px = [int][math]::Round(([double]$nw - $w) * 0.5)
    $py = [int][math]::Round(([double]$nh - $h) * 0.5)
    $g.DrawImage($img, $px, $py, $w, $h)
    $g.Dispose()
    $name = [System.IO.Path]::GetFileNameWithoutExtension($_.Name)
    $safe = ($name -replace '[^\w\- ]', '') -replace '\s+', '_'
    $dest = Join-Path $out ($safe + '.png')
    $bmp.Save($dest, [System.Drawing.Imaging.ImageFormat]::Png)
    $bmp.Dispose(); $img.Dispose()
    $done += ("{0} -> {1}x{2}" -f $name, $nw, $nh)
  } catch { $done += ("ERR " + $_.Name + " " + $_.Exception.Message) }
}
"=== $($done.Count) reprocesadas (rotadas + aspecto 86/69) ==="
$done | ForEach-Object { $_ }
