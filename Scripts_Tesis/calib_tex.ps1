Add-Type -AssemblyName System.Drawing
$out = "C:\UnrealProjects\JatunWasiNawpakay\Content\FotosAntano\Encuadradas\ZZ_CALIB.png"
$w = 1994; $h = 1600
$bmp = New-Object System.Drawing.Bitmap($w, $h)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.Clear([System.Drawing.Color]::FromArgb(255,230,230,230))
# bordes de colores: ARRIBA=rojo, ABAJO=azul, IZQ=verde, DER=amarillo
$bw = 70
$g.FillRectangle((New-Object System.Drawing.SolidBrush([System.Drawing.Color]::Red)), 0, 0, $w, $bw)
$g.FillRectangle((New-Object System.Drawing.SolidBrush([System.Drawing.Color]::Blue)), 0, ($h-$bw), $w, $bw)
$g.FillRectangle((New-Object System.Drawing.SolidBrush([System.Drawing.Color]::Green)), 0, 0, $bw, $h)
$g.FillRectangle((New-Object System.Drawing.SolidBrush([System.Drawing.Color]::Yellow)), ($w-$bw), 0, $bw, $h)
# diagonales de esquina a esquina
$pen = New-Object System.Drawing.Pen([System.Drawing.Color]::Black, 6)
$g.DrawLine($pen, 0, 0, $w, $h); $g.DrawLine($pen, $w, 0, 0, $h)
# texto ARRIBA / ABAJO / IZQ / DER
$fnt = New-Object System.Drawing.Font("Arial", 130, [System.Drawing.FontStyle]::Bold)
$fntS = New-Object System.Drawing.Font("Arial", 90, [System.Drawing.FontStyle]::Bold)
$blk = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::Black)
$sf = New-Object System.Drawing.StringFormat
$sf.Alignment = [System.Drawing.StringAlignment]::Center
$sf.LineAlignment = [System.Drawing.StringAlignment]::Center
$g.DrawString("ARRIBA", $fnt, $blk, [System.Drawing.RectangleF]::new(0, 120, $w, 200), $sf)
$g.DrawString("ABAJO", $fnt, $blk, [System.Drawing.RectangleF]::new(0, ($h-320), $w, 200), $sf)
$g.DrawString("CENTRO", $fnt, (New-Object System.Drawing.SolidBrush([System.Drawing.Color]::Magenta)), [System.Drawing.RectangleF]::new(0, ($h/2-100), $w, 200), $sf)
$g.DrawString("IZQ", $fntS, $blk, [System.Drawing.RectangleF]::new(90, ($h/2-60), 300, 150), $sf)
$g.DrawString("DER", $fntS, $blk, [System.Drawing.RectangleF]::new(($w-390), ($h/2-60), 300, 150), $sf)
$g.Dispose()
$bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
"CALIB OK $out"
