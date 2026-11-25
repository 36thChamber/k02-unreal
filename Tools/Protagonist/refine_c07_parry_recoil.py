"""Keep native stun control while supplying a planted, short parry reaction."""
import unreal,json,sys
from pathlib import Path
sys.path.insert(0,'A:/K-02 5.8/Tools/Protagonist')
from kyokushin_assets import *
from editor_toolset.toolsets.blueprint import BlueprintTools as B
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
# Discard temporary macro expansions from read-only diagnosis before editing the own graph.
hit=unreal.load_asset(ROOT+'/Abilities/GA_K02_HitReactions');unreal.EditorLoadingAndSavingUtils.reload_packages([hit.get_outermost()],unreal.ReloadPackagesInteractionMode.ASSUME_POSITIVE);hit=unreal.load_asset(ROOT+'/Abilities/GA_K02_HitReactions')
seq=clone(ROOT+'/Reactions/Sequences/AS_K02_HitBody_F',ROOT+'/Counter/Sequences/AS_K02_ParryRecoil');unreal.AnimationLibrary.set_root_motion_enabled(seq,True);seq.set_editor_property('bForceRootLock',True);seq.set_editor_property('RootMotionRootLock',unreal.RootMotionRootLock.ANIM_FIRST_FRAME);save(seq)
m=clone(ROOT+'/Reactions/Montages/AM_K02_HitBody_F',ROOT+'/Counter/Montages/AM_K02_ParryRecoil');v=props(m,['slotAnimTracks']);v['slotAnimTracks'][0]['animTrack']['animSegments'][0]['animReference']={'refPath':seq.get_path_name()};setprops(m,v);save(m)
base=clone('/Game/MACS/GAS/Abilities/Base/GA_MACS_Base_DefenseMode',ROOT+'/Abilities/GA_K02_Base_DefenseMode');g=next(g for g in B.list_graphs(base) if g.get_name()=='Gameplay Ability Graph');n=next(n for n in B.find_nodes(g) if 'SetHitReaction' in n.get_node_title());info=B._get_node_info(n);pin=next(p for p in info.input_pins if 'SpecificMontage' in p.name);B.set_pin_value(pin.pin_id,m.get_path_name());B.compile_blueprint(base,warnings_as_errors=True);save(base)
guard=unreal.load_asset(ROOT+'/Abilities/GA_K02_DefenseMode');unreal.BlueprintEditorLibrary.reparent_blueprint(guard,base.generated_class());B.compile_blueprint(guard,warnings_as_errors=True);save(guard)
# The existing SpecificMontage pin is only used by MACS's special flying reaction.
# Honor it before choosing a directional montage, preserving native stun and collision rules.
g=next(g for g in B.list_graphs(hit) if g.get_name()=='SelectRightMontage');ed=unreal.BlueprintGraphEditor.get_graph_editor(g)
entry=next(n for n in B.find_nodes(g) if n.get_class().get_name()=='K2Node_FunctionEntry');out=entry.find_then_pin();old=out.list_connected_pins();assert len(old)==1
if 'Branch' not in old[0].get_owning_node().get_node_title():
 source=None
 for n in B.find_nodes(g):
  for p in B._get_node_info(n).output_pins:
   if 'SpecificMontage' in p.name:source=n.find_output_pin(p.name)
 assert source
 result=ed.add_return_node();rp=next(p for p in B._get_node_info(result).input_pins if 'Anim Montage' in p.type_id);assert source.try_create_connection(result.find_input_pin(rp.name))
 valid=ed.add_call_function_node('/Script/Engine.KismetSystemLibrary:IsValid');assert source.try_create_connection(valid.find_input_pin('Object'))
 branch=ed.add_branch_node();assert valid.find_output_pin('ReturnValue').try_create_connection(branch.find_input_pin('Condition'));out.break_single_pin_link(old[0]);assert out.try_create_connection(branch.find_execute_pin());assert branch.find_then_pin().try_create_connection(result.find_execute_pin());assert branch.find_output_pin('else').try_create_connection(old[0])
B.compile_blueprint(hit,warnings_as_errors=True);save(hit)
Path('A:/K-02 5.8/Saved/Diagnostics/C07/recoil.json').write_text(json.dumps({'montage':m.get_path_name(),'controlTypePreserved':'KnockBack / native stun','guardParent':base.get_path_name()},indent=2));unreal.log('K02_C07_SHORT_PARRY_RECOIL')
