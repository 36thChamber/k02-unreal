"""Verify all six preferences survive a new controller/map and clamp invalid values."""
import unreal,json,time,traceback
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());D=ROOT/'Saved/Diagnostics/Integration';W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();pc=unreal.GameplayStatics.get_player_controller(W,0)
assert unreal.GameplayStatics.is_game_paused(W)
fields=['K02SensitivityX','K02SensitivityY','K02InvertX','K02InvertY','K02CameraFOV','K02CameraDistance']
pc.call_method('K02ResetComfortPreferences');pc.call_method('K02CycleSensitivityX');pc.call_method('K02ToggleInvertY');pc.call_method('K02CycleCameraFOV');pc.call_method('K02CycleCameraDistance')
before={f:pc.get_editor_property(f) for f in fields};saved=unreal.GameplayStatics.load_game_from_slot('K02_Preferences_v1',0);disk={f:saved.get_editor_property(f) for f in fields};assert before==disk
pc.get_editor_property('K02TrainingMenu').call_method('K02Restart')
class Test:
 def __init__(self):self.start=time.monotonic();self.handle=unreal.register_slate_post_tick_callback(self.tick)
 def tick(self,dt):
  if time.monotonic()-self.start<2:return
  unreal.unregister_slate_post_tick_callback(self.handle)
  try:
   w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();new=unreal.GameplayStatics.get_player_controller(w,0);p=unreal.GameplayStatics.get_player_pawn(w,0);cam=p.get_components_by_class(unreal.CameraComponent)[0];arm=p.get_components_by_class(unreal.SpringArmComponent)[0];after={f:new.get_editor_property(f) for f in fields};camera=[cam.field_of_view,arm.target_arm_length];checks={'reload':new!=pc and before==disk==after and unreal.GameplayStatics.is_game_paused(w),'applied_on_reload':camera==[95.,240.]}
   bounds={}
   for key,count,allowed in [('CameraFOV',3,[90.,95.,100.]),('CameraDistance',4,[200.,240.,280.,320.])]:
    vals=[];initial=new.get_editor_property('K02'+key)
    for _ in range(count):
     new.call_method('K02Cycle'+key);vals.append(new.get_editor_property('K02'+key))
    bounds[key]=vals;checks['cycle_'+key]=sorted(vals)==allowed and vals[-1]==initial
   # Restore defaults after probes; tests should leave a predictable starting camera.
   new.call_method('K02ResetComfortPreferences');checks['reset']=[cam.field_of_view,arm.target_arm_length]==[90.,200.]
   r={'pass':all(checks.values()),'error':None,'checks':checks,'before':before,'disk':disk,'after':after,'camera_after_reload':camera,'cycle_readbacks':bounds}
  except Exception:r={'pass':False,'error':traceback.format_exc()}
  (D/'extended-preferences-reload-v3.json').write_text(json.dumps(r,indent=2));print('EXTENDED_PREFERENCES_RELOAD',r['pass'])
test=Test()
