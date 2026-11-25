param([int]$GamePid,[int]$Seconds=20,[string]$Name='standalone-native',[switch]$Record,[switch]$StartupMenu,[switch]$MenuRegression,[switch]$PreferencesRegression,[switch]$CameraPreferencesRegression,[ValidateRange(1,20)][int]$SoakCycles=1)
$ErrorActionPreference='Stop';$ProgressPreference='SilentlyContinue'
if($Name -notmatch '^[A-Za-z0-9_-]+$'){throw 'Invalid test name'}
Add-Type -AssemblyName System.Drawing
Add-Type @'
using System;using System.Text;using System.Runtime.InteropServices;
public static class K02Standalone {
 public delegate bool EnumProc(IntPtr h,IntPtr l);
 [StructLayout(LayoutKind.Sequential)] public struct RECT{public int L,T,R,B;}
 [StructLayout(LayoutKind.Sequential)] public struct POINT{public int X,Y;}
 [DllImport("user32.dll")] static extern bool EnumWindows(EnumProc cb,IntPtr l);
 [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr h,out uint p);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)] static extern int GetWindowText(IntPtr h,StringBuilder s,int n);
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
 [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
 [DllImport("user32.dll")] public static extern bool IsHungAppWindow(IntPtr h);
 [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr h,out RECT r);
 [DllImport("user32.dll")] public static extern bool ClientToScreen(IntPtr h,ref POINT p);
 [DllImport("user32.dll")] public static extern bool SetCursorPos(int x,int y);
 [DllImport("user32.dll")] public static extern void mouse_event(uint f,uint x,uint y,uint d,UIntPtr e);
 [DllImport("user32.dll")] public static extern void keybd_event(byte k,byte s,uint f,UIntPtr e);
 public static IntPtr Find(int pid){IntPtr found=IntPtr.Zero;EnumWindows((h,l)=>{uint p;GetWindowThreadProcessId(h,out p);if(p!=pid)return true;var s=new StringBuilder(512);GetWindowText(h,s,512);if(s.ToString().Contains("64-bit Development"))found=h;return true;},IntPtr.Zero);return found;}
 public static void Key(byte k,bool down){keybd_event(k,0,down?0u:2u,UIntPtr.Zero);}
 public static void Mouse(uint flag){mouse_event(flag,0,0,0,UIntPtr.Zero);}
}
'@
# Wait for the arena/menu initialization, not merely creation of a window.
$processInfo=Get-CimInstance Win32_Process -Filter "ProcessId = $GamePid"
if($processInfo.CommandLine -notmatch '-abslog="([^"]+)"'){throw 'Standalone readiness requires an explicit test log path'}
$readyLog=$Matches[1];$readyDeadline=[DateTime]::UtcNow.AddSeconds(90);$ready=$false
while([DateTime]::UtcNow -lt $readyDeadline){
 if(Test-Path $readyLog){
  $logTail=(Get-Content $readyLog -Tail 1600 -ErrorAction SilentlyContinue) -join "`n"
  if($logTail -match 'Load map complete /Game/K02/Prototype/Levels/L_K02_CombatArena' -and $logTail -match 'Player bShowMouseCursor Changed, False -> True'){$ready=$true;break}
 }
 Start-Sleep -Milliseconds 250
}
if(-not $ready){throw 'Arena/menu initialization not confirmed; no native inputs sent'}
$hwnd=[K02Standalone]::Find($GamePid);if($hwnd -eq [IntPtr]::Zero){throw 'Standalone game window not found'}
[K02Standalone]::SetForegroundWindow($hwnd) | Out-Null
Start-Sleep -Milliseconds 250
if([K02Standalone]::GetForegroundWindow() -ne $hwnd){throw 'Could not focus authorized Standalone window'}
$rect=New-Object K02Standalone+RECT;$point=New-Object K02Standalone+POINT
[K02Standalone]::GetClientRect($hwnd,[ref]$rect) | Out-Null;[K02Standalone]::ClientToScreen($hwnd,[ref]$point) | Out-Null
[K02Standalone]::SetCursorPos($point.X+($rect.R/2),$point.Y+($rect.B/2)) | Out-Null
$out="A:\K-02 5.8\Saved\Diagnostics\Integration\$Name"
if(Test-Path $out){throw 'Evidence directory already exists; use a new test name'}
New-Item -ItemType Directory -Path $out | Out-Null
$events=@(@(1,87,1),@(2,87,0),@(3,162,1),@(4,65,1),@(4.12,65,0),@(5,162,0),@(6,'P',1),@(6.05,'P',0),@(6.2,'P',1),@(6.25,'P',0),@(6.4,'P',1),@(6.45,'P',0),@(8,76,1),@(8.05,76,0),@(9,65,1),@(10,65,0),@(11,'F',1),@(11.05,'F',0),@(11.4,69,1),@(11.45,69,0),@(13,76,1),@(13.05,76,0),@(14,83,1),@(15,83,0),@(16,162,1),@(17,68,1),@(17.12,68,0),@(18,162,0))
if($SoakCycles -gt 1){
 if($MenuRegression -or $PreferencesRegression -or $CameraPreferencesRegression -or -not $StartupMenu){throw 'Soak requires a fresh startup menu and cannot mix other scenarios'}
 $baseEvents=$events;$events=@()
 for($cycle=0;$cycle -lt $SoakCycles;$cycle++){
  $offset=25*$cycle
  foreach($e in $baseEvents){$events+=,@(($offset+[double]$e[0]),$e[1],$e[2])}
  $events+=,@(($offset+20),27,1);$events+=,@(($offset+20.1),27,0)
  if($cycle -lt ($SoakCycles-1)){
   $events+=,@(($offset+21),40,1);$events+=,@(($offset+21.1),40,0)
   $events+=,@(($offset+22),13,1);$events+=,@(($offset+22.1),13,0)
   $events+=,@(($offset+23.5),13,1);$events+=,@(($offset+23.6),13,0)
  }
 }
 $Seconds=25*$SoakCycles
}
if($StartupMenu){$events=@(@(0.25,13,1),@(0.35,13,0))+$events}
if($MenuRegression){$events=@(@(1,13,1),@(1.1,13,0),@(3,27,1),@(3.1,27,0),@(4,'P',1),@(4.1,'P',0),@(5,27,1),@(5.1,27,0),@(6,76,1),@(6.1,76,0),@(7,27,1),@(7.1,27,0),@(8,13,1),@(8.1,13,0),@(9,162,1),@(10,162,0),@(11,27,1),@(11.1,27,0),@(12,40,1),@(12.1,40,0),@(13,13,1),@(13.1,13,0),@(15,13,1),@(15.1,13,0),@(16,76,1),@(16.1,76,0),@(17,162,1),@(17.2,68,1),@(17.3,68,0),@(18,162,0),@(19,27,1),@(19.1,27,0))}
if($PreferencesRegression){$events=@(@(0.5,40,1),@(0.6,40,0),@(0.8,40,1),@(0.9,40,0),@(1.1,13,1),@(1.2,13,0),@(4,13,1),@(4.1,13,0),@(5,40,1),@(5.1,40,0),@(5.3,40,1),@(5.4,40,0),@(5.6,40,1),@(5.7,40,0),@(6,40,1),@(6.1,40,0),@(6.3,40,1),@(6.4,40,0),@(6.6,40,1),@(6.7,40,0),@(7,13,1),@(7.1,13,0),@(9,27,1),@(9.1,27,0),@(10,13,1),@(10.1,13,0),@(11,162,1),@(12,68,1),@(12.1,68,0),@(13,162,0),@(14,27,1),@(14.1,27,0),@(15,40,1),@(15.1,40,0),@(15.3,40,1),@(15.4,40,0),@(15.6,13,1),@(15.7,13,0))}
if($CameraPreferencesRegression){
 $events=@();$taps=@(@(0.5,40),@(0.8,40),@(1.1,13),@(2,40),@(2.3,40),@(2.6,40),@(2.9,40),@(3.4,13),@(3.9,40),@(4.4,13),@(6,27),@(7,27),@(9.5,76),@(13,27),@(14,40),@(15,13),@(17,40),@(17.3,40),@(17.6,13),@(19,40),@(19.2,40),@(19.4,40),@(19.6,40),@(19.8,40),@(20,40),@(20.3,13),@(21,27))
 foreach($tap in $taps){$events+=,@($tap[0],$tap[1],1);$events+=,@(($tap[0]+0.08),$tap[1],0)}
 $events+=,@(8,87,1);$events+=,@(9,87,0);$events+=,@(10,162,1);$events+=,@(11,68,1);$events+=,@(11.12,68,0);$events+=,@(12,162,0)
 $events=@($events | Sort-Object {[double]$_[0]});$Seconds=24
}
$watch=[Diagnostics.Stopwatch]::StartNew();$i=0;$frames=@();$inputs=@();$nextFrame=0;$frame=0;$errorText=$null
try {
 while($watch.Elapsed.TotalSeconds -lt $Seconds){
  if([K02Standalone]::GetForegroundWindow() -ne $hwnd){throw 'Foreground lost; inputs stopped and released'}
  if([K02Standalone]::IsHungAppWindow($hwnd)){throw 'Standalone did not respond to Windows; inputs stopped and released'}
  $t=$watch.Elapsed.TotalSeconds
  while($i -lt $events.Length -and $t -ge [double]$events[$i][0]){
   $e=$events[$i];$key=$e[1];$down=[bool]$e[2]
   if($key -is [string]){$flags=@{P=@(4,2);F=@(16,8);M=@(64,32)};[K02Standalone]::Mouse($flags[$key][[int]$down])}else{[K02Standalone]::Key([byte]$key,$down)}
   $inputs+=@{scheduled=$e[0];actual=$watch.Elapsed.TotalSeconds;key=$key;down=$down};$i++
  }
  if($t -ge $nextFrame){
   $bitmap=New-Object System.Drawing.Bitmap($rect.R,$rect.B);$g=[System.Drawing.Graphics]::FromImage($bitmap)
   $g.CopyFromScreen($point.X,$point.Y,0,0,$bitmap.Size)
   $file=('{0:D5}.png' -f $frame);$bitmap.Save((Join-Path $out $file));$g.Dispose();$bitmap.Dispose()
   $frames+=@{file=$file;t=$t};$frame++;$nextFrame=$t+$(if($Record){1.0/12.0}else{4.0})
  }
  Start-Sleep -Milliseconds 2
 }
} catch {$errorText=$_.Exception.Message}
finally {
 foreach($k in @(87,65,83,68,69,162,9,76,13,27,40)){[K02Standalone]::Key([byte]$k,$false)}
 foreach($flag in @(4,16,64)){[K02Standalone]::Mouse($flag)}
 @{pid=$GamePid;seconds=$watch.Elapsed.TotalSeconds;width=$rect.R;height=$rect.B;input_events=$inputs;frames=$frames;error=$errorText;scope='Native OS input and actual client-window pixels; no human approval';recording=[bool]$Record;soak_cycles=$SoakCycles;startup_menu=[bool]$StartupMenu;menu_regression=[bool]$MenuRegression;preferences_regression=[bool]$PreferencesRegression;camera_preferences_regression=[bool]$CameraPreferencesRegression} | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $out 'manifest.json')
}
if($errorText){throw $errorText}
Write-Output $out
