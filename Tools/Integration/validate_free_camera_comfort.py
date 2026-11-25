"""Geometry/state checks of free fallback and lock round trip; controlled live PIE."""
import unreal,json,traceback,math
from pathlib import Path
D=Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration';W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();assert W
params=globals().get('REQUEST',{}).get('params',{})
class Test:
 def __init__(self):
  self.p=unreal.GameplayStatics.get_player_pawn(W,0);self.pc=unreal.GameplayStatics.get_player_controller(W,0);self.arm=self.p.get_components_by_class(unreal.SpringArmComponent)[0];self.cam=self.p.get_components_by_class(unreal.CameraComponent)[0];self.body=next(c for c in self.p.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name()=='K02Body');self.rows=[];self.i=-1;self.t=0;self.busy=False
  if 'fov' in params:
   for key,target,count in [('CameraFOV',float(params['fov']),5),('CameraDistance',float(params['distance']),4)]:
    for _ in range(count):
     if self.pc.get_editor_property('K02'+key)==target:break
     self.pc.call_method('K02Cycle'+key)
    assert self.pc.get_editor_property('K02'+key)==target
   self.pc.call_method('K02ApplyComfortPreferences')
  self.target=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(W,unreal.Character) if a.get_class().get_name()=='BP_K02_TrainingDummy_C')
  for a in unreal.GameplayStatics.get_all_actors_of_class(W,unreal.Character):
   a.character_movement.stop_movement_immediately();a.character_movement.set_movement_mode(unreal.MovementMode.MOVE_NONE)
   if a!=self.p:
    c=a.get_controller();c.stop_movement();brain=c.get_editor_property('BrainComponent')
    if brain:brain.stop_logic('Free camera validation')
    a.set_actor_location(unreal.Vector(5000,5000,92),False,True)
  self.perf=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));self.old=self.perf.get_editor_property('bThrottleCPUWhenNotForeground');self.perf.set_editor_property('bThrottleCPUWhenNotForeground',False)
  self.next();self.handle=unreal.register_slate_post_tick_callback(self.tick)
 def next(self):
  self.i+=1
  if self.i==len(self.cases):self.finish();return
  n,pos,pitch,yaw,locked=self.cases[self.i];self.row={'case':n,'samples':[]};self.rows.append(self.row);self.t=0
  if self.pc.get_editor_property('LockonMode')!=0:self.pc.call_method('LockOnTargetMode')
  self.p.set_actor_location_and_rotation(unreal.Vector(*pos),unreal.Rotator(yaw=yaw),False,True);self.pc.set_control_rotation(unreal.Rotator(pitch=pitch,yaw=yaw))
  self.target.set_actor_location(unreal.Vector(pos[0]+150,pos[1],pos[2]),False,True)
  if locked:self.pc.call_method('LockOnTargetMode')
 def tick(self,dt):
  if self.busy:return
  self.busy=True
  try:
   self.t+=unreal.GameplayStatics.get_world_delta_seconds(W)
   if self.t>1.5:
    c=self.pc.player_camera_manager.get_camera_location();rot=self.pc.get_control_rotation();head=self.body.get_socket_location('head');pelvis=self.body.get_socket_location('pelvis');w,h=self.pc.get_viewport_size()
    projected={}
    for n,pt in [('head',head),('pelvis',pelvis),('near_target_head',self.target.mesh.get_socket_location('head'))]:
     v=unreal.GameplayStatics.project_world_to_screen(self.pc,pt,True);projected[n]=[v.x/w,v.y/h] if v else None
    self.row['samples'].append({'camera':c.to_tuple(),'fov':self.cam.field_of_view,'arm':self.arm.target_arm_length,'distance_from_head':c.distance(head),'distance_from_actor':c.distance(self.p.get_actor_location()),'alpha':self.pc.get_editor_property('K02FreeCameraAlpha'),'offset':self.arm.target_offset.to_tuple(),'control_pitch':rot.pitch,'control_yaw':rot.yaw,'camera_relative_pitch':self.cam.get_editor_property('relative_rotation').pitch,'locked':self.pc.get_editor_property('K02CameraLocked'),'ignore_look':self.pc.is_look_input_ignored(),'projected':projected})
   if self.t>2:
    n,pos,pitch,yaw,locked=self.cases[self.i];samples=self.row['samples']
    self.row['pass']=bool(samples) and all(s['distance_from_head']>60 and s['distance_from_actor']>100 and all(v and .02<v[0]<.98 and .02<v[1]<.98 for v in s['projected'].values()) and (locked or (abs(s['control_pitch']-pitch)<.01 and abs(s['control_yaw']-yaw)<.01 and not s['ignore_look'])) for s in samples)
    if n.startswith('open'):self.row['pass']=self.row['pass'] and all(s['alpha']<.01 and abs(s['camera_relative_pitch'])<.1 and abs(s['offset'][2])<1 and ('distance' not in params or abs(s['arm']-float(params['distance']))<.01) for s in samples)
    self.next()
  except Exception:self.finish(traceback.format_exc())
  finally:self.busy=False
 def finish(self,error=None):
  if hasattr(self,'handle'):unreal.unregister_slate_post_tick_callback(self.handle)
  self.perf.set_editor_property('bThrottleCPUWhenNotForeground',self.old)
  r={'error':error,'pass':not error and all(x.get('pass',False) for x in self.rows),'rows':self.rows,'scope':'Controlled PIE geometry and controller-state checks, not human comfort approval'};(D/(params.get('output','free-camera-validation')+'.json')).write_text(json.dumps(r,indent=2));unreal.log('K02_FREE_CAMERA_TEST '+str(r['pass']))
 cases=[('open_start',(0,0,92),0,0,False),('wall',(-1465,0,92),0,0,False),('corner',(-1465,-1165,92),0,0,False),('wall_look_down',(-1465,0,92),-35,0,False),('wall_look_up',(-1465,0,92),35,0,False),('lock_from_wall',(-1465,0,92),0,0,True),('open_after_lock',(0,0,92),0,0,False),('wall_final',(-1465,-1165,92),0,0,False)]
test=Test()
