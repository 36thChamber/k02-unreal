$ErrorActionPreference='Stop'
Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class K02ControllerProbe {
 [StructLayout(LayoutKind.Sequential)] public struct Pad {public ushort Buttons;public byte LT;public byte RT;public short LX;public short LY;public short RX;public short RY;}
 [StructLayout(LayoutKind.Sequential)] public struct State {public uint Packet;public Pad Gamepad;}
 [DllImport("xinput1_4.dll")] public static extern uint XInputGetState(uint index,out State state);
 public static uint Probe(uint index){State state;return XInputGetState(index,out state);}
}
'@
$controllers=0..3 | ForEach-Object { $status=[K02ControllerProbe]::Probe($_); @{slot=$_;connected=($status -eq 0);status=$status} }
$vswhere='C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe'
$r=@{utc=[DateTime]::UtcNow.ToString('o');xinput=$controllers;vswhere_present=(Test-Path $vswhere);windows_sdk_include=(Test-Path 'C:\Program Files (x86)\Windows Kits\10\Include');scope='Read-only discovery; not physical controller validation'}
if(Test-Path $vswhere){$r.visual_studio=(& $vswhere -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath)}
$r | ConvertTo-Json -Depth 5 | Set-Content 'A:\K-02 5.8\Saved\Diagnostics\Integration\build-gamepad-readiness.json'
$r | ConvertTo-Json -Depth 5
