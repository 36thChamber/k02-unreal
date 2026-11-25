"""Keep MACS-style combat stance in locomotion; give manual block its own held pose."""
import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
A=unreal.EditorAssetLibrary;R='/Game/K02/Protagonist'
assert 'K-02 5.8' in unreal.Paths.project_dir()
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
def get(o,keys):return json.loads(unreal.ToolsetLibrary.get_object_properties(o,keys))
clip=unreal.load_asset(R+'/Defense/Sequences/AS_K02_Block_Idle');assert clip
bp=unreal.load_asset(R+'/Abilities/GA_K02_DefenseMode');c=unreal.get_default_object(bp.generated_class());rows=[]
for part in ['FullBody','UpperBody']:
 src=R+'/Defense/Montages/AM_K02_Guard_'+part;dst=R+'/Defense/Montages/AM_K02_BlockHold_'+part
 m=unreal.load_asset(dst) if A.does_asset_exist(dst) else A.duplicate_asset(src,dst);assert m
 # Preserve the existing section/loop timing and blend settings.
 v=get(unreal.load_asset(src),['slotAnimTracks']);seg=v['slotAnimTracks'][0]['animTrack']['animSegments'][0];duration=(seg['animEndTime']-seg['animStartTime'])/seg['animPlayRate']
 seg.update({'animReference':{'refPath':clip.get_path_name()},'animStartTime':0,'animEndTime':clip.get_play_length(),'animPlayRate':clip.get_play_length()/duration,'cachedPlayLength':clip.get_play_length()})
 assert unreal.ToolsetLibrary.set_object_properties(m,json.dumps(v));assert A.save_loaded_asset(m,only_if_is_dirty=False)
 c.set_editor_property(part+'DefendMontage',m);rows.append({'montage':m.get_path_name(),**get(m,['slotAnimTracks','blendIn','blendOut'])})
B.compile_blueprint(bp,warnings_as_errors=True);assert A.save_loaded_asset(bp,only_if_is_dirty=False)
# Read the actual combat-idle graph without changing it.
a=unreal.load_asset(R+'/Locomotion/ABP_K02_Commun');g=next(g for g in B.list_graphs(a) if g.get_name()=='MM_Idle');selector=next(n for n in B.find_nodes(g) if n.get_class().get_name()=='AnimGraphNode_BlendListByBool');node=selector.find_input_pin('BlendPose_0').list_connected_pins()[0].get_owning_node();stance=get(node,['node'])['node']['sequence']['refPath'];assert 'AS_K02_Fighter_Idle' in stance
result={'stance':stance,'block':clip.get_path_name(),'montages':rows,'pass':stance!=clip.get_path_name()};Path('A:/K-02 5.8/Saved/Diagnostics/StanceBlock/after.json').write_text(json.dumps(result,indent=2));unreal.log('K02_STANCE_BLOCK_SEPARATED '+str(result['pass']))
