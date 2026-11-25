"""Wall-clock native input test: initial pause, resume, held guard, navigation/restart."""
import unreal,json,time,datetime,uuid,traceback
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());D=ROOT/'Saved/Diagnostics/Integration';Q=ROOT/'Saved/NativeInputBridge';W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();assert W
class Test:
 def __init__(self):
  assert time.time()-Q.joinpath('heartbeat.txt').stat().st_mtime<2,'Native worker expired'
  self.pc=unreal.GameplayStatics.get_player_controller(W,0);self.p=unreal.GameplayStatics.get_player_pawn(W,0);self.inspector=unreal.get_default_object(unreal.load_class(None,'/Script/GASToolsets.AbilitySystemInspectorToolset'));self.start=time.monotonic();self.done=set();self.rows=[];self.jobs=[];self.checks={};self.before=self.snapshot();self.guard_time=0
  for a in unreal.GameplayStatics.get_all_actors_of_class(W,unreal.Character):
   if a!=self.p:
    c=a.get_controller();c.stop_movement();brain=c.get_editor_property('BrainComponent')
    if brain:brain.stop_logic('Menu/input isolation')
  self.handle=unreal.register_slate_post_tick_callback(self.tick)
 def send(self,key):
  name=str(time.time_ns())+'-'+uuid.uuid4().hex[:6];f=Q/(name+'.tmp');f.write_text(json.dumps({'id':name,'key':key,'created':datetime.datetime.now(datetime.timezone.utc).isoformat()}));f.rename(Q/(name+'.pending.json'));self.jobs.append(name)
 def snapshot(self):
  w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();pc=unreal.GameplayStatics.get_player_controller(w,0);p=unreal.GameplayStatics.get_player_pawn(w,0);m=pc.get_editor_property('K02TrainingMenu');a=p.mesh.get_anim_instance().get_current_active_montage();tags=list(self.inspector.call_method('GetActiveTags',args=(p,)))
  return {'wall':time.monotonic()-self.start,'world_time':unreal.GameplayStatics.get_time_seconds(w),'paused':unreal.GameplayStatics.is_game_paused(w),'menu_open':pc.get_editor_property('K02TrainingMenuOpen'),'menu_in_viewport':m.is_in_viewport() if m else False,'focus_resume':m.get_editor_property('Resume').has_keyboard_focus() if m else False,'health':{v.attribute_name:v.current_value for v in self.inspector.call_method('GetAttributeValues',args=(p,)) if v.attribute_name in ['Health','Shield','Resource']},'tags':tags,'montage':a.get_name() if a else None,'pawn':p.get_path_name(),'new_pawn':p!=self.p}
 def tick(self,dt):
  try:
   t=time.monotonic()-self.start
   actions=[(1,'EnterDown'),(1.08,'EnterUp'),(3,'CtrlDown'),(4.2,'CtrlUp'),(5,'PDown'),(5.08,'PUp'),(6,'EnterDown'),(6.08,'EnterUp'),(8.3,'ArrowDownDown'),(8.4,'ArrowDownUp'),(8.6,'EnterDown'),(8.68,'EnterUp')]
   for i,(at,key) in enumerate(actions):
    if t>=at and ('input',i) not in self.done:self.done.add(('input',i));self.send(key)
   for at,n in [(0.8,'startup'),(2,'resumed'),(3.8,'guard'),(5.7,'paused_guard'),(7.2,'resumed_guard'),(9.7,'restarted')]:
    if t>=at and n not in self.done:
     self.done.add(n);s=self.snapshot();s['stage']=n;self.rows.append(s)
     if n=='startup':self.checks[n]=s['paused'] and s['menu_open'] and s['focus_resume'] and abs(s['world_time']-self.before['world_time'])<.001 and s['health']==self.before['health']
     if n=='resumed':self.checks[n]=not s['paused'] and not s['menu_in_viewport'] and s['world_time']>self.before['world_time']+.3 and s['montage'] is None
     if n=='guard':self.checks[n]=any('Fighter.DefenseMode' in x for x in s['tags'])
     if n=='paused_guard':self.checks[n]=s['paused'] and s['menu_open'] and abs(s['world_time']-self.guard_time)<.001 and s['health']==self.guard_health
     if n=='resumed_guard':self.checks[n]=not s['paused'] and not any('Fighter.DefenseMode' in x or 'Fighter.Combo' in x for x in s['tags']) and s['montage'] is None
     if n=='restarted':self.checks[n]=s['new_pawn'] and s['paused'] and s['menu_open'] and s['health']['Health']==100
   for at,n in [(4,'show_guard'),(8,'show_restart')]:
    if t>=at and n not in self.done:
     self.done.add(n);self.pc.call_method('K02ShowTrainingMenu');s=self.snapshot();self.guard_time=s['world_time'];self.guard_health=s['health']
   if t>10:self.finish()
  except Exception:self.finish(traceback.format_exc())
 def finish(self,error=None):
  unreal.unregister_slate_post_tick_callback(self.handle);jobs=[]
  for name in self.jobs:
   f=Q/(name+'.result.json');jobs.append(json.loads(f.read_text(encoding='utf-8-sig')) if f.exists() else {'id':name,'ok':False,'error':'No result'})
  r={'error':error,'checks':self.checks,'native_inputs':jobs,'rows':self.rows,'pass':not error and len(self.checks)==6 and all(self.checks.values()) and all(x['ok'] for x in jobs)};(D/'training-menu-validation.json').write_text(json.dumps(r,indent=2));unreal.log('K02_TRAINING_MENU_TEST '+str(r['pass']))
test=Test()
