param([ValidateSet("Both","EvaluationOnly","UpdateOnly")][string]$Mode="Both",[ValidateSet(30,60,120)][int]$Fps=60,[ValidatePattern('^[A-Za-z0-9_-]+$')][string]$Name='standalone', [int]$CaptureFrames=1800)
$ErrorActionPreference='Stop';$ProgressPreference='SilentlyContinue'
$root='A:\K-02 5.8';$log="$root\Saved\Logs\$Name.log"
if(Test-Path $log){throw 'Log already exists; choose a new run name'}
$animationCommands=switch($Mode){'EvaluationOnly'{'a.ParallelAnimEvaluation 0,a.ParallelAnimUpdate 1,'};'UpdateOnly'{'a.ParallelAnimEvaluation 1,a.ParallelAnimUpdate 0,'};default{'a.ParallelAnimEvaluation 0,a.ParallelAnimUpdate 0,'}}
$argsText='"'+$root+'\MultiplayerActionCombatSy.uproject" /Game/K02/Prototype/Levels/L_K02_CombatArena -game -windowed -ResX=1280 -ResY=720 -NoSplash -DisablePython -abslog="'+$log+'" -ExecCmds="'+$animationCommands+'t.MaxFPS '+$Fps+',csvprofile FRAMES='+$CaptureFrames+'"'
$p=Start-Process -FilePath 'A:\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe' -ArgumentList $argsText -PassThru
$r=@{pid=$p.Id;fps_cap=$Fps;log=$log;arguments=$argsText;started=[DateTime]::UtcNow.ToString('o');animation_diagnostic=$Mode;kind='Diagnostic only: global serial animation; uncooked Standalone, not packaged build'}
$r | ConvertTo-Json | Set-Content "$root\Saved\Diagnostics\Integration\$Name-launch.json"
$r | ConvertTo-Json -Compress
