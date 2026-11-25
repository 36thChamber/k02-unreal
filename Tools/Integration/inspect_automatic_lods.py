import unreal,json
from pathlib import Path
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();pc=unreal.GameplayStatics.get_player_controller(w,0)
print('CAMERA',pc.get_view_target(),pc.player_camera_manager.get_camera_location(),pc.player_camera_manager.get_fov_angle())
for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Actor):
 if a.get_actor_label()!='B_3':continue
 for c in a.get_components_by_class(unreal.SkeletalMeshComponent):
  print(c.get_name(),'LOD',c.get_predicted_lod_level(),'sync',c.get_editor_property('sync_attach_parent_lod'),'parent',c.get_attach_parent(),'forced',c.get_forced_lod(),'location',c.get_socket_location('root'))
  print('properties',unreal.ToolsetLibrary.get_object_properties(c,['MinLodModel','MaxDistanceFactor','BoundsScale','MinDesiredLODLevel','bRecentlyRendered','bIgnoreLeaderPoseComponentLOD']))
  mesh=c.get_skinned_asset()
  try:
   for i,l in enumerate(mesh.get_editor_property('lod_info')):print('LODINFO',i,l.get_editor_property('screen_size'),l.get_editor_property('lod_hysteresis'))
  except Exception as e:print('LODINFO_ERROR',e)
