"""Disposable PIE measurement: contact proxies, stop/reversal response, no saved actor edits."""
import unreal,json,math,traceback
from pathlib import Path
D=Path('A:/K-02 5.8/Saved/Diagnostics/Locomotion');D.mkdir(parents=True,exist_ok=True)
class LocomotionMeasure:
 def __init__(self):
  self.w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();assert self.w
  self.p=unreal.GameplayStatics.get_player_pawn(self.w,0);self.pc=unreal.GameplayStatics.get_player_controller(self.w,0);self.m=self.p.character_movement
  self.ai=[]
  for a in unreal.GameplayStatics.get_all_actors_of_class(self.w,unreal.Character):
   if a!=self.p:
    self.ai.append({'class':a.get_class().get_path_name(),'anim':a.mesh.get_editor_property('AnimClass').get_path_name(),'movement':json.loads(unreal.ToolsetLibrary.get_object_properties(a.character_movement,['MaxAcceleration','GroundFriction','BrakingDecelerationWalking','bRequestedMoveUseAcceleration','bUseControllerDesiredRotation','RotationRate']))});a.destroy_actor()
  self.settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));self.throttle=self.settings.get_editor_property('bThrottleCPUWhenNotForeground');self.settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
  self.oldcap=unreal.SystemLibrary.get_console_variable_float_value('t.MaxFPS');unreal.SystemLibrary.execute_console_command(self.w,'t.MaxFPS 60')
  self.original=self.p.get_actor_transform();self.oldspeed=self.m.max_walk_speed
  self.cases=[{'name':f'steady_{s}_{a}','speed':s,'angle':a} for s,a in [(40,0),(100,0),(210,0),(250,0),(250,45),(250,90),(250,180),(400,0),(550,0),(650,0)]]+ [{'name':'reverse','speed':250,'angle':0,'reverse':True},{'name':'turn_90','speed':250,'angle':0,'turn':True},{'name':'camera_turn','speed':250,'angle':0,'camera':True}]
  self.i=-1;self.rows=[];self.next();self.cb=unreal.register_slate_post_tick_callback(self.tick)
 def next(self):
  self.i+=1;self.t=0;self.samples=[]
  if self.i>=len(self.cases):self.finish();return
  self.case=self.cases[self.i];self.m.stop_movement_immediately();self.p.set_actor_location_and_rotation(unreal.Vector(-700,0,100),unreal.Rotator(pitch=0,yaw=0,roll=0),False,True);self.pc.set_control_rotation(unreal.Rotator(pitch=0,yaw=0,roll=0));self.m.max_walk_speed=self.case['speed']
 def tick(self,dt):
  try:
   dt=unreal.GameplayStatics.get_world_delta_seconds(self.w);self.t+=dt
   c=self.case;a=c['angle']
   if c.get('reverse') and self.t>=1.6:a=180
   if c.get('turn') and self.t>=1.6:a=90
   if c.get('camera') and self.t>=1.6:self.pc.set_control_rotation(unreal.Rotator(pitch=0,yaw=90,roll=0))
   if .4<self.t<3.0:self.p.add_movement_input(unreal.Vector(math.cos(math.radians(a)),math.sin(math.radians(a)),0),1,True)
   anim=self.p.mesh.get_anim_instance();feet={b:self.p.mesh.get_socket_location(b).to_tuple() for b in ['foot_l','foot_r','pelvis','root']}
   self.samples.append({'t':self.t,'dt':dt,'position':self.p.get_actor_location().to_tuple(),'velocity':self.p.get_velocity().to_tuple(),'yaw':self.p.get_actor_rotation().yaw,'feet':feet,'body':{b:{'p':self.p.mesh.get_socket_location(b).to_tuple(),'r':self.p.mesh.get_socket_rotation(b).to_tuple()} for b in ['spine_03','spine_05','hand_l','hand_r']},'anim':json.loads(unreal.ToolsetLibrary.get_object_properties(anim,['GroundSpeed','ShouldMove','Direction']))})
   if self.t>=3.8:
    self.rows.append({'case':c,'samples':self.samples});self.next()
  except Exception:self.finish(traceback.format_exc())
 def finish(self,error=None):
  if hasattr(self,'cb'):unreal.unregister_slate_post_tick_callback(self.cb)
  self.settings.set_editor_property('bThrottleCPUWhenNotForeground',self.throttle);self.m.max_walk_speed=self.oldspeed;self.p.set_actor_transform(self.original,False,True);unreal.SystemLibrary.execute_console_command(self.w,'t.MaxFPS '+str(self.oldcap))
  phase=(D/'phase.txt').read_text().strip();r={'phase':phase,'ai':self.ai,'rows':self.rows,'error':error}
  (D/('runtime-'+phase+'.json')).write_text(json.dumps(r));unreal.log('K02_LOCOMOTION_MEASURE_DONE '+phase+' '+str(len(self.rows))+' error='+str(error))
k02_measure=LocomotionMeasure()
