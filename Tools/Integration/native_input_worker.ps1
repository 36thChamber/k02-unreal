param([int]$EditorPid,[int]$LifetimeSeconds=180)
$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class K02Input {
 [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
 [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h,out uint p);
 [DllImport("user32.dll")] public static extern void mouse_event(uint f,uint x,uint y,uint d,UIntPtr e);
 [DllImport("user32.dll")] public static extern void keybd_event(byte k,byte s,uint f,UIntPtr e);
 public static uint ForegroundPid(){uint p;GetWindowThreadProcessId(GetForegroundWindow(),out p);return p;}
 public static void Key(byte k,bool down){keybd_event(k,0,down?0u:2u,UIntPtr.Zero);}
 public static void Move(int x,int y){mouse_event(1u,unchecked((uint)x),unchecked((uint)y),0,UIntPtr.Zero);}
 public static void Mouse(bool left,bool down){mouse_event(left?(down?2u:4u):(down?8u:16u),0,0,0,UIntPtr.Zero);}
}
'@
$queue='A:\K-02 5.8\Saved\NativeInputBridge'
New-Item -ItemType Directory -Path $queue -Force | Out-Null
$held=@{}
$lastHeartbeat=[DateTime]::MinValue
function Release-K02($key) {
 if($key -eq 'P'){[K02Input]::Mouse($true,$false)} elseif($key -eq 'F'){[K02Input]::Mouse($false,$false)} else {[K02Input]::Key([byte]$key,$false)}
}
$end=[DateTime]::UtcNow.AddSeconds($LifetimeSeconds)
@{pid=$PID;editor_pid=$EditorPid;started=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content "$queue\worker.json"
while([DateTime]::UtcNow -lt $end -and (Get-Process -Id $EditorPid -ErrorAction SilentlyContinue)) {
 if(([DateTime]::UtcNow-$lastHeartbeat).TotalSeconds -gt 0.5){[DateTime]::UtcNow.ToString('o') | Set-Content "$queue\heartbeat.txt";$lastHeartbeat=[DateTime]::UtcNow}
 foreach($key in @($held.Keys)) {if([DateTime]::UtcNow -gt $held[$key] -or [K02Input]::ForegroundPid() -ne $EditorPid){Release-K02 $key;$held.Remove($key)}}
 foreach($file in Get-ChildItem $queue -Filter '*.pending.json' | Sort-Object Name) {
  $job=Get-Content -Raw $file.FullName | ConvertFrom-Json
  $claimed=$file.FullName.Replace('.pending.json','.running.json');Move-Item $file.FullName $claimed
  $r=@{id=$job.id;key=$job.key;ok=$false;started=[DateTime]::UtcNow.ToString('o')}
  try {
   if([K02Input]::ForegroundPid() -ne $EditorPid){throw 'Foreground is not the authorized Unreal process'}
   if(([DateTimeOffset]::UtcNow-[DateTimeOffset]::Parse($job.created)).TotalSeconds -gt 1){throw 'Expired input request'}
   switch($job.key) {
    'MouseRight' {[K02Input]::Move(40,0)}
    'MouseDown' {[K02Input]::Move(0,40)}
    'P' {try {[K02Input]::Mouse($true,$true);Start-Sleep -Milliseconds 50} finally {[K02Input]::Mouse($true,$false)}}
    'F' {try {[K02Input]::Mouse($false,$true);Start-Sleep -Milliseconds 50} finally {[K02Input]::Mouse($false,$false)}}
    'K' {try {[K02Input]::Key(69,$true);Start-Sleep -Milliseconds 50} finally {[K02Input]::Key(69,$false)}}
    'T' {try {[K02Input]::Key(82,$true);Start-Sleep -Milliseconds 50} finally {[K02Input]::Key(82,$false)}}
    'FRONT_T' {try {[K02Input]::Key(87,$true);Start-Sleep -Milliseconds 120;[K02Input]::Key(82,$true);Start-Sleep -Milliseconds 50} finally {[K02Input]::Key(82,$false);[K02Input]::Key(87,$false)}}
    default {
     if($job.key -notmatch '^(Ctrl|Shift|W|A|S|D|E|R|P|F|Enter|Escape|ArrowDown|ArrowUp|L|Space)(Down|Up)$'){throw 'Unsupported test input'}
     $name=$Matches[1];$down=$Matches[2] -eq 'Down';$codes=@{Ctrl=162;Shift=160;W=87;A=65;S=83;D=68;E=69;R=82;Enter=13;Escape=27;ArrowDown=40;ArrowUp=38;L=76;Space=32}
     $key=if($name -in @('P','F')){$name}else{[string]$codes[$name]}
     if($name -in @('P','F')){[K02Input]::Mouse($name -eq 'P',$down)}else{[K02Input]::Key([byte]$codes[$name],$down)}
     if($down){$hold=5;if($job.hold_seconds){$hold=[Math]::Max(1,[Math]::Min(20,[double]$job.hold_seconds))};$held[$key]=[DateTime]::UtcNow.AddSeconds($hold)}else{$held.Remove($key)}
    }
   }
   $r.ok=$true
  } catch {$r.error=$_.Exception.Message}
  $r.finished=[DateTime]::UtcNow.ToString('o');$r | ConvertTo-Json | Set-Content $file.FullName.Replace('.pending.json','.result.json')
  Move-Item $claimed $file.FullName.Replace('.pending.json','.done.json')
 }
 Start-Sleep -Milliseconds 5
}

foreach($key in @($held.Keys)){Release-K02 $key}
