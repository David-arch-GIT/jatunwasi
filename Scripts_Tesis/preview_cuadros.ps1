Add-Type -AssemblyName System.Drawing
$src = "C:\UnrealProjects\JatunWasiNawpakay\Content\FotosAntano"
$out = "C:\Users\MIPC~1\AppData\Local\Temp\claude\C--UnrealProjects-JatunWasiNawpakay\a4e359b4-b64f-4e68-b665-65d4641be52a\scratchpad\preview"
New-Item -ItemType Directory -Force -Path $out | Out-Null
# vista en pared: lienzo VERTICAL 69x86 -> aspecto 0.802 (ancho/alto)
$Ca = [double]69 / [double]86
$mat = [System.Drawing.Color]::FromArgb(255, 42, 34, 27)
$target = 1400.0
Get-ChildItem -Path $src -Filter *.jpg | ForEach-Object {
  try {
    $orig = [System.Drawing.Image]::FromFile($_.FullName)
    $ow=$orig.Width; $oh=$orig.Height
    $mx=[math]::Max($ow,$oh); $f=$target/[double]$mx
    if($f -lt 1.0){$f=1.0}; if($f -gt 3.0){$f=3.0}
    $uw=[int][math]::Round([double]$ow*$f); $uh=[int][math]::Round([double]$oh*$f)
    $up=New-Object System.Drawing.Bitmap($uw,$uh)
    $gu=[System.Drawing.Graphics]::FromImage($up)
    $gu.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $gu.DrawImage($orig,0,0,$uw,$uh); $gu.Dispose(); $orig.Dispose()
    $w=$up.Width; $h=$up.Height; $Ia=[double]$w/[double]$h
    if($Ia -ge $Ca){ $nw=$w; $nh=[int][math]::Round([double]$w/$Ca) }
    else { $nh=$h; $nw=[int][math]::Round([double]$h*$Ca) }
    $bmp=New-Object System.Drawing.Bitmap($nw,$nh)
    $g=[System.Drawing.Graphics]::FromImage($bmp); $g.Clear($mat)
    $g.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $px=[int][math]::Round(([double]$nw-$w)*0.5); $py=[int][math]::Round(([double]$nh-$h)*0.5)
    $g.DrawImage($up,$px,$py,$w,$h); $g.Dispose(); $up.Dispose()
    $name=[System.IO.Path]::GetFileNameWithoutExtension($_.Name)
    $safe=($name -replace '[^\w\- ]','') -replace '\s+','_'
    $bmp.Save((Join-Path $out ($safe+'.png')),[System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()
  } catch {}
}
"PREVIEWS OK"
