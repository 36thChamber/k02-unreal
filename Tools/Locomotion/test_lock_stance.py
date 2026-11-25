import unreal,json,traceback
from pathlib import Path
class Test:
 def __init__(self):
  self.w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();assert self.w
  self.p=unreal.GameplayStatics.get_player_pawn(self.w,0);self.pc=unreal.GameplayStatics.get_player_controller(self.w,0);self.m=self.p.character_movement
  self.commun=next(o for o in unreal.ObjectIterator(unreal.AnimInstance) if o.get_outer()==self.p.mesh and o.get_class().get_name()=='ABP_K02_Commun_C')
  self.target=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(self.w,unreal.Character) if a.get_class().get_name()=='BP_K02_TrainingDummy_C')
  for a in unreal.GameplayStatics.get_all_actors_of_class(self.w,unreal.Character):
   if a not in [self.p,self.target]:a.destroy_actor()
  self.perf=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));self.old=self.perf.get_editor_property('bThrottleCPUWhenNotForeground');self.perf.set_editor_property('bThrottleCPUWhenNotForeground',False)
  self.cap=unreal.SystemLibrary.get_console_variable_float_value('t.MaxFPS');unreal.SystemLibrary.execute_console_command(self.w,'t.MaxFPS 60')
  self.lib=unreal.get_default_object(unreal.load_class(None,'/Script/GameplayAbilities.AbilitySystemBlueprintLibrary'));self.asc=self.lib.call_method('GetAbilitySystemComponent',args=(self.p,));self.guard=unreal.load_class(None,'/Game/K02/Protagonist/Abilities/GA_K02_DefenseMode.GA_K02_DefenseMode_C');self.rows=[];self.i=-1;self.next();self.cb=unreal.register_slate_post_tick_callback(self.tick)
 def set(self,o,v):assert unreal.ToolsetLibrary.set_object_properties(o,json.dumps(v))
 def prop(self,o,keys):return json.loads(unreal.ToolsetLibrary.get_object_properties(o,keys))
 def next(self):
  self.i+=1;self.t=0
  if self.i>=5:self.finish();return
  self.lock=self.i in [1,2,4];self.p.set_actor_location_and_rotation(unreal.Vector(-700,0,100),unreal.Rotator(),False,True);self.target.set_actor_location(unreal.Vector(100,0,100),False,True);self.pc.set_control_rotation(unreal.Rotator());self.m.stop_movement_immediately()

  desired=1 if self.lock else 0
  for _ in range(4):
   if self.prop(self.pc,['LockonMode'])['LockonMode']==desired:break
   self.pc.call_method('LockOnTargetMode')
  self.row={'initialMaxWalkSpeed':self.m.max_walk_speed,'lock':self.lock,'case':self.i,'samples':[]};self.rows.append(self.row)
 def tick(self,dt):
  try:
   self.t+=unreal.GameplayStatics.get_world_delta_seconds(self.w)
   if self.i==4 and self.t>.8 and 'unlocked' not in self.row:
    self.pc.call_method('LockOnTargetMode')
    self.row['unlocked']=self.t
   if self.t<1:self.p.add_movement_input(unreal.Vector(.707,.707,0),1,True)
   if self.t>.5 and 'activated' not in self.row:self.row['activated']=bool(self.asc.try_activate_ability_by_class(self.guard,True))
   m=self.p.mesh.get_anim_instance().get_current_active_montage()
   self.row['samples'].append({'t':self.t,'yaw':self.p.get_actor_rotation().yaw,'combatStance':self.commun.get_editor_property('K02CombatStance'),'flags':self.prop(self.m,['bOrientRotationToMovement','bUseControllerDesiredRotation']),'montage':m.get_name() if m else None})
   if self.t>1.2:
    self.row['speedRestored']=self.i in [1,2] or abs(self.m.max_walk_speed-self.row['initialMaxWalkSpeed'])<.01
    last=self.row['samples'][-1];guarded=any(bool(x['montage'] and x['montage'].startswith('AM_K02_Guard_')) for x in self.row['samples']);expected=self.i in [1,2];self.row['pass']=(self.row['speedRestored'] and last['combatStance']==expected and guarded==self.lock and bool(last['montage'] and last['montage'].startswith('AM_K02_Guard_'))==expected and last['flags']['bOrientRotationToMovement']==(not expected))
    self.lib.call_method('SendGameplayEventToActor',args=(self.p,unreal.get_default_object(self.guard).get_editor_property('EventEndAbility'),unreal.GameplayEventData()));self.next()
  except Exception:self.finish(traceback.format_exc())
 def finish(self,error=None):
  if hasattr(self,'cb'):unreal.unregister_slate_post_tick_callback(self.cb)
  self.perf.set_editor_property('bThrottleCPUWhenNotForeground',self.old);unreal.SystemLibrary.execute_console_command(self.w,'t.MaxFPS '+str(self.cap));Path('A:/K-02 5.8/Saved/Diagnostics/LockRecovery/stance-test.json').write_text(json.dumps({'pass':not error and len(self.rows)==5 and all(r.get('pass',False) for r in self.rows),'error':error,'rows':self.rows},indent=2));unreal.log('K02_STANCE_TEST_DONE '+str(error))
k02_lock_test=Test()
