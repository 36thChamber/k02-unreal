import unreal,json
from pathlib import Path
W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();assert W
p=unreal.GameplayStatics.get_player_pawn(W,0);assert p
r={'pawn':p.get_path_name(),'capsule_half_height':p.capsule_component.get_scaled_capsule_half_height(),'position':p.get_actor_location().to_tuple(),'components':[]}
for c in p.get_components_by_class(unreal.SkeletalMeshComponent):
 r['components'].append({'name':c.get_name(),'parent':str(c.get_attach_parent()),'mesh':str(c.get_skinned_asset()),'visible':c.is_visible(),'hidden':c.get_editor_property('hidden_in_game'),'collision':str(c.get_collision_enabled()),'leader':str(c.leader_pose_component),'anim':str(c.get_anim_instance()),'transform':str(c.get_world_transform()),'bones':{b:c.get_socket_location(b).to_tuple() for b in ['root','pelvis','head','hand_l','foot_l']}})
trace=next(c for c in p.get_components_by_class(unreal.ActorComponent) if c.get_name()=='UnarmedTrace')
for key in ['LocalMeshesRef','TracePointsRef','SocketNames']:r[key]=[str(v) for v in trace.get_editor_property(key)]
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/arena-presentation.json').write_text(json.dumps(r,indent=2));print(r)
