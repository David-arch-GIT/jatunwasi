# Guia de controles con el CONTROL REAL (foto) + instrucciones claras al lado.
Add-Type -AssemblyName System.Drawing
$W=1700; $H=1000
$bmp=New-Object System.Drawing.Bitmap($W,$H); $g=[System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode='AntiAlias'; $g.TextRenderingHint='ClearTypeGridFit'; $g.InterpolationMode='HighQualityBicubic'
$rf=New-Object System.Drawing.Rectangle(0,0,$W,$H)
$g.FillRectangle((New-Object System.Drawing.Drawing2D.LinearGradientBrush($rf,[System.Drawing.Color]::FromArgb(30,21,13),[System.Drawing.Color]::FromArgb(9,6,4),90)),$rf)
$gold=[System.Drawing.Color]::FromArgb(235,197,124); $goldDim=[System.Drawing.Color]::FromArgb(150,122,74); $cream=[System.Drawing.Color]::FromArgb(244,231,205)
$B=[System.Drawing.FontStyle]::Bold; $I=[System.Drawing.FontStyle]::Italic; $Rg=[System.Drawing.FontStyle]::Regular
$penLine=New-Object System.Drawing.Pen($goldDim,2.5)
$brGold=New-Object System.Drawing.SolidBrush($gold); $brCream=New-Object System.Drawing.SolidBrush($cream)
$ce=New-Object System.Drawing.StringFormat; $ce.Alignment='Center'; $le=New-Object System.Drawing.StringFormat; $le.Alignment='Near'
function RRect($x,$y,$w,$h,$r){ $p=New-Object System.Drawing.Drawing2D.GraphicsPath; $d=2*$r
  $p.AddArc($x,$y,$d,$d,180,90);$p.AddArc(($x+$w-$d),$y,$d,$d,270,90);$p.AddArc(($x+$w-$d),($y+$h-$d),$d,$d,0,90);$p.AddArc($x,($y+$h-$d),$d,$d,90,90);$p.CloseFigure();return $p }
$g.DrawRectangle($penLine,35,35,($W-70),($H-70))
$g.DrawString("CONTROLES",(New-Object System.Drawing.Font("Georgia",44,$B)),$brGold,(New-Object System.Drawing.RectangleF(0,52,$W,62)),$ce)
$g.DrawString("Sigue a Adela y explora la Cochabamba de anta"+[char]0x00F1+"o",(New-Object System.Drawing.Font("Georgia",22,$I)),$brCream,(New-Object System.Drawing.RectangleF(0,122,$W,34)),$ce)

# --- foto del control real en tarjeta ---
$card=RRect 90 210 640 680 24
$g.FillPath((New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(245,244,242))),$card)
$g.DrawPath((New-Object System.Drawing.Pen($gold,3)),$card)
$ctrl=[System.Drawing.Image]::FromFile("C:\UnrealProjects\JatunWasiNawpakay\Saved\ClaudeBackups\control_real.png")
$g.DrawImage($ctrl,120,300,580,500)
$g.DrawString("Controles Meta Quest 2",(New-Object System.Drawing.Font("Segoe UI",18,$B)),(New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(60,50,40))),(New-Object System.Drawing.RectangleF(90,830,640,30)),$ce)
$ctrl.Dispose()

# --- instrucciones al lado ---
$fH=New-Object System.Drawing.Font("Georgia",26,$B)
$fB=New-Object System.Drawing.Font("Segoe UI",22,$B)
$fT=New-Object System.Drawing.Font("Segoe UI",20,$Rg)
$x=790
function Item($y,$parte,$que){
  $g.FillEllipse($brGold,$x,($y+8),14,14)
  $g.DrawString($parte,$fB,$brGold,(New-Object System.Drawing.RectangleF(($x+28),$y,560,30)),$le)
  $g.DrawString($que,$fT,$brCream,(New-Object System.Drawing.RectangleF(($x+28),($y+32),820,30)),$le)
}
$g.DrawString("CONTROL IZQUIERDO",$fH,$brCream,(New-Object System.Drawing.RectangleF($x,235,860,34)),$le)
Item 285 "Palanca" "GIRAR la camara (rapido, para no marearte)."
Item 350 "Gatillo" ("APUNTAR y seleccionar en el men"+[char]0x00FA+" (teletransporte, opciones).")

$g.DrawString("CONTROL DERECHO",$fH,$brCream,(New-Object System.Drawing.RectangleF($x,440,860,34)),$le)
Item 490 "Palanca" "MOVERTE por el lugar."
Item 555 ("Bot"+[char]0x00F3+"n B") "ABRIR / CERRAR el menu (B otra vez cierra)."
Item 620 "Gatillo" "VER CONTENIDO: apunta y abre/cierra su texto + audio."

$g.FillPath((New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(60,40,20))),(RRect 790 720 860 150 16))
$g.DrawPath($penLine,(RRect 790 720 860 150 16))
$g.DrawString(("Con el RAYO apuntas y seleccionas (incluye teletransporte)."),$fT,$brCream,(New-Object System.Drawing.RectangleF(815,745,820,30)),$le)
$g.DrawString(("En VR ver"+[char]0x00E1+"s tus MANOS, pero sostienes los controles"),$fT,$brCream,(New-Object System.Drawing.RectangleF(815,790,820,30)),$le)
$g.DrawString(("reales: usa estos botones."),$fT,$brCream,(New-Object System.Drawing.RectangleF(815,822,820,30)),$le)

$out="C:\UnrealProjects\JatunWasiNawpakay\Saved\ClaudeBackups\guia_controles.png"
$bmp.Save($out,[System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose();$bmp.Dispose(); "OK -> $out"