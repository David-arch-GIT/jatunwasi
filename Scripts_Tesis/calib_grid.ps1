Add-Type -AssemblyName System.Drawing
$out = "C:\UnrealProjects\JatunWasiNawpakay\Content\FotosAntano\Encuadradas\ZZ_CALIB.png"
$w = 1994; $h = 1600
$bmp = New-Object System.Drawing.Bitmap($w, $h)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.Clear([System.Drawing.Color]::White)
$cols = 5; $rows = 5
$cw = $w / $cols; $ch = $h / $rows
$letters = @('A','B','C','D','E')
$fnt = New-Object System.Drawing.Font("Arial", 120, [System.Drawing.FontStyle]::Bold)
$blk = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::Black)
$sf = New-Object System.Drawing.StringFormat
$sf.Alignment = [System.Drawing.StringAlignment]::Center
$sf.LineAlignment = [System.Drawing.StringAlignment]::Center
# celdas alternadas + etiqueta col-fila (ej A1 = col A, fila 1)
for ($r=0; $r -lt $rows; $r++) {
  for ($c=0; $c -lt $cols; $c++) {
    $x = $c*$cw; $y = $r*$ch
    if ((($r+$c) % 2) -eq 0) {
      $g.FillRectangle((New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255,215,225,240))), $x, $y, $cw, $ch)
    }
    $lbl = $letters[$c] + ($r+1).ToString()
    $g.DrawString($lbl, $fnt, $blk, [System.Drawing.RectangleF]::new($x, $y, $cw, $ch), $sf)
  }
}
# lineas de cuadricula
$pen = New-Object System.Drawing.Pen([System.Drawing.Color]::Gray, 3)
for ($c=0; $c -le $cols; $c++) { $g.DrawLine($pen, $c*$cw, 0, $c*$cw, $h) }
for ($r=0; $r -le $rows; $r++) { $g.DrawLine($pen, 0, $r*$ch, $w, $r*$ch) }
# marcadores de esquina de color
$m = 45
$g.FillEllipse((New-Object System.Drawing.SolidBrush([System.Drawing.Color]::Red)),    10, 10, $m, $m)         # TL rojo
$g.FillEllipse((New-Object System.Drawing.SolidBrush([System.Drawing.Color]::Green)),  ($w-$m-10), 10, $m, $m) # TR verde
$g.FillEllipse((New-Object System.Drawing.SolidBrush([System.Drawing.Color]::Blue)),   10, ($h-$m-10), $m, $m) # BL azul
$g.FillEllipse((New-Object System.Drawing.SolidBrush([System.Drawing.Color]::Orange)), ($w-$m-10), ($h-$m-10), $m, $m) # BR naranja
# flecha ARRIBA grande en el centro superior
$fnt2 = New-Object System.Drawing.Font("Arial", 90, [System.Drawing.FontStyle]::Bold)
$g.DrawString([char]0x2191 + "TOP", $fnt2, (New-Object System.Drawing.SolidBrush([System.Drawing.Color]::Red)), [System.Drawing.RectangleF]::new(0, 5, $w, 130), $sf)
$g.Dispose()
$bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
"CALIB GRID OK"
