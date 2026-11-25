"""Small representative sequence gate, not a moveset expansion."""
import json
from pathlib import Path
import unreal
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
A=unreal.EditorAssetLibrary
BASE='/Game/K02/Validation/ImportProbeV3/B_1'
rt=unreal.load_asset(BASE+'/Rig/RTG_Manny_B_1')
c=unreal.IKRetargeterController.get_controller(rt)
pc=c.get_op_controller(0);pc.set_source_pelvis_bone('pelvis');pc.set_target_pelvis_bone('pelvis')
A.save_loaded_asset(rt,False)
ar=unreal.AssetRegistryHelpers.get_asset_registry()
assets=ar.get_assets_by_path('/Game',recursive=True)
names=['AS_MACS_Fighter_Idle','AS_K02_M01','AS_K02_M06','AS_K02_Slip_Left','A_Run_F_Manny','AS_K02_GetUp_Forward','AS_K02_Block_Idle']
selected=[]
for name in names:
    matches=[a for a in assets if str(a.asset_name)==name and str(a.asset_class_path.asset_name)=='AnimSequence']
    if matches:selected.append(matches[0])
assert len(selected)>=5,[str(a.asset_name) for a in selected]
inp=unreal.IKRetargetBatchOperationInputs()
for prop,val in {'assets_to_retarget':selected,'source_mesh':unreal.load_asset('/Game/MACS/Demo/ThirdPersonTemplateUE5/Characters/Mannequins/Meshes/SKM_Manny'),
 'target_mesh':unreal.load_asset(BASE+'/Meshes/SK_B_1_Combined_v009'),'ik_retarget_asset':rt,
 'target_path':BASE+'/Animations','suffix':'_B1_Pilot','include_referenced_assets':False,'overwrite_existing_files':True,'retain_additive_flags':True}.items():inp.set_editor_property(prop,val)
result=unreal.IKRetargetBatchOperation.run_batch_retarget(inp)
rows=[]
for src in selected:
    path=BASE+'/Animations/'+str(src.asset_name)+'_B1_Pilot'
    anim=unreal.load_asset(path);assert anim,path
    assert abs(anim.get_play_length()-src.get_asset().get_play_length())<.001
    opts=unreal.AnimPoseEvaluationOptions();opts.set_editor_property('should_retarget',False)
    row={'source':str(src.package_name),'asset':path,'length':anim.get_play_length(),'samples':[]}
    for f in [0,.25,.5,.75,1]:
        pose=anim.get_anim_pose_at_time(anim.get_play_length()*f,opts)
        row['samples'].append({'t':anim.get_play_length()*f,'bones':{b:unreal.AnimPoseExtensions.get_bone_pose(pose,b,unreal.AnimPoseSpaces.WORLD).translation.to_tuple() for b in ['root','pelvis','head','hand_l','hand_r','foot_l','foot_r']}})
    assert A.save_loaded_asset(anim,False);rows.append(row)
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/pilot-clips.json').write_text(json.dumps(rows,indent=2))
print('Retargeted '+str(len(rows))+' clips; visual and contact approval pending')
