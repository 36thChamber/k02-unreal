param([int]$EditorPid)
Add-Type @'
using System;using System.Text;using System.Runtime.InteropServices;
public static class K02Window {
 public delegate bool EnumProc(IntPtr h,IntPtr l);
 [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb,IntPtr l);
 [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h,out uint p);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h,StringBuilder s,int n);
 [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h,uint m,IntPtr w,IntPtr l);
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
 [DllImport("user32.dll")] public static extern bool SetCursorPos(int x,int y);
 public static void Focus(int pid){
  IntPtr main=IntPtr.Zero;
  EnumWindows((h,l)=>{uint p;GetWindowThreadProcessId(h,out p);if(p!=pid)return true;var s=new StringBuilder(512);GetWindowText(h,s,512);var title=s.ToString();
   if(title=="Message Log")PostMessage(h,0x10,IntPtr.Zero,IntPtr.Zero);
   if(title.Contains("Unreal Editor"))main=h;
   return true;
  },IntPtr.Zero);
  if(main==IntPtr.Zero)throw new Exception("Main editor window not found");
  SetForegroundWindow(main);SetCursorPos(850,580);
 }
}
'@
[K02Window]::Focus($EditorPid)
