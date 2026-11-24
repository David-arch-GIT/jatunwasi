# 506_cartela_san_severino.ps1
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-25
# Proposito: pedido de la usuaria: "falto la cartela de San Severino en el convento". Genera SOLO para
#   san_severino (texto en cartelas.json, datos verificados: Los Tiempos 27/11/2016 y 17/03/2023, Ley 596 de
#   2014) la imagen del panel (mismo estilo que cartela_gen.ps1) y la voz Sabina (como cartela_audio.ps1),
#   ejecutando esos scripts con un JSON de un solo elemento. No toca las otras cartelas.
$uno = "C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/cartela_sansev.json"
foreach ($f in "cartela_gen.ps1", "cartela_audio.ps1") {
    $code = Get-Content "C:/UnrealProjects/JatunWasiNawpakay/Scripts_Tesis/$f" -Raw -Encoding UTF8
    $code = $code -replace '\$jsonPath = "[^"]+"', ('$jsonPath = "' + $uno + '"')
    Invoke-Expression $code
}
