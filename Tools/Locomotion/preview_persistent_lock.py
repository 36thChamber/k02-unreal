"""PIE framing/facing/persistence assertions, native projection of target capsule bounds."""
import unreal,json,math,traceback
from pathlib import Path
D=Path('A:/K-02 5.8/Saved/Diagnostics/PersistentLock')
class LockTest:
 def __init__(self):
  self.w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();assert self.w
  self.p=unreal.GameplayStatics.get_player_pawn(self.w,0);self.pc=unreal.GameplayStatics.get_player_controller(self.w,0);self.target=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(self.w,unreal.Character) if a.get_class().get_name()=='BP_K02_TrainingDummy_C')
  for a in unreal.GameplayStatics.get_all_actors_of_class(self.w,unreal.Character):
   if a not in [self.p,self.target]:a.destroy_actor()
  self.arm=self.p.get_components_by_class(unreal.SpringArmComponent)[0];self.orig={'arm':self.arm.target_arm_length,'socket':self.arm.socket_offset.to_tuple(),'offset':self.arm.target_offset.to_tuple(),'look':self.pc.is_look_input_ignored()};self.rows=[];self.i=-1
  self.perf=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));self.old=self.perf.get_editor_property('bThrottleCPUWhenNotForeground');self.perf.set_editor_property('bThrottleCPUWhenNotForeground',False);self.cap=unreal.SystemLibrary.get_console_variable_float_value('t.MaxFPS');unreal.SystemLibrary.execute_console_command(self.w,'t.MaxFPS '+str(int((D/'test-fps.txt').read_text()) if (D/'test-fps.txt').exists() else 60))
  self.p.set_actor_location_and_rotation(unreal.Vector(0,0,92),unreal.Rotator(),False,True);self.target.set_actor_location(unreal.Vector(500,0,92),False,True);self.pc.set_control_rotation(unreal.Rotator());self.pc.call_method('LockOnTargetMode')
  self.cases=['front_close','right_close','target_circle','far_beyond_acquisition'];self.next();self.cb=unreal.register_slate_post_tick_callback(self.tick)
 def next(self):
  self.i+=1;self.t=0
  if self.i>=len(self.cases):self.finish();return
  self.name=self.cases[self.i];self.row={'case':self.name,'samples':[]};self.rows.append(self.row)
  self.p.character_movement.stop_movement_immediately();self.p.set_actor_location(unreal.Vector(0,0,92),False,True)
  if self.name=='release':self.pc.call_method('LockOnTargetMode')
  if self.name=='look_stack':self.pc.set_ignore_look_input(True);self.pc.call_method('LockOnTargetMode')
  if self.name=='target_destroyed':self.pc.set_ignore_look_input(False);self.pc.call_method('LockOnTargetMode');self.target.destroy_actor()
 def tick(self,dt):
  try:
   self.t+=unreal.GameplayStatics.get_world_delta_seconds(self.w);n=self.name
   pos={'front_close':(100,0,92),'right_close':(0,100,92),'behind_close':(-100,0,92),'far_beyond_acquisition':(1300,0,92),'target_above':(300,0,442),'target_below':(500,0,-108)}.get(n,(500,0,92))
   if n=='target_circle':pos=(150*math.cos(self.t*3),150*math.sin(self.t*3),92)
   if n!='target_destroyed':self.target.character_movement.stop_movement_immediately();self.target.set_actor_location(unreal.Vector(*pos),False,True)
   if n=='look_input':self.pc.add_yaw_input(100);self.pc.add_pitch_input(100)
   if n=='player_strafe' and self.t<1:self.p.add_movement_input(unreal.Vector(0,1,0),1,True)
   if n=='look_stack' and self.t>.6 and 'released' not in self.row:self.pc.call_method('LockOnTargetMode');self.row['released']=True
   if self.t>.25:
    sample={'t':self.t,'mode':self.pc.get_editor_property('LockonMode'),'ignored':self.pc.is_look_input_ignored(),'camera':self.pc.player_camera_manager.get_camera_location().to_tuple()}
    if n not in ['release','look_stack','target_destroyed']:
     delta=self.target.get_actor_location()-self.p.get_actor_location();expected=math.degrees(math.atan2(delta.y,delta.x));sample['yawError']=abs((expected-self.p.get_actor_rotation().yaw+180)%360-180);sample['sameTarget']=self.pc.get_editor_property('CurrentTarget')==self.target
     origin,extent=self.target.get_actor_bounds(True,False);width,height=self.pc.get_viewport_size();points=[]
     for x in [-extent.x,extent.x]:
      for y in [-extent.y,extent.y]:
       for z in [-extent.z,extent.z]:
        screen=unreal.GameplayStatics.project_world_to_screen(self.pc,origin+unreal.Vector(x,y,z),True);points.append(None if screen is None else (screen.x/width,screen.y/height))
     sample['bounds']=points;sample['framed']=all(p and .025<=p[0]<=.975 and .025<=p[1]<=.975 for p in points)
    self.row['samples'].append(sample)
   if self.t>.75 and 'captured' not in self.row:
    self.row['captured']=True;unreal.SystemLibrary.execute_console_command(self.w,'HighResShot 1280x720 filename="'+str(D/('camera-'+n+'.png'))+'"',self.pc)
   if self.t>1.5:
    last=self.row['samples'][-1]
    if n in ['release','target_destroyed']:self.row['pass']=last['mode']==0 and not last['ignored'] and abs(self.arm.target_arm_length-self.orig['arm'])<.01 and self.arm.socket_offset.to_tuple()==self.orig['socket'] and self.arm.target_offset.to_tuple()==self.orig['offset']
    elif n=='look_stack':self.row['pass']=last['mode']==0 and last['ignored']
    else:self.row['pass']=all(s['mode']>0 and s['sameTarget'] and s['framed'] and s['yawError']<(7 if n=='target_circle' else (3 if n=='player_strafe' else 1)) for s in self.row['samples'])
    self.next()
  except Exception:self.finish(traceback.format_exc())
 def finish(self,error=None):
  if hasattr(self,'cb'):unreal.unregister_slate_post_tick_callback(self.cb)
  self.perf.set_editor_property('bThrottleCPUWhenNotForeground',self.old);unreal.SystemLibrary.execute_console_command(self.w,'t.MaxFPS '+str(self.cap));r={'visualOnly':True,'error':error,'original':self.orig,'rows':self.rows};(D/'framing-preview.json').write_text(json.dumps(r,indent=2));unreal.log('K02_PERSISTENT_LOCK_PREVIEW_DONE '+str(error))
k02_persistent_lock_preview=LockTest()
