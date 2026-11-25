import unreal,json
from pathlib import Path
reg=unreal.AssetRegistryHelpers.get_asset_registry()
source=[x for x in reg.get_assets_by_path('/Game/FightAnimations',recursive=True) if str(x.asset_class_path.asset_name)=='AnimSequence']
rt=unreal.load_asset('/Game/MACS/Demo/ThirdPersonTemplateUE5/Characters/Mannequin_UE4/Rigs/RTG_UE4Manny_UE5Manny')
c=unreal.IKRetargeterController.get_controller(rt)
r={'source_count':len(source),'names':[str(x.asset_name) for x in source],'rigs':{},'api':{}}
for side in [unreal.RetargetSourceOrTarget.SOURCE,unreal.RetargetSourceOrTarget.TARGET]:
 rig=c.get_ik_rig(side);rc=unreal.IKRigController.get_controller(rig)
 r['rigs'][str(side)]={'rig':rig.get_path_name(),'preview':c.get_preview_mesh(side).get_path_name(),'root':str(rc.get_retarget_root()),'chains':[str(x) for x in rc.get_retarget_chains()]}
for obj in [c,unreal.IKRetargetBatchOperationInputs,unreal.AnimSequence,unreal.AnimationLibrary]:
 r['api'][str(obj)[:90]]=[x for x in dir(obj) if any(t in x for t in ['bone','root','pose','op_','chain','frame','notify','length'])]
Path('A:/K-02 5.8/Saved/Diagnostics/retarget-inspect.json').write_text(json.dumps(r,indent=2))
unreal.log('K02_RETARGET_INSPECT '+str(len(source)))
