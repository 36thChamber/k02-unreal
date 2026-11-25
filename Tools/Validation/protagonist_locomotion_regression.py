import unreal,json,math,traceback
from pathlib import Path
class K02LocomotionTest:
 def __init__(self):
  self.w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();assert self.w
  self.p=unreal.GameplayStatics.get_player_pawn(self.w,0);self.pc=unreal.GameplayStatics.get_player_controller(self.w,0)
  for a in unreal.GameplayStatics.get_all_actors_of_class(self.w,unreal.Character):
   if a!=self.p:a.destroy_actor()
  self.settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));self.old=self.settings.get_editor_property('bThrottleCPUWhenNotForeground');self.settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
  self.original=self.p.get_actor_transform();self.old_speed=self.p.character_movement.max_walk_speed
  self.cases=[(speed,d) for speed in [250,650] for d in [0,45,90,135,180,-135,-90,-45]];self.i=-1;self.t=0;self.rows=[];self.next()
  self.cb=unreal.register_slate_post_tick_callback(self.tick)
 def next(self):
  self.i+=1;self.t=0;self.samples=[]
  if self.i>=len(self.cases):self.finish();return
  self.speed,self.d=self.cases[self.i];self.p.character_movement.stop_movement_immediately();self.p.set_actor_location_and_rotation(unreal.Vector(0,0,100),unreal.Rotator(pitch=0,yaw=0,roll=0),False,True)
  self.pc.set_control_rotation(unreal.Rotator(pitch=0,yaw=0,roll=0));self.p.character_movement.max_walk_speed=self.speed
  self.vec=unreal.Vector(math.cos(math.radians(self.d)),math.sin(math.radians(self.d)),0)
 def tick(self,dt):
  try:
   self.t+=dt
   if self.t<1.1:self.p.add_movement_input(self.vec,1,True)
   root=self.p.mesh.get_socket_location('root');loc=self.p.get_actor_location();off=math.hypot(root.x-loc.x,root.y-loc.y)
   if .3<self.t<1.0:self.samples.append({'speed':self.p.get_velocity().length(),'rootXYOffset':off,'rootZ':root.z,'yaw':self.p.get_actor_rotation().yaw})
   if self.t>1.5:
    row={'commandSpeed':self.speed,'direction':self.d,'maxRootOffset':max(x['rootXYOffset'] for x in self.samples),'meanSpeed':sum(x['speed'] for x in self.samples)/len(self.samples),'endSpeed':self.p.get_velocity().length(),'sampleCount':len(self.samples)}
    row['pass']=row['maxRootOffset']<3 and abs(row['meanSpeed']-self.speed)<25 and row['endSpeed']<1
    self.rows.append(row);self.next()
  except Exception:self.finish(traceback.format_exc())
 def finish(self,error=None):
  if hasattr(self,'cb'):unreal.unregister_slate_post_tick_callback(self.cb)
  self.settings.set_editor_property('bThrottleCPUWhenNotForeground',self.old);self.p.character_movement.max_walk_speed=self.old_speed;self.p.set_actor_transform(self.original,False,True)
  r={'cases':self.rows,'error':error,'pass':len(self.rows)==16 and all(x['pass'] for x in self.rows) and error is None}
  Path('A:/K-02 5.8/Saved/Diagnostics/protagonist-locomotion-regression.json').write_text(json.dumps(r,indent=2));unreal.log('K02_LOCOMOTION_TEST '+json.dumps(r))
k02_locomotion_test=K02LocomotionTest()
