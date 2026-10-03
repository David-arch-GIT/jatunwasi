# Guia de controles Quest REAL: DER=moverte, IZQ=girar camara, B(der)=menu, gatillo der=ver contenido.
Add-Type -AssemblyName System.Drawing
$W=1700; $H=1080
$bmp=New-Object System.Drawing.Bitmap($W,$H); $g=[System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode='AntiAlias'; $g.TextRenderingHint='ClearTypeGridFit'
$rf=New-Object System.Drawing.Rectangle(0,0,$W,$H)
$g.FillRectangle((New-Object System.Drawing.Drawing2D.LinearGradientBrush($rf,[System.Drawing.Color]::FromArgb(30,21,13),[System.Drawing.Color]::FromArgb(9,6,4),90)),$rf)
$gold=[System.Drawing.Color]::FromArgb(235,197,124); $goldDim=[System.Drawing.Color]::FromArgb(150,122,74); $cream=[System.Drawing.Color]::FromArgb(244,231,205)
$B=[System.Drawing.FontStyle]::Bold; $I=[System.Drawing.FontStyle]::Italic; $Rg=[System.Drawing.FontStyle]::Regular
$penGold=New-Object System.Drawing.Pen($gold,3); $penLine=New-Object System.Drawing.Pen($goldDim,2.5)
$brGold=New-Object System.Drawing.SolidBrush($gold); $brCream=New-Object System.Drawing.SolidBrush($cream)
$grayB=New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(95,95,103))
$ce=New-Object System.Drawing.StringFormat; $ce.Alignment='Center'
$le=New-Object System.Drawing.StringFormat; $le.Alignment='Near'
$re=New-Object System.Drawing.StringFormat; $re.Alignment='Far'
$g.DrawRectangle($penLine,35,35,($W-70),($H-70))
$g.DrawString("CONTROLES",(New-Object System.Drawing.Font("Georgia",44,$B)),$brGold,(New-Object System.Drawing.RectangleF(0,52,$W,62)),$ce)
$g.DrawString("Sigue a Adela y explora la Cochabamba de anta"+[char]0x00F1+"o",(New-Object System.Drawing.Font("Georgia",22,$I)),$brCream,(New-Object System.Drawing.RectangleF(0,122,$W,34)),$ce)
function RRect($x,$y,$w,$h,$r){ $p=New-Object System.Drawing.Drawing2D.GraphicsPath; $d=2*$r
  $p.AddArc($x,$y,$d,$d,180,90);$p.AddArc(($x+$w-$d),$y,$d,$d,270,90);$p.AddArc(($x+$w-$d),($y+$h-$d),$d,$d,0,90);$p.AddArc($x,($y+$h-$d),$d,$d,90,90);$p.CloseFigure();return $p }
