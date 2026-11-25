"""Use existing Enhanced Input heavy-2 channel as deterministic T on R."""
import unreal,json
from editor_toolset.toolsets.blueprint import BlueprintTools as B
A=unreal.EditorAssetLibrary;ROOT='/Game/K02/Protagonist';assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
p=ROOT+'/Inputs/IMC_K02_Abilities';imc=unreal.load_asset(p) if A.does_asset_exist(p) else A.duplicate_asset('/Game/MACS/Inputs/Abilities/IMC_MACS_Abilities',p)
source=unreal.load_asset('/Game/MACS/Inputs/Abilities/IMC_MACS_Abilities')
v=json.loads(unreal.ToolsetLibrary.get_object_properties(source,['defaultKeyMappings']));v=json.loads(json.dumps(v).replace(source.get_path_name(),imc.get_path_name()));ms=v['defaultKeyMappings']['mappings'];row=json.loads(json.dumps(ms[0]));row['action']={'refPath':'/Game/MACS/Inputs/Abilities/IA_MACS_HeavyAttack_2.IA_MACS_HeavyAttack_2'};row['key']='R'
v['defaultKeyMappings']['mappings']=[m for m in ms if 'IA_MACS_HeavyAttack_2.' not in m['action']['refPath']]+[row]
assert unreal.ToolsetLibrary.set_object_properties(imc,json.dumps({'defaultKeyMappings':{'mappings':[]}}));assert unreal.ToolsetLibrary.set_object_properties(imc,json.dumps(v));assert A.save_loaded_asset(imc,only_if_is_dirty=False)
pc=unreal.load_asset(ROOT+'/Blueprints/BP_K02_PlayerController')
for g in B.list_graphs(pc):
 for n in B.find_nodes(g):
  for pin in n.list_input_pins():
   if pin.get_pin_value()=='/Game/MACS/Inputs/Abilities/IMC_MACS_Abilities.IMC_MACS_Abilities':assert pin.set_pin_value(imc.get_path_name())
for g in list(B.list_graphs(pc)):
 if g.get_name()=='K02StrongKick':unreal.BlueprintEditorLibrary.remove_function_graph(pc,'K02StrongKick')
unreal.BlueprintEditorLibrary.compile_blueprint(pc);assert A.save_loaded_asset(pc,only_if_is_dirty=False)
unused=ROOT+'/Inputs/IA_K02_StrongKick'
if A.does_asset_exist(unused):assert A.delete_asset(unused)
unreal.log('K02_STRONG_KICK_INPUT_BUILT R -> existing IA_MACS_HeavyAttack_2')
