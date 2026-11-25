import unreal,json
from pathlib import Path
W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();assert W
r={}
for a in unreal.GameplayStatics.get_all_actors_of_class(W,unreal.SkeletalMeshActor):
 if a.get_actor_label() not in ['Manny_Source','B_1_Stance','B_1_BindPose']:continue
 row={'location':a.get_actor_location().to_tuple(),'components':[]}
 for c in a.get_components_by_class(unreal.SkeletalMeshComponent):
  x={'name':c.get_name(),'parent':str(c.get_attach_parent()),'mesh':str(c.get_skinned_asset()),'anim':str(c.get_anim_instance()),'transform':str(c.get_world_transform()),'visible':c.is_visible(),'bounds':str(unreal.SystemLibrary.get_component_bounds(c)),'bones':{str(b):c.get_socket_location(b).to_tuple() for b in ['root','pelvis','head','hand_l','foot_l']}}
  row['components'].append(x)
 r[a.get_actor_label()]=row
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/lab-runtime-state.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r,indent=2))