function DrawCtrl($cx,$topY,$left){
  $g.DrawEllipse((New-Object System.Drawing.Pen($goldDim,7)),($cx-92),($topY-6),184,150)
  $br=New-Object System.Drawing.RectangleF(($cx-58),($topY+40),116,230)
  $g.FillPath((New-Object System.Drawing.Drawing2D.LinearGradientBrush($br,[System.Drawing.Color]::FromArgb(120,120,128),[System.Drawing.Color]::FromArgb(38,38,44),0)),(RRect ($cx-58) ($topY+40) 116 230 40))
  $g.DrawPath((New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(180,180,190),2)),(RRect ($cx-58) ($topY+40) 116 230 40))
  $g.FillPath((New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(60,60,68))),(RRect ($cx-64) ($topY+30) 128 120 40))
  $tsx=$cx; $tsy=$topY+70
  $g.FillEllipse((New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(25,25,30))),($tsx-30),($tsy-30),60,60)
  $g.FillEllipse($brGold,($tsx-22),($tsy-22),44,44); $g.DrawEllipse($penGold,($tsx-30),($tsy-30),60,60)
  # botones cara: derecho b2(izq)=B resaltado
  $b1x=$cx+8; $b2x=$cx-42; $by=$topY+110
  $fb=New-Object System.Drawing.Font("Segoe UI",14,$B)
  if($left){$n1="X";$n2="Y"; $g.FillEllipse($grayB,$b1x,$by,34,34); $g.FillEllipse($grayB,$b2x,$by,34,34)}
  else{$n1="A";$n2="B"; $g.FillEllipse($grayB,$b1x,$by,34,34); $g.FillEllipse($brGold,$b2x,$by,34,34); $g.DrawEllipse($penGold,$b2x,$by,34,34)}
  $g.DrawString($n1,$fb,$brCream,(New-Object System.Drawing.RectangleF($b1x,($by+4),34,26)),$ce)
  $g.DrawString($n2,$fb,(New-Object System.Drawing.SolidBrush((&{if($left){$cream}else{[System.Drawing.Color]::FromArgb(40,30,10)}}))),(New-Object System.Drawing.RectangleF($b2x,($by+4),34,26)),$ce)
  # menu ≡ neutro
  $mx=$cx-30; $my=$topY+165; $g.FillPath($grayB,(RRect $mx $my 34 18 6))
  for($i=0;$i -lt 3;$i++){ $g.DrawLine((New-Object System.Drawing.Pen($cream,2)),($mx+7),($my+4+$i*5),($mx+27),($my+4+$i*5)) }
  # gatillo: resaltado en AMBOS (izq=menu, der=cartelas)
  $gx=$cx; $gy=$topY+232
  $g.FillEllipse($brGold,($gx-16),($gy-16),32,32); $g.DrawEllipse($penGold,($gx-16),($gy-16),32,32)
  return @{ts=@($tsx,$tsy); bbtn=@(($b2x+17),($by+17)); trig=@($gx,$gy)}
}
$L=DrawCtrl 520 250 $true
$R=DrawCtrl 1180 250 $false
$g.DrawString("CONTROL IZQUIERDO",(New-Object System.Drawing.Font("Georgia",20,$B)),$brCream,(New-Object System.Drawing.RectangleF(300,545,440,28)),$ce)
$g.DrawString("CONTROL DERECHO",(New-Object System.Drawing.Font("Georgia",20,$B)),$brCream,(New-Object System.Drawing.RectangleF(960,545,440,28)),$ce)
$fAb=New-Object System.Drawing.Font("Segoe UI",22,$B); $fA=New-Object System.Drawing.Font("Segoe UI",19,$Rg)
function Callout($from,$tx,$ty,$title,$body,$w,$align){
  $sf=$le; $ax=$tx; if($align -eq 'r'){$sf=$re; $ax=$tx+$w}
  $g.DrawLine($penLine,$from[0],$from[1],$ax,($ty-4)); $g.FillEllipse($brGold,($from[0]-5),($from[1]-5),10,10)
  $g.DrawString($title,$fAb,$brGold,(New-Object System.Drawing.RectangleF($tx,$ty,$w,28)),$sf)
  $g.DrawString($body,$fA,$brCream,(New-Object System.Drawing.RectangleF($tx,($ty+30),$w,92)),$sf)
}
# IZQUIERDO: girar (palanca) + apuntar/seleccionar menu (gatillo)
Callout $L.ts 70 600 "GIRAR LA CAMARA" "Palanca izquierda: gira tu vista." 440 'l'
Callout $L.trig 70 770 ("APUNTAR / SELECCIONAR") ("Gatillo izquierdo: apunta el rayo y selecciona (teletransporte).") 460 'l'
# DERECHO: moverte (palanca) + B menu + gatillo ver contenido
Callout $R.ts 1200 600 "MOVERTE" "Palanca derecha: camina por el lugar." 440 'r'
Callout $R.bbtn 1200 770 ("ABRIR / CERRAR MENU") ("Boton B: abre y cierra el men"+[char]0x00FA+".") 440 'r'
Callout $R.trig 1200 900 "VER CONTENIDO" ("Gatillo derecho: abre o cierra el texto y voz de una cartela.") 440 'r'
$g.FillPath((New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(60,40,20))),(RRect 380 990 940 56 14))
$g.DrawPath($penLine,(RRect 380 990 940 56 14))
$g.DrawString("En VR ves tus MANOS, pero sostienes los controles reales: usa estos botones.",(New-Object System.Drawing.Font("Segoe UI",17,$B)),$brCream,(New-Object System.Drawing.RectangleF(390,1007,920,28)),$ce)
$out="C:\UnrealProjects\JatunWasiNawpakay\Saved\ClaudeBackups\guia_controles.png"
$bmp.Save($out,[System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose();$bmp.Dispose(); "OK -> $out"