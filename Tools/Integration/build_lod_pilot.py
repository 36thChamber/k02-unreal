"""Conservative LOD experiment on own copies; gameplay meshes and imported LOD0 stay intact."""
import unreal,json
from pathlib import Path
from editor_toolset.toolsets.skeletal_mesh import SkeletalMeshTools as S
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();folder='/Game/K02/Validation/LOD';preset=folder+'/LOD_K02_Conservative_v001'
assert not A.does_asset_exist(preset),'Pilot already exists: inspect it rather than overwriting'
f=unreal.DataAssetFactory();f.set_editor_property('data_asset_class',unreal.SkeletalMeshLODSettings.static_class());settings=T.create_asset('LOD_K02_Conservative_v001',folder,unreal.SkeletalMeshLODSettings.static_class(),f);assert settings
priority=['head','neck_01','hand_l','hand_r','foot_l','foot_r']+[n+'_'+str(i).zfill(2)+'_'+side for side in ['l','r'] for n in ['thumb','index','middle','ring','pinky'] for i in [1,2,3]]
groups=[]
for index,(ratio,screen,hyst) in enumerate([(1.,1.,.0),(.65,.25,.04),(.40,.12,.025)]):
 reduction=unreal.SkeletalMeshOptimizationSettings();reduction.set_editor_properties({'num_of_triangles_percentage':ratio,'num_of_vert_percentage':ratio,'base_lod':0,'lock_edges':True,'merge_coincident_vert_bones':True,'max_bones_per_vertex':8,'recalc_normals':False,'volume_importance':1.0})
 group=unreal.SkeletalMeshLODGroupSettings();group.set_editor_properties({'screen_size':unreal.PerPlatformFloat(default=screen),'lod_hysteresis':hyst,'reduction_settings':reduction,'bones_to_prioritize':priority if index else [],'weight_of_prioritization':5000.0 if index else 0.0,'bone_list':[]})
 groups.append(group)
settings.set_editor_property('lod_groups',groups);assert A.save_loaded_asset(settings,False)
sub=unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem);rows=[]
for source,name in [('SK_K02_BodyForDogi_v001','SK_K02_Body_LODPilot'),('SK_K02_Dogi_v002','SK_K02_Dogi_LODPilot')]:
 original=A.load_asset('/Game/K02/Characters/Protagonist/Dogi_v001/Meshes/'+source);assert original;destination=folder+'/'+name;assert not A.does_asset_exist(destination)
 mesh=A.duplicate_asset(original.get_path_name(),destination);assert mesh;before=S.get_vertex_count(original,0)
 mesh.set_editor_property('lod_settings',settings);assert sub.regenerate_lod(mesh,3,False,False);assert sub.get_lod_count(mesh)==3
 counts=[S.get_vertex_count(mesh,i) for i in range(3)];assert counts[0]==before and 0<counts[2]<=counts[1]<counts[0]
 assert A.save_loaded_asset(mesh,False);rows.append({'source':original.get_path_name(),'pilot':mesh.get_path_name(),'lod_vertices':counts,'source_lod0_vertices':before,'skeleton':mesh.get_editor_property('skeleton').get_path_name()})
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/lod-pilot-build.json').write_text(json.dumps({'preset':preset,'rows':rows,'scope':'New validation copies only. Visual, animation and runtime LOD selection validation pending.'},indent=2));print('LOD_PILOT_BUILT',rows)
