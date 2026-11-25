param([int]$GamePid,[string]$Name)
$ErrorActionPreference='Stop'
if($Name -notmatch '^[A-Za-z0-9_-]+$'){throw 'Invalid evidence name'}
$p=Get-Process -Id $GamePid
$info=Get-CimInstance Win32_Process -Filter "ProcessId = $GamePid"
if($info.CommandLine -notlike '*K-02 5.8*' -or $info.CommandLine -notlike '* -game *'){throw 'Only the authorized Standalone process may be dumped'}
$out="A:\K-02 5.8\Saved\Diagnostics\Integration\$Name"
New-Item -ItemType Directory -Path $out -ErrorAction Stop | Out-Null
$info | Select-Object ProcessId,CommandLine | ConvertTo-Json | Set-Content "$out\process.json"
Get-CimInstance Win32_OperatingSystem | Select-Object FreePhysicalMemory,FreeVirtualMemory,TotalVirtualMemorySize | ConvertTo-Json | Set-Content "$out\memory.json"
if($info.CommandLine -match '-abslog="([^\"]+)"'){Copy-Item $Matches[1] "$out\preserved.log"}
Add-Type @'
using System;using System.Runtime.InteropServices;
public static class K02Dump {
 [DllImport("Dbghelp.dll",SetLastError=true)] public static extern bool MiniDumpWriteDump(IntPtr process,uint pid,IntPtr file,uint type,IntPtr exception,IntPtr user,IntPtr callback);
}
'@
$f=[IO.File]::Open("$out\standalone-minidump.dmp",[IO.FileMode]::CreateNew,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None)
try {$ok=[K02Dump]::MiniDumpWriteDump($p.Handle,[uint32]$GamePid,$f.SafeFileHandle.DangerousGetHandle(),0x1020,[IntPtr]::Zero,[IntPtr]::Zero,[IntPtr]::Zero);if(-not $ok){throw "MiniDump failed: $([Runtime.InteropServices.Marshal]::GetLastWin32Error())"}}finally{$f.Dispose()}
Get-FileHash "$out\standalone-minidump.dmp" -Algorithm SHA256 | ConvertTo-Json
