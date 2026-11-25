param([ValidateSet(30,60,120)][int]$Fps=60,[ValidatePattern('^[A-Za-z0-9_-]+$')][string]$Name='standalone', [int]$CaptureFrames=1800)
$ErrorActionPreference='Stop';$ProgressPreference='SilentlyContinue'
$root='A:\K-02 5.8';$log="$root\Saved\Logs\$Name.log"
if(Test-Path $log){throw 'Log already exists; choose a new run name'}
$argsText='"'+$root+'\MultiplayerActionCombatSy.uproject" /Game/K02/Prototype/Levels/L_K02_CombatArena -game -windowed -ResX=1280 -ResY=720 -NoSplash -DisablePython -abslog="'+$log+'" -ExecCmds="t.MaxFPS '+$Fps+',csvprofile FRAMES='+$CaptureFrames+'"'
$p=Start-Process -FilePath 'A:\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe' -ArgumentList $argsText -PassThru
$r=@{pid=$p.Id;fps_cap=$Fps;log=$log;arguments=$argsText;started=[DateTime]::UtcNow.ToString('o');kind='Uncooked Standalone via UnrealEditor, not packaged build'}
$r | ConvertTo-Json | Set-Content "$root\Saved\Diagnostics\Integration\$Name-launch.json"
$r | ConvertTo-Json -Compress
