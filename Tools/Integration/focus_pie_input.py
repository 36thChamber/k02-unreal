"""Explicit input setup only after the OS has activated the Editor window."""
import unreal,ctypes,os
u=ctypes.windll.user32;pid=ctypes.c_ulong();u.GetWindowThreadProcessId(u.GetForegroundWindow(),ctypes.byref(pid));assert pid.value==os.getpid(),'Do not request synchronous game focus while another process is foreground'
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();assert w
pc=unreal.GameplayStatics.get_player_controller(w,0)
# Test-only: explicitly dismiss the startup menu before gameplay fixtures.
pc.call_method('K02EnsureTrainingMenu')
pc.call_method('K02CloseTrainingMenu')
unreal.get_default_object(unreal.load_class(None,'/Script/UMG.WidgetBlueprintLibrary')).call_method('SetInputMode_GameOnly',args=(pc,True))
unreal.get_default_object(unreal.load_class(None,'/Script/UMG.WidgetBlueprintLibrary')).call_method('SetFocusToGameViewport')
print('PIE input focus established while Editor is foreground')
