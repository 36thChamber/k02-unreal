"""Read actual save slot and a new controller after arena reload."""
import unreal,json,time,traceback
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());D=ROOT/'Saved/Diagnostics/Integration';W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();pc=unreal.GameplayStatics.get_player_controller(W,0)
assert unreal.GameplayStatics.is_game_paused(W)
fields=['K02SensitivityX','K02SensitivityY','K02InvertX','K02InvertY']
pc.call_method('K02ResetComfortPreferences');pc.call_method('K02CycleSensitivityX');pc.call_method('K02CycleSensitivityX');pc.call_method('K02ToggleInvertY')
before={f:pc.get_editor_property(f) for f in fields};saved=unreal.GameplayStatics.load_game_from_slot('K02_Preferences_v1',0);disk={f:saved.get_editor_property(f) for f in fields};assert before==disk
pc.get_editor_property('K02TrainingMenu').call_method('K02Restart')
class Test:
 def __init__(self):self.start=time.monotonic();self.handle=unreal.register_slate_post_tick_callback(self.tick)
 def tick(self,dt):
  if time.monotonic()-self.start<2:return
  unreal.unregister_slate_post_tick_callback(self.handle)
  try:
   w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();new=unreal.GameplayStatics.get_player_controller(w,0);after={f:new.get_editor_property(f) for f in fields};r={'before':before,'disk':disk,'after':after,'new_controller':new!=pc,'paused':unreal.GameplayStatics.is_game_paused(w),'pass':new!=pc and before==disk==after and unreal.GameplayStatics.is_game_paused(w)}
  except Exception:r={'pass':False,'error':traceback.format_exc()}
  (D/'preferences-reload-validation.json').write_text(json.dumps(r,indent=2));unreal.log('K02_PREFERENCES_RELOAD '+str(r['pass']))
test=Test()
