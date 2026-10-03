# Guia VISUAL: control real + iconos grandes + 1 palabra. Minimo texto, para no leer.
Add-Type -AssemblyName System.Drawing
$W=1700; $H=1000
$bmp=New-Object System.Drawing.Bitmap($W,$H); $g=[System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode='AntiAlias'; $g.TextRenderingHint='ClearTypeGridFit'; $g.InterpolationMode='HighQualityBicubic'
$rf=New-Object System.Drawing.Rectangle(0,0,$W,$H)
$g.FillRectangle((New-Object System.Drawing.Drawing2D.LinearGradientBrush($rf,[System.Drawing.Color]::FromArgb(30,21,13),[System.Drawing.Color]::FromArgb(9,6,4),90)),$rf)
$gold=[System.Drawing.Color]::FromArgb(235,197,124); $goldDim=[System.Drawing.Color]::FromArgb(150,122,74); $cream=[System.Drawing.Color]::FromArgb(244,231,205)
$Bf=[System.Drawing.FontStyle]::Bold; $If=[System.Drawing.FontStyle]::Italic
$brGold=New-Object System.Drawing.SolidBrush($gold); $brCream=New-Object System.Drawing.SolidBrush($cream)
$penG=New-Object System.Drawing.Pen($gold,5); $penG.StartCap='Round'; $penG.EndCap='Round'; $penG.LineJoin='Round'
$penLine=New-Object System.Drawing.Pen($goldDim,2.5)
$ce=New-Object System.Drawing.StringFormat; $ce.Alignment='Center'; $le=New-Object System.Drawing.StringFormat; $le.Alignment='Near'
function RRect($x,$y,$w,$h,$r){ $p=New-Object System.Drawing.Drawing2D.GraphicsPath; $d=2*$r
  $p.AddArc($x,$y,$d,$d,180,90);$p.AddArc(($x+$w-$d),$y,$d,$d,270,90);$p.AddArc(($x+$w-$d),($y+$h-$d),$d,$d,0,90);$p.AddArc($x,($y+$h-$d),$d,$d,90,90);$p.CloseFigure();return $p }
$g.DrawRectangle($penLine,35,35,($W-70),($H-70))
$g.DrawString("CONTROLES",(New-Object System.Drawing.Font("Georgia",40,$Bf)),$brGold,(New-Object System.Drawing.RectangleF(0,48,$W,56)),$ce)

# --- control real ---
$card=RRect 80 165 620 770 24
$g.FillPath((New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(245,244,242))),$card)
$g.DrawPath((New-Object System.Drawing.Pen($gold,3)),$card)
$ctrl=[System.Drawing.Image]::FromFile("C:\UnrealProjects\JatunWasiNawpakay\Saved\ClaudeBackups\control_real.png")
$g.DrawImage($ctrl,105,320,570,490); $ctrl.Dispose()
$g.DrawString("Tus mandos Meta Quest",(New-Object System.Drawing.Font("Segoe UI",17,$Bf)),(New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(60,50,40))),(New-Object System.Drawing.RectangleF(80,865,620,28)),$ce)

# --- iconos ---
function Arrow($x1,$y1,$x2,$y2){
  $g.DrawLine($penG,$x1,$y1,$x2,$y2)
  $a=[math]::Atan2(($y2-$y1),($x2-$x1)); $l=16
  $g.DrawLine($penG,$x2,$y2,($x2-$l*[math]::Cos($a-0.5)),($y2-$l*[math]::Sin($a-0.5)))
  $g.DrawLine($penG,$x2,$y2,($x2-$l*[math]::Cos($a+0.5)),($y2-$l*[math]::Sin($a+0.5)))
}
function IcoMove($cx,$cy){ Arrow $cx ($cy+6) $cx ($cy-26); Arrow $cx ($cy-6) $cx ($cy+26); Arrow ($cx+6) $cy ($cx+26) $cy; Arrow ($cx-6) $cy ($cx-26) $cy }
function IcoTurn($cx,$cy){ $g.DrawArc($penG,($cx-24),($cy-24),48,48,120,260); Arrow ($cx+18) ($cy-16) ($cx+24) ($cy+6) }
function IcoMenu($cx,$cy){ for($i=-1;$i -le 1;$i++){ $g.DrawLine($penG,($cx-24),($cy+$i*12),($cx+24),($cy+$i*12)) } }
function IcoEye($cx,$cy){ $g.DrawArc($penG,($cx-26),($cy-16),52,32,0,360); $g.FillEllipse($brGold,($cx-9),($cy-9),18,18) }
function IcoTarget($cx,$cy){ $g.DrawEllipse($penG,($cx-24),($cy-24),48,48); $g.DrawEllipse($penG,($cx-12),($cy-12),24,24); $g.FillEllipse($brGold,($cx-4),($cy-4),8,8) }

$fW=New-Object System.Drawing.Font("Segoe UI",30,$Bf)
$fS=New-Object System.Drawing.Font("Segoe UI",19,([System.Drawing.FontStyle]::Regular))
$ix=830; $tx=930
function Row($y,$icon,$word,$sub){
  $g.FillEllipse((New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(48,38,24))),($ix-52),($y-52),104,104)
  $g.DrawEllipse((New-Object System.Drawing.Pen($goldDim,3)),($ix-52),($y-52),104,104)
  & $icon $ix $y
  $g.DrawString($word,$fW,$brGold,(New-Object System.Drawing.RectangleF($tx,($y-40),720,44)),$le)
  $g.DrawString($sub,$fS,$brCream,(New-Object System.Drawing.RectangleF($tx,($y+6),720,32)),$le)
}
Row 210 (Get-Item function:IcoMove).ScriptBlock "MOVERTE" "Palanca derecha"
Row 355 (Get-Item function:IcoTurn).ScriptBlock "GIRAR" "Palanca izquierda"
Row 500 (Get-Item function:IcoMenu).ScriptBlock ("MEN"+[char]0x00DA) ("Bot"+[char]0x00F3+"n B derecho (otra vez cierra)")
Row 645 (Get-Item function:IcoEye).ScriptBlock "VER TEXTO + VOZ" "Gatillo derecho (apunta a una cartela)"
Row 790 (Get-Item function:IcoTarget).ScriptBlock "TELETRANSPORTE" "Apunta con el rayo y selecciona"

$out="C:\UnrealProjects\JatunWasiNawpakay\Saved\ClaudeBackups\guia_controles.png"
$bmp.Save($out,[System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose();$bmp.Dispose(); "OK -> $out"