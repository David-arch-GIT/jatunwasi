Add-Type -AssemblyName System.Drawing
$src = "C:\UnrealProjects\JatunWasiNawpakay\Content\FotosAntano"
$out = "C:\UnrealProjects\JatunWasiNawpakay\Content\FotosAntano\Encuadradas"
New-Item -ItemType Directory -Force -Path $out | Out-Null
$Ca = [double]69 / [double]86   # aspecto del cuadro (ancho/alto) vertical
$mat = [System.Drawing.Color]::FromArgb(255, 42, 34, 27)
$done = @()
Get-ChildItem -Path $src -Filter *.jpg | ForEach-Object {
  try {
    $img = [System.Drawing.Image]::FromFile($_.FullName)
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
    $orient = if ($Ia -ge $Ca) { 'H' } else { 'V' }
    $done += ("{0} ({1}x{2} {3}) -> {4}x{5}  {6}" -f $name, $w, $h, $orient, $nw, $nh, ($safe + '.png'))
  } catch {
    $done += ("ERR " + $_.Name + " " + $_.Exception.Message)
  }
}
"=== $($done.Count) encuadradas ==="
$done | ForEach-Object { $_ }
