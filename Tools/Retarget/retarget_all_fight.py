"""Retarget every FightAnimations AnimSequence in small native editor batches."""
import unreal,json,time
from pathlib import Path
ROOT='/Game/K02/Animations/FightAnimations/Manny'
REBUILD_EXISTING=False  # Only isolated outputs; first-pass backup kept outside project.
OUT=Path('A:/K-02 5.8/Saved/Diagnostics/retarget-batch.json')
class FightBatch:
 def __init__(self):
  assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(),'Stop PIE first'
  self.assets=sorted([x for x in unreal.AssetRegistryHelpers.get_asset_registry().get_assets_by_path('/Game/FightAnimations',recursive=True) if str(x.asset_class_path.asset_name)=='AnimSequence'],key=lambda x:str(x.package_name))
  assert len(self.assets)==239
  assert len(set(str(x.asset_name) for x in self.assets))==239,'Duplicate names: preserve directories before export'
  self.source=unreal.load_asset('/Game/FightAnimations/Mannequin/Character/Mesh/SK_Mannequin')
  self.target=unreal.load_asset('/Game/MACS/Demo/ThirdPersonTemplateUE5/Characters/Mannequins/Meshes/SKM_Manny')
  self.rt=unreal.load_asset('/Game/K02/Retarget/FightAnimations/Rigs/RTG_Fight_UE4_K02_Manny')
  self.rows=[];self.pending=[];self.index=0;self.handle=None;self.busy=False;self.started=time.perf_counter()
  for a in self.assets:
   dest=ROOT+'/'+str(a.asset_name)+'_Manny'
   if unreal.EditorAssetLibrary.does_asset_exist(dest) and not REBUILD_EXISTING:
    out=unreal.load_asset(dest);src=a.get_asset()
    assert out.get_editor_property('Skeleton')==self.target.get_editor_property('Skeleton') and abs(out.get_play_length()-src.get_play_length())<0.0001,dest
    self.rows.append({'source':str(a.package_name),'target':dest})
   else:self.pending.append(a)
  self.progress('running')
 def progress(self,status,error=None):
  OUT.write_text(json.dumps({'status':status,'error':error,'source_count':len(self.assets),'completed':len(self.rows),'output_root':ROOT,'elapsed_seconds':time.perf_counter()-self.started,'assets':self.rows},indent=2))
 def tick(self,dt):
  if self.busy:return
  self.busy=True
  try:
   batch=self.pending[self.index:self.index+8]
   if not batch:
    unreal.unregister_slate_post_tick_callback(self.handle);self.handle=None;self.progress('pass');unreal.log('K02_RETARGET_BATCH COMPLETE '+str(len(self.rows)));return
   for a in batch:
    assert REBUILD_EXISTING or not unreal.EditorAssetLibrary.does_asset_exist(ROOT+'/'+str(a.asset_name)+'_Manny'),'Output exists: '+str(a.asset_name)
   inp=unreal.IKRetargetBatchOperationInputs()
   for prop,val in {'assets_to_retarget':batch,'source_mesh':self.source,'target_mesh':self.target,'ik_retarget_asset':self.rt,'target_path':ROOT,'suffix':'_Manny','include_referenced_assets':False,'overwrite_existing_files':REBUILD_EXISTING,'retain_additive_flags':True}.items():inp.set_editor_property(prop,val)
   results=unreal.IKRetargetBatchOperation.run_batch_retarget(inp)
   assert len(results)==len(batch),'Batch returned '+str(len(results))
   for a in batch:
    dest=ROOT+'/'+str(a.asset_name)+'_Manny';out=unreal.load_asset(dest)
    assert out and out.get_editor_property('Skeleton')==self.target.get_editor_property('Skeleton'),dest
    opts=unreal.AnimPoseEvaluationOptions();opts.set_editor_property('should_retarget',False)
    pose=out.get_anim_pose_at_time(unreal.AnimationLibrary.get_time_at_frame(out,unreal.AnimationLibrary.get_num_frames(out)//2),opts)
    for limb in ['hand','foot']:
     for side in ['l','r']:
      b=unreal.AnimPoseExtensions.get_bone_pose(pose,limb+'_'+side,unreal.AnimPoseSpaces.WORLD)
      ik=unreal.AnimPoseExtensions.get_bone_pose(pose,'ik_'+limb+'_'+side,unreal.AnimPoseSpaces.WORLD)
      assert (b.translation-ik.translation).length()<.05,'IK alignment failed: '+dest
    assert unreal.EditorAssetLibrary.save_asset(dest,only_if_is_dirty=False),dest
    self.rows.append({'source':str(a.package_name),'target':dest})
   self.index+=len(batch);self.progress('running');unreal.log('K02_RETARGET_BATCH '+str(len(self.rows))+'/239')
  except Exception as e:
   if self.handle:unreal.unregister_slate_post_tick_callback(self.handle);self.handle=None
   self.progress('fail',str(e));unreal.log_error('K02_RETARGET_BATCH '+str(e))
  finally:self.busy=False
_k02_fight_batch=FightBatch()
_k02_fight_batch.handle=unreal.register_slate_post_tick_callback(_k02_fight_batch.tick)
