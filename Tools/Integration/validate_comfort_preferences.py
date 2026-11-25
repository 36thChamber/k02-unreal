"""Native UI selection and actual mouse deltas; independent fixture resets after each sample."""
import unreal,json,time,datetime,uuid,traceback
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());D=ROOT/'Saved/Diagnostics/Integration';Q=ROOT/'Saved/NativeInputBridge';W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();assert W
class Test:
 def __init__(self):
  assert time.time()-Q.joinpath('heartbeat.txt').stat().st_mtime<2
  self.pc=unreal.GameplayStatics.get_player_controller(W,0);self.p=unreal.GameplayStatics.get_player_pawn(W,0);self.pc.call_method('K02ResetComfortPreferences');self.start=time.monotonic();self.done=set();self.rows=[];self.jobs=[];self.checks={}
  for a in unreal.GameplayStatics.get_all_actors_of_class(W,unreal.Character):
   if a!=self.p:
    c=a.get_controller();c.stop_movement();brain=c.get_editor_property('BrainComponent')
    if brain:brain.stop_logic('Mouse preferences isolation')
  self.handle=unreal.register_slate_post_tick_callback(self.tick)
 def send(self,key):
  name=str(time.time_ns())+'-'+uuid.uuid4().hex[:6];f=Q/(name+'.tmp');f.write_text(json.dumps({'id':name,'key':key,'created':datetime.datetime.now(datetime.timezone.utc).isoformat()}));f.rename(Q/(name+'.pending.json'));self.jobs.append(name)
 def snapshot(self,n):
  rot=self.pc.get_control_rotation();r={'stage':n,'wall':time.monotonic()-self.start,'paused':unreal.GameplayStatics.is_game_paused(W),'yaw':(rot.yaw+180)%360-180,'pitch':(rot.pitch+180)%360-180}
  for key in ['K02SensitivityX','K02SensitivityY','K02InvertX','K02InvertY','K02LookScaleX','K02LookScaleY','K02PreferencesSaved','K02ComfortOpen','K02TrainingMenuOpen']:r[key]=self.pc.get_editor_property(key)
  u=self.pc.get_editor_property('K02ComfortOptions')
  if u:r['labels']={k:str(u.get_editor_property(k).get_text()) for k in ['SensitivityXValue','SensitivityYValue','InvertXValue','InvertYValue','SaveStatus']}
  self.rows.append(r);return r
 def tick(self,dt):
  try:
   t=time.monotonic()-self.start
   taps=[(.5,'ArrowDown'),(.8,'ArrowDown'),(1.1,'Enter'),(2,'Enter'),(2.5,'ArrowDown'),(3,'Enter'),(3.5,'ArrowDown'),(4,'Enter'),(4.5,'ArrowDown'),(5,'Enter'),(6,'Escape'),(7,'Escape')]
   events=[]
   for at,key in taps:events.extend([(at,key+'Down'),(at+.08,key+'Up')])
   events += [(8,'MouseRight'),(9,'MouseDown'),(11,'MouseRight'),(12,'MouseDown')]
   for i,(at,key) in enumerate(events):
    if t>=at and ('input',i) not in self.done:self.done.add(('input',i));self.send(key)
   for at,n in [(1.7,'options_open'),(5.5,'configured'),(6.5,'back'),(7.6,'start_inverted'),(8.5,'inverted_x'),(9.5,'inverted_y'),(10.5,'start_default'),(11.5,'default_x'),(12.5,'default_y')]:
    if t>=at and n not in self.done:
     self.done.add(n)
     if n in ['start_inverted','start_default']:
      if n=='start_default':self.pc.call_method('K02ResetComfortPreferences')
      self.pc.set_control_rotation(unreal.Rotator(pitch=0,yaw=0,roll=0))
     s=self.snapshot(n)
     if n=='options_open':self.checks[n]=s['paused'] and s['K02ComfortOpen']
     if n=='configured':self.checks[n]=s['K02SensitivityX']==1.25 and s['K02SensitivityY']==1.25 and s['K02InvertX'] and s['K02InvertY'] and s['K02LookScaleX']==-1.25 and s['K02LookScaleY']==-1.25 and s['K02PreferencesSaved']
     if n=='back':self.checks[n]=s['paused'] and not s['K02ComfortOpen'] and s['K02TrainingMenuOpen']
   if t>13:
    r={x['stage']:x for x in self.rows};ix=r['inverted_x']['yaw'];iy=r['inverted_y']['pitch'];dx=r['default_x']['yaw'];dy=r['default_y']['pitch'];self.checks['mouse_x']=abs(dx)>.1 and abs(ix/dx+1.25)<.03;self.checks['mouse_y']=abs(dy)>.1 and abs(iy/dy+1.25)<.03
    self.checks['reset']=r['default_y']['K02SensitivityX']==1 and r['default_y']['K02SensitivityY']==1 and not r['default_y']['K02InvertX'] and not r['default_y']['K02InvertY']
    self.pc.call_method('K02ShowTrainingMenu');self.finish()
  except Exception:self.finish(traceback.format_exc())
 def finish(self,error=None):
  unreal.unregister_slate_post_tick_callback(self.handle);jobs=[]
  for name in self.jobs:
   f=Q/(name+'.result.json');jobs.append(json.loads(f.read_text(encoding='utf-8-sig')) if f.exists() else {'id':name,'ok':False,'error':'No result'})
  r={'error':error,'checks':self.checks,'native_inputs':jobs,'rows':self.rows,'pass':not error and len(self.checks)==6 and all(self.checks.values()) and all(x['ok'] for x in jobs)};(D/'comfort-preferences-validation.json').write_text(json.dumps(r,indent=2));unreal.log('K02_COMFORT_PREFERENCES_TEST '+str(r['pass']))
test=Test()
