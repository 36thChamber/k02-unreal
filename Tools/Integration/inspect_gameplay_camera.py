import unreal,json
from pathlib import Path
W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();assert W
p=unreal.GameplayStatics.get_player_pawn(W,0);pc=unreal.GameplayStatics.get_player_controller(W,0);cam=pc.player_camera_manager
r={'pawn':p.get_path_name(),'location':p.get_actor_location().to_tuple(),'rotation':str(p.get_actor_rotation()),'control_rotation':str(pc.get_control_rotation()),'viewtarget':str(pc.get_view_target()),'camera_location':cam.get_camera_location().to_tuple(),'camera_rotation':str(cam.get_camera_rotation()),'fov':cam.get_fov_angle(),'components':[],'controller':{}}
for c in p.get_components_by_class(unreal.SceneComponent):
 d={'name':c.get_name(),'class':c.get_class().get_name(),'parent':str(c.get_attach_parent()),'transform':str(c.get_world_transform())}
 for k in ['target_arm_length','socket_offset','target_offset','do_collision_test','probe_channel','probe_size','camera_lag_speed','relative_location','use_pawn_control_rotation','field_of_view','is_active','collision_enabled','collision_responses']:
  try:d[k]=str(c.get_editor_property(k))
  except Exception:pass
 if isinstance(c,unreal.PrimitiveComponent):d['camera_response']=str(c.get_collision_response_to_channel(unreal.CollisionChannel.ECC_CAMERA))
 r['components'].append(d)
from editor_toolset.toolsets.blueprint import BlueprintTools as B
bp=unreal.load_asset('/Game/K02/Protagonist/Blueprints/BP_K02_PlayerController')
for n in B.list_variables(bp):
 if any(s in n.lower() for s in ['camera','lock','distance','offset']):
  try:r['controller'][n]=str(pc.get_editor_property(n))
  except Exception:pass
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/gameplay-camera.json').write_text(json.dumps(r,indent=2));print(r)
