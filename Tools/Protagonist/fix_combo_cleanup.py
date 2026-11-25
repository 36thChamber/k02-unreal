"""Always stop the protagonist's unarmed trace when a Fighter ability ends/cancels."""
import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
A=unreal.EditorAssetLibrary;ROOT='/Game/K02/Protagonist';assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
p=ROOT+'/Abilities/GA_K02_Base_Combo';base=unreal.load_asset(p) if A.does_asset_exist(p) else A.duplicate_asset('/Game/MACS/GAS/Abilities/Base/GA_MACS_Base_Combo',p)
f=next((g for g in B.list_graphs(base) if g.get_name()=='K02StopUnarmedTrace'),None) or unreal.BlueprintEditorLibrary.add_function_graph(base,'K02StopUnarmedTrace')
B.write_graph_dsl(f,'''(fn K02StopUnarmedTrace ()
  (bind _trace (Actor|GetComponentByClass (Ability|GetAvatarActorFromActorInfo) "/Game/MACS/Classes/Components/BP_MACS_TraceComp.BP_MACS_TraceComp_C"))
  (Utilities|IsValid _trace
    (:"Is Valid" (Class|BPMACSTraceComp|StopTrace _trace))))''')
unreal.BlueprintEditorLibrary.compile_blueprint(base)
g=next(g for g in B.list_graphs(base) if g.get_name()=='Gameplay Ability Graph');ed=unreal.BlueprintGraphEditor.get_graph_editor(g);event=next(n for n in B.find_nodes(g) if 'OnEndAbility' in n.get_node_title());outputs=event.find_then_pin().list_connected_pins();assert len(outputs)==1
n=ed.add_call_function_node(base.generated_class().get_path_name()+':K02StopUnarmedTrace');event.find_then_pin().break_single_pin_link(outputs[0]);assert event.find_then_pin().try_create_connection(n.find_execute_pin());assert n.find_then_pin().try_create_connection(outputs[0]);unreal.BlueprintEditorLibrary.compile_blueprint(base);assert A.save_loaded_asset(base,only_if_is_dirty=False)
rows=[]
for path in A.list_assets(ROOT+'/Abilities',recursive=False,include_folder=False):
 bp=unreal.load_asset(path)
 if not isinstance(bp,unreal.Blueprint) or bp==base:continue
 parent=unreal.BlueprintEditorLibrary.get_blueprint_parent_class(bp)
 if parent.get_path_name()=='/Game/MACS/GAS/Abilities/Base/GA_MACS_Base_Combo.GA_MACS_Base_Combo_C':
  c=unreal.get_default_object(bp.generated_class());before=c.get_editor_property('AbilityMontage').get_path_name()
  unreal.BlueprintEditorLibrary.reparent_blueprint(bp,base.generated_class());unreal.BlueprintEditorLibrary.compile_blueprint(bp)
  assert unreal.get_default_object(bp.generated_class()).get_editor_property('AbilityMontage').get_path_name()==before
  assert A.save_loaded_asset(bp,only_if_is_dirty=False);rows.append(bp.get_path_name())
Path('A:/K-02 5.8/Saved/Diagnostics/protagonist-combo-cleanup.json').write_text(json.dumps({'reparented':rows,'cleanup':'StopTrace on avatar component before legacy EndAbility cleanup'},indent=2));unreal.log('K02_COMBO_CLEANUP_FIXED '+str(len(rows)))
