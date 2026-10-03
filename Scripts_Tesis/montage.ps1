Add-Type -AssemblyName System.Drawing
$dir = "C:\UnrealProjects\JatunWasiNawpakay\Saved\ClaudeBackups"
$labels = @("MUS_Cuadro_00","MUS_Cuadro_01","MUS_Cuadro_02","MUS_Cuadro_03","MUS_Cuadro_coc0","MUS_Cuadro_coc1","MUS_Cuadro_dorm0","BALL_Cuadro_0","BALL_Cuadro_1","COR_Cuadro_00","COR_Cuadro_01","COR_Cuadro_03","COR_Cuadro_07")
$cols = 4; $tw = 300; $th = 168; $lblH = 22
$rows = [math]::Ceiling($labels.Count / $cols)
$W = $cols*$tw; $H = $rows*($th+$lblH)
$mont = New-Object System.Drawing.Bitmap($W, $H)
$g = [System.Drawing.Graphics]::FromImage($mont)
$g.Clear([System.Drawing.Color]::Black)
$fnt = New-Object System.Drawing.Font("Arial", 11, [System.Drawing.FontStyle]::Bold)
$wb = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
for ($i=0; $i -lt $labels.Count; $i++) {
  $lbl = $labels[$i]
  $c = $i % $cols; $r = [math]::Floor($i / $cols)
  $x = $c*$tw; $y = $r*($th+$lblH)
  $g.DrawString($lbl, $fnt, $wb, ($x+3), ($y+2))
  $p = Join-Path $dir ("w_"+$lbl+".png")
  if (Test-Path $p) {
    $img = [System.Drawing.Image]::FromFile($p)
    $g.DrawImage($img, $x, ($y+$lblH), $tw, $th)
    $img.Dispose()
  }
}
$g.Dispose()
$mont.Save((Join-Path $dir "montage.png"), [System.Drawing.Imaging.ImageFormat]::Png)
$mont.Dispose()
"MONTAGE OK"
