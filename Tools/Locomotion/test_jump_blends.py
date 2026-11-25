import unreal,json,traceback
from pathlib import Path
class JumpTest:
 def __init__(self):
  self.w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();assert self.w;self.p=unreal.GameplayStatics.get_player_pawn(self.w,0);self.pc=unreal.GameplayStatics.get_player_controller(self.w,0);self.target=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(self.w,unreal.Character) if a.get_class().get_name()=='BP_K02_TrainingDummy_C')
  for a in unreal.GameplayStatics.get_all_actors_of_class(self.w,unreal.Character):
   if a not in [self.p,self.target]:a.destroy_actor()
  self.perf=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));self.old=self.perf.get_editor_property('bThrottleCPUWhenNotForeground');self.perf.set_editor_property('bThrottleCPUWhenNotForeground',False);self.cap=unreal.SystemLibrary.get_console_variable_float_value('t.MaxFPS');unreal.SystemLibrary.execute_console_command(self.w,'t.MaxFPS 60');self.cases=['idle_jump','moving_jump','lock_jump'];self.i=-1;self.rows=[];self.next();self.cb=unreal.register_slate_post_tick_callback(self.tick)
 def next(self):
  self.i+=1;self.t=0
  if self.i>=len(self.cases):self.finish();return
  self.name=self.cases[self.i];self.p.character_movement.stop_movement_immediately();self.p.character_movement.max_walk_speed=250;self.p.set_actor_location_and_rotation(unreal.Vector(-500,0,92),unreal.Rotator(),False,True);self.target.set_actor_location(unreal.Vector(300,0,92),False,True)
  desired=1 if self.name=='lock_jump' else 0
  if self.pc.get_editor_property('LockonMode')!=desired:self.pc.call_method('LockOnTargetMode')
  self.row={'case':self.name,'samples':[]};self.rows.append(self.row)
 def tick(self,dt):
  try:
   self.t+=unreal.GameplayStatics.get_world_delta_seconds(self.w)
   if self.name=='moving_jump' and .1<self.t<1.3:self.p.add_movement_input(unreal.Vector(1,0,0),1,True)
   if self.t>.35 and 'jumped' not in self.row:self.p.jump();self.row['jumped']=True
   if self.t>.5:self.p.stop_jumping()
   self.row['samples'].append({'t':self.t,'z':self.p.get_actor_location().z,'falling':self.p.character_movement.is_falling(),'footLocalZ':self.p.mesh.get_socket_location('foot_l').z-self.p.get_actor_location().z})
   if self.t>2.6:
    instances=[o.get_class().get_name() for o in unreal.ObjectIterator(unreal.AnimInstance) if o.get_outer()==self.p.mesh];self.row['linkedJump']='ABP_K02_Jump_C' in instances;self.row['pass']=self.row['linkedJump'] and any(s['falling'] for s in self.row['samples']) and not self.row['samples'][-1]['falling'] and max(s['z'] for s in self.row['samples'])>120 and max(s['footLocalZ'] for s in self.row['samples'])-min(s['footLocalZ'] for s in self.row['samples'])>10;self.next()
  except Exception:self.finish(traceback.format_exc())
 def finish(self,error=None):
  if hasattr(self,'cb'):unreal.unregister_slate_post_tick_callback(self.cb)
  self.perf.set_editor_property('bThrottleCPUWhenNotForeground',self.old);unreal.SystemLibrary.execute_console_command(self.w,'t.MaxFPS '+str(self.cap));r={'pass':not error and len(self.rows)==3 and all(x.get('pass') for x in self.rows),'error':error,'rows':self.rows};Path('A:/K-02 5.8/Saved/Diagnostics/TransitionBlends/jumps.json').write_text(json.dumps(r,indent=2));unreal.log('K02_JUMP_BLEND_TEST '+str(r['pass']))
k02_jump_blends=JumpTest()
