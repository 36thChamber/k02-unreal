"""Both combatants must stay visible at the live-reported wall position."""
import unreal,json,traceback,math
from pathlib import Path
D=Path('A:/K-02 5.8/Saved/Diagnostics/LiveCamera')
class CameraTest:
 def __init__(self):
  self.w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();self.pc=unreal.GameplayStatics.get_player_controller(self.w,0);self.p=unreal.GameplayStatics.get_player_pawn(self.w,0)
  cs=unreal.GameplayStatics.get_all_actors_of_class(self.w,unreal.Character);self.target=next(a for a in cs if a.get_class().get_name()=='BP_K02_TrainingDummy_C');self.enemy=next(a for a in cs if a.get_class().get_name()=='BP_K02_Enemy_C')
  for a in cs:
   if a==self.p:continue
   c=a.get_controller();c.stop_movement();brain=c.get_editor_property('BrainComponent')
   if brain:brain.stop_logic('Camera regression')
  self.perf=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));self.throttle=self.perf.get_editor_property('bThrottleCPUWhenNotForeground');self.perf.set_editor_property('bThrottleCPUWhenNotForeground',False);self.busy=False
  for a in [self.p,self.target,self.enemy]:a.character_movement.set_movement_mode(unreal.MovementMode.MOVE_NONE)
  self.arm=self.p.get_components_by_class(unreal.SpringArmComponent)[0];self.orig=(self.arm.target_arm_length,self.arm.target_offset.to_tuple(),self.arm.socket_offset.to_tuple());self.rows=[];self.i=-1;self.start=0;self.next();self.cb=unreal.register_slate_post_tick_callback(self.tick)
 def next(self):
  self.i+=1
  if self.i>=len(self.cases):self.finish();return
  self.name,pp,tp=self.cases[self.i];self.row={'case':self.name,'samples':[]};self.rows.append(self.row);self.start=unreal.GameplayStatics.get_time_seconds(self.w)
  self.p.character_movement.stop_movement_immediately();self.p.set_actor_location(unreal.Vector(*pp),False,True);self.target.set_actor_location(unreal.Vector(*tp),False,True);self.enemy.set_actor_location(unreal.Vector(5000,5000,92),False,True)
  if self.pc.get_editor_property('LockonMode')==0:self.pc.call_method('LockOnTargetMode')
  self.pc.set_control_rotation(unreal.MathLibrary.find_look_at_rotation(self.p.get_actor_location(),self.target.get_actor_location()))
 def bounds(self,a):
  origin,ext=a.get_actor_bounds(True,False);width,height=self.pc.get_viewport_size();points=[]
  for x in [-ext.x,ext.x]:
   for y in [-ext.y,ext.y]:
    for z in [-ext.z,ext.z]:
     s=unreal.GameplayStatics.project_world_to_screen(self.pc,origin+unreal.Vector(x,y,z),True);points.append(None if s is None else (s.x/width,s.y/height))
  return {'visible':all(p and .015<p[0]<.985 and .015<p[1]<.985 for p in points),'points':points}
 def tick(self,dt):
  if self.busy:return
  self.busy=True
  try:
   t=unreal.GameplayStatics.get_time_seconds(self.w)-self.start
   pp,tp=self.cases[self.i][1:]
   self.target.set_actor_location(unreal.Vector(*tp),False,True)
   if 'above' in self.name or 'below' in self.name:self.p.set_actor_location(unreal.Vector(*pp),False,True)
   if t>.5:self.enemy.set_actor_location(unreal.Vector(pp[0]+50,pp[1]+85,pp[2]),False,True)
   if t>1.5:
    c=self.pc.player_camera_manager.get_camera_location();self.row['samples'].append({'t':t,'player':self.bounds(self.p),'target':self.bounds(self.target),'nearEnemy':self.bounds(self.enemy),'cameraDistance':c.distance(self.p.get_actor_location()),'orbit':self.pc.get_editor_property('K02CameraBestOrbit'),'ignored':self.pc.is_look_input_ignored(),'sameTarget':self.pc.get_editor_property('CurrentTarget')==self.target,'yawError':abs((unreal.MathLibrary.find_look_at_rotation(self.p.get_actor_location(),self.target.get_actor_location()).yaw-self.p.get_actor_rotation().yaw+180)%360-180)})
   if t>2.5:
    self.row['pass']=all(s['sameTarget'] and s['yawError']<3 and s['ignored'] and s['player']['visible'] and s['target']['visible'] and s['cameraDistance']>120 for s in self.row['samples'])
    self.next()
  except Exception:self.finish(traceback.format_exc())
  finally:self.busy=False
 def finish(self,error=None):
  if hasattr(self,'cb'):unreal.unregister_slate_post_tick_callback(self.cb)
  if self.pc.get_editor_property('LockonMode'):self.pc.call_method('LockOnTargetMode')
  self.perf.set_editor_property('bThrottleCPUWhenNotForeground',self.throttle)
  r={'pass':not error and all(r.get('pass',False) for r in self.rows),'error':error,'rows':self.rows,'originalCamera':self.orig};(D/'test.json').write_text(json.dumps(r,indent=2));unreal.log('K02_OBSTRUCTED_CAMERA_TEST '+str(r['pass']))
 cases=[('open_close',(0,0,92),(110,0,92)),('reported_wall',(-1465,-102,92),(-600,-500,92)),('wall_close',(-1465,0,92),(-1355,0,92)),('corner',(-1465,-1165,92),(-1200,-900,92)),('far',(0,0,92),(1300,0,92)),('target_above',(0,0,92),(300,0,442)),('target_below',(0,0,442),(500,0,92))]
k02_camera_test=CameraTest()
