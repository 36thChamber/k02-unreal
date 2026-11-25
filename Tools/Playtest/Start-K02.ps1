# Local uncooked playtest launcher. Requires the existing Unreal installation.
$ErrorActionPreference='Stop'
$projectRoot=(Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$project=Join-Path $projectRoot 'MultiplayerActionCombatSy.uproject'
$engine='A:\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
if(-not (Test-Path $project) -or -not (Test-Path $engine)){Write-Host 'Não foi possível localizar o projeto K-02 ou a Unreal 5.8.';exit 1}
$running=Get-CimInstance Win32_Process -Filter "Name='UnrealEditor.exe'" | Where-Object {$_.CommandLine -and $_.CommandLine.Contains($projectRoot)}
if($running){Write-Host 'K-02 já está aberto. Use a janela existente ou feche o Editor antes de iniciar este teste.';exit 2}
$logFolder=Join-Path $projectRoot 'Saved\Logs';New-Item -ItemType Directory -Force -Path $logFolder | Out-Null
$stamp=[DateTime]::Now.ToString('yyyyMMdd-HHmmss-fff');$log=Join-Path $logFolder "K02-Play-$stamp.log"
$argsText='"'+$project+'" /Game/K02/Prototype/Levels/L_K02_CombatArena -game -windowed -ResX=1280 -ResY=720 -NoSplash -DisablePython -abslog="'+$log+'" -ExecCmds="t.MaxFPS 60"'
Start-Process -FilePath $engine -ArgumentList $argsText | Out-Null
Write-Host 'Abrindo a arena. Consulte os controles e as opções no menu inicial. Esc pausa o treino.'
