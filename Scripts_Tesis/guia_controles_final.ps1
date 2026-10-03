# Guia de controles FINAL sobre la FOTO REAL de frente (control_frente.png).
# Flechas exactas a: palanca, boton B, y gatillos de atras. Mapeo del proyecto.
Add-Type -AssemblyName System.Drawing
$W=1700; $H=1020
$bmp=New-Object System.Drawing.Bitmap($W,$H); $g=[System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode='AntiAlias'; $g.TextRenderingHint='ClearTypeGridFit'; $g.InterpolationMode='HighQualityBicubic'
$rf=New-Object System.Drawing.Rectangle(0,0,$W,$H)
$g.FillRectangle((New-Object System.Drawing.Drawing2D.LinearGradientBrush($rf,[System.Drawing.Color]::FromArgb(30,21,13),[System.Drawing.Color]::FromArgb(9,6,4),90)),$rf)
$gold=[System.Drawing.Color]::FromArgb(240,201,128); $goldDim=[System.Drawing.Color]::FromArgb(150,122,74); $cream=[System.Drawing.Color]::FromArgb(245,233,208)
$B=[System.Drawing.FontStyle]::Bold; $I=[System.Drawing.FontStyle]::Italic; $Rg=[System.Drawing.FontStyle]::Regular
$brGold=New-Object System.Drawing.SolidBrush($gold); $brCream=New-Object System.Drawing.SolidBrush($cream)
$penLine=New-Object System.Drawing.Pen($goldDim,2.5)
$penG=New-Object System.Drawing.Pen($gold,4); $penG.StartCap='Round'; $penG.EndCap='Round'
$penRing=New-Object System.Drawing.Pen($gold,5)
$le=New-Object System.Drawing.StringFormat; $le.Alignment='Near'
$re=New-Object System.Drawing.StringFormat; $re.Alignment='Far'
$ce=New-Object System.Drawing.StringFormat; $ce.Alignment='Center'
function RRect($x,$y,$w,$h,$r){ $p=New-Object System.Drawing.Drawing2D.GraphicsPath; $d=2*$r
  $p.AddArc($x,$y,$d,$d,180,90);$p.AddArc(($x+$w-$d),$y,$d,$d,270,90);$p.AddArc(($x+$w-$d),($y+$h-$d),$d,$d,0,90);$p.AddArc($x,($y+$h-$d),$d,$d,90,90);$p.CloseFigure();return $p }
$g.DrawRectangle($penLine,35,35,($W-70),($H-70))
$g.DrawString("CONTROLES",(New-Object System.Drawing.Font("Georgia",42,$B)),$brGold,(New-Object System.Drawing.RectangleF(0,52,$W,58)),$ce)
$g.DrawString("Sigue a Adela y explora la Cochabamba de anta"+[char]0x00F1+"o",(New-Object System.Drawing.Font("Georgia",21,$I)),$brCream,(New-Object System.Drawing.RectangleF(0,118,$W,32)),$ce)

# --- foto real de frente ---
$S=1.7; $PX=425; $PY=150
$photo=[System.Drawing.Image]::FromFile("C:\UnrealProjects\JatunWasiNawpakay\Saved\ClaudeBackups\control_frente.png")
$g.DrawImage($photo,$PX,$PY,[int](500*$S),[int](345*$S)); $photo.Dispose()
function PX2([int]$ox,[int]$oy){ return @([int]($PX+$ox*$S),[int]($PY+$oy*$S)) }
# puntos de boton (medidos en la foto 500x345)
$Lstick=PX2 77 110; $Ltrig=PX2 133 192
$Rstick=PX2 417 112; $Rb=PX2 370 113; $Rtrig=PX2 357 197
function Ring($p,$r){ $g.DrawEllipse($penRing,($p[0]-$r),($p[1]-$r),(2*$r),(2*$r)) }
Ring $Lstick 30; Ring $Ltrig 24; Ring $Rstick 30; Ring $Rb 20; Ring $Rtrig 24

# --- callouts ---
$fT=New-Object System.Drawing.Font("Segoe UI",24,$B)
$fBd=New-Object System.Drawing.Font("Segoe UI",18,$Rg)
function CalloutL($from,$ty,$title,$body){
  $ex=430; $ey=$ty+16
  $g.DrawLine($penG,$from[0],$from[1],$ex,$ey); $g.FillEllipse($brGold,($from[0]-6),($from[1]-6),12,12)
  $g.DrawString($title,$fT,$brGold,(New-Object System.Drawing.RectangleF(55,$ty,360,30)),$le)
  $g.DrawString($body,$fBd,$brCream,(New-Object System.Drawing.RectangleF(55,($ty+34),380,90)),$le)
}
function CalloutR($from,$ty,$title,$body){
  $ex=1270; $ey=$ty+16
  $g.DrawLine($penG,$from[0],$from[1],$ex,$ey); $g.FillEllipse($brGold,($from[0]-6),($from[1]-6),12,12)
  $g.DrawString($title,$fT,$brGold,(New-Object System.Drawing.RectangleF(1285,$ty,360,30)),$re)
  $g.DrawString($body,$fBd,$brCream,(New-Object System.Drawing.RectangleF(1265,($ty+34),380,90)),$re)
}
# IZQUIERDO
CalloutL $Lstick 250 "GIRAR" "Palanca izquierda: gira tu vista."
CalloutL $Ltrig 470 ("APUNTAR") ("Gatillo de atr"+[char]0x00E1+"s (izquierdo): apunta el rayo y selecciona / teletransporte.")
# DERECHO
CalloutR $Rstick 235 "MOVERTE" "Palanca derecha: camina por el lugar."
CalloutR $Rb 450 ("MEN"+[char]0x00DA) ("Bot"+[char]0x00F3+"n B derecho: abre y cierra el men"+[char]0x00FA+".")
CalloutR $Rtrig 640 "VER CONTENIDO" ("Gatillo de atr"+[char]0x00E1+"s (derecho): abre o cierra el texto y voz de una cartela.")

# --- banda inferior ---
$g.FillPath((New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(60,40,20))),(RRect 360 930 980 56 14))
$g.DrawPath($penLine,(RRect 360 930 980 56 14))
$g.DrawString("En VR ves tus MANOS, pero sostienes los controles reales: usa estos botones.",(New-Object System.Drawing.Font("Segoe UI",17,$B)),$brCream,(New-Object System.Drawing.RectangleF(370,947,960,28)),$ce)

$out="C:\UnrealProjects\JatunWasiNawpakay\Saved\ClaudeBackups\guia_controles.png"
$bmp.Save($out,[System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose();$bmp.Dispose(); "OK -> $out"