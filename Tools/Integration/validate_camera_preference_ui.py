"""Native menu navigation and runtime camera/SaveGame readback; no physical gamepad claim."""
import unreal,json,time,datetime,uuid,traceback
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());D=ROOT/'Saved/Diagnostics/Integration';Q=ROOT/'Saved/NativeInputBridge';W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();assert W
class Test:
 def __init__(self):
  assert time.time()-Q.joinpath('heartbeat.txt').stat().st_mtime<2
  self.pc=unreal.GameplayStatics.get_player_controller(W,0);self.p=unreal.GameplayStatics.get_player_pawn(W,0);self.cam=self.p.get_components_by_class(unreal.CameraComponent)[0];self.arm=self.p.get_components_by_class(unreal.SpringArmComponent)[0];self.pc.call_method('K02ResetComfortPreferences');self.start=time.monotonic();self.done=set();self.rows=[];self.jobs=[];self.checks={}
  for a in unreal.GameplayStatics.get_all_actors_of_class(W,unreal.Character):
   if a!=self.p:
    c=a.get_controller();c.stop_movement();brain=c.get_editor_property('BrainComponent')
    if brain:brain.stop_logic('Camera settings validation')
  self.handle=unreal.register_slate_post_tick_callback(self.tick)
 def send(self,key):
  ident=str(time.time_ns())+'-'+uuid.uuid4().hex[:6];f=Q/(ident+'.tmp');f.write_text(json.dumps({'id':ident,'key':key,'created':datetime.datetime.now(datetime.timezone.utc).isoformat()}));f.rename(Q/(ident+'.pending.json'));self.jobs.append(ident)
 def snapshot(self,n):
  r={'stage':n,'paused':unreal.GameplayStatics.is_game_paused(W),'camera_fov':self.cam.field_of_view,'camera_arm':self.arm.target_arm_length,'manager_fov':self.pc.player_camera_manager.get_fov_angle()}
  for key in ['K02CameraFOV','K02CameraDistance','K02PreferencesSaved','K02ComfortOpen','K02TrainingMenuOpen']:r[key]=self.pc.get_editor_property(key)
  u=self.pc.get_editor_property('K02ComfortOptions')
  if u:r['labels']={k:str(u.get_editor_property(k).get_text()) for k in ['CameraFOVValue','CameraDistanceValue','SaveStatus']}
  self.rows.append(r);return r
 def tick(self,dt):
  try:
   t=time.monotonic()-self.start
   taps=[(.5,'ArrowDown'),(.8,'ArrowDown'),(1.1,'Enter'),(2,'ArrowDown'),(2.3,'ArrowDown'),(2.6,'ArrowDown'),(2.9,'ArrowDown'),(3.4,'Enter'),(3.9,'ArrowDown'),(4.4,'Enter'),(5.5,'Escape'),(6.5,'Escape')]
   events=[e for at,key in taps for e in [(at,key+'Down'),(at+.08,key+'Up')]]
   for i,(at,key) in enumerate(events):
    if t>=at and i not in self.done:self.done.add(i);self.send(key)
   for at,n in [(1.7,'options'),(5,'configured'),(7.2,'game')]:
    if t>=at and n not in self.done:
     self.done.add(n);r=self.snapshot(n)
     if n=='options':self.checks[n]=r['paused'] and r['K02ComfortOpen']
     if n=='configured':self.checks[n]=r['paused'] and r['K02CameraFOV']==95 and r['K02CameraDistance']==240 and r['K02PreferencesSaved'] and r['labels']['CameraFOVValue']=='95' and r['labels']['CameraDistanceValue']=='240'
     if n=='game':self.checks[n]=not r['paused'] and r['camera_fov']==95 and r['camera_arm']==240 and abs(r['manager_fov']-95)<.01
   if t>8:
    sg=unreal.GameplayStatics.load_game_from_slot('K02_Preferences_v1',0);self.checks['savegame']=sg.get_editor_property('K02CameraFOV')==95 and sg.get_editor_property('K02CameraDistance')==240
    self.pc.call_method('K02ShowTrainingMenu');self.finish()
  except Exception:self.finish(traceback.format_exc())
 def finish(self,error=None):
  unreal.unregister_slate_post_tick_callback(self.handle);jobs=[]
  for n in self.jobs:
   f=Q/(n+'.result.json');jobs.append(json.loads(f.read_text(encoding='utf-8-sig')) if f.exists() else {'id':n,'ok':False})
  r={'pass':not error and len(self.checks)==4 and all(self.checks.values()) and all(j['ok'] for j in jobs),'error':error,'checks':self.checks,'rows':self.rows,'native_inputs':jobs};(D/(globals().get('REQUEST',{}).get('params',{}).get('output','camera-preference-ui-v1')+'.json')).write_text(json.dumps(r,indent=2));print('CAMERA_PREFERENCE_UI',r['pass'],error)
test=Test()
