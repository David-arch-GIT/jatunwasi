Add-Type -AssemblyName System.Drawing
$dir = "C:\UnrealProjects\JatunWasiNawpakay\Content\Cartelas\Tex"
New-Item -ItemType Directory -Force -Path $dir | Out-Null
$jsonPath = "C:\UnrealProjects\JatunWasiNawpakay\Scripts_Tesis\cartelas.json"
$items = Get-Content $jsonPath -Raw -Encoding UTF8 | ConvertFrom-Json

function New-RoundedPath([int]$x,[int]$y,[int]$w,[int]$h,[int]$r){
  $p = New-Object System.Drawing.Drawing2D.GraphicsPath
  $d = $r*2
  $p.AddArc($x,$y,$d,$d,180,90)
  $p.AddArc(($x+$w-$d),$y,$d,$d,270,90)
  $p.AddArc(($x+$w-$d),($y+$h-$d),$d,$d,0,90)
  $p.AddArc($x,($y+$h-$d),$d,$d,90,90)
  $p.CloseFigure()
  return $p
}
function Draw-Diamond($g,$brush,[double]$cx,[double]$cy,[double]$s){
  $pts = @(
    (New-Object System.Drawing.PointF($cx,($cy-$s))),
    (New-Object System.Drawing.PointF(($cx+$s),$cy)),
    (New-Object System.Drawing.PointF($cx,($cy+$s))),
    (New-Object System.Drawing.PointF(($cx-$s),$cy))
  )
  $g.FillPolygon($brush,$pts)
}

foreach($it in $items){
  $W=1600; $H=1000
  $bmp=New-Object System.Drawing.Bitmap($W,$H,[System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
  $g=[System.Drawing.Graphics]::FromImage($bmp)
  $g.SmoothingMode=[System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
  $g.TextRenderingHint=[System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
  $g.Clear([System.Drawing.Color]::FromArgb(0,0,0,0))
  # panel
  $m=70; $pw=$W-2*$m; $ph=$H-2*$m
  $panel=New-RoundedPath $m $m $pw $ph 40
  # fondo con degradado calido semitransparente (vidrio holografico)
  $r1=New-Object System.Drawing.Rectangle($m,$m,$pw,$ph)
  $grad=New-Object System.Drawing.Drawing2D.LinearGradientBrush($r1,([System.Drawing.Color]::FromArgb(232,34,26,18)),([System.Drawing.Color]::FromArgb(232,20,15,10)),90.0)
  $g.FillPath($grad,$panel)
  # borde dorado doble
  $gold=[System.Drawing.Color]::FromArgb(255,206,170,104)
  $goldSoft=[System.Drawing.Color]::FromArgb(255,150,120,70)
  $penOut=New-Object System.Drawing.Pen($gold,4)
  $g.DrawPath($penOut,$panel)
  $inset=22
  $panel2=New-RoundedPath ($m+$inset) ($m+$inset) ($pw-2*$inset) ($ph-2*$inset) 28
  $penIn=New-Object System.Drawing.Pen($goldSoft,2)
  $g.DrawPath($penIn,$panel2)
  # diamantes ornamentales en bordes (centros)
  $gb=New-Object System.Drawing.SolidBrush($gold)
  $cx=$W/2; $topY=$m+$inset; $botY=$m+$ph-$inset
  Draw-Diamond $g $gb $cx $topY 16
  Draw-Diamond $g $gb $cx $botY 16
  # esquinas
  foreach($pt in @(@(($m+$inset),$topY),@(($m+$pw-$inset),$topY),@(($m+$inset),$botY),@(($m+$pw-$inset),$botY))){
    Draw-Diamond $g $gb $pt[0] $pt[1] 12
  }
  # TITULO
  $sf=New-Object System.Drawing.StringFormat
  $sf.Alignment=[System.Drawing.StringAlignment]::Center
  $titleFont=New-Object System.Drawing.Font("Georgia",44,[System.Drawing.FontStyle]::Bold)
  $titleBrush=New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255,232,205,150))
  $title=$it.title.ToUpper()
  $tRect=New-Object System.Drawing.RectangleF($m,($m+70),$pw,120)
  $g.DrawString($title,$titleFont,$titleBrush,$tRect,$sf)
  # linea bajo titulo
  $lyc=$m+190
  $penLine=New-Object System.Drawing.Pen($goldSoft,2)
  $g.DrawLine($penLine,($cx-160),$lyc,($cx-30),$lyc)
  $g.DrawLine($penLine,($cx+30),$lyc,($cx+160),$lyc)
  Draw-Diamond $g $gb $cx $lyc 9
  # CUERPO
  $bodyFont=New-Object System.Drawing.Font("Georgia",29,[System.Drawing.FontStyle]::Regular)
  $bodyBrush=New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255,236,226,206))
  $sf2=New-Object System.Drawing.StringFormat
  $sf2.Alignment=[System.Drawing.StringAlignment]::Center
  $sf2.LineAlignment=[System.Drawing.StringAlignment]::Near
  $bRect=New-Object System.Drawing.RectangleF(($m+90),($lyc+40),($pw-180),($ph-320))
  $g.DrawString($it.body,$bodyFont,$bodyBrush,$bRect,$sf2)
  # ICONO BOCINA (abajo derecha)
  $ix=$m+$pw-120; $iy=$m+$ph-95
  $g.FillRectangle($gb,($ix-2),($iy+8),14,20)
  $spk=@(
    (New-Object System.Drawing.PointF(($ix+12),($iy+18))),
    (New-Object System.Drawing.PointF(($ix+34),($iy+2))),
    (New-Object System.Drawing.PointF(($ix+34),($iy+34)))
  )
  $g.FillPolygon($gb,$spk)
  $penSpk=New-Object System.Drawing.Pen($gold,3)
  $g.DrawArc($penSpk,($ix+38),($iy+6),16,24,-55,110)
  $g.DrawArc($penSpk,($ix+46),($iy-2),22,40,-55,110)
  $g.Dispose()
  $out=Join-Path $dir ($it.file+".png")
  $bmp.Save($out,[System.Drawing.Imaging.ImageFormat]::Png)
  $bmp.Dispose()
  "OK $($it.file)"
}
