import unreal,json,sys
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
sys.path.insert(0,'A:/K-02 5.8/Tools/Protagonist')
from kyokushin_assets import *
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
r=move('M07','A_FrontKick_L','foot_l_Trace_Sphere','Combo_4_1',8,7,11,True)
branches('M07',[('IA_MACS_HeavyAttack_1','4.2')]);bp=ability('Combo_4_2');c=unreal.get_default_object(bp.generated_class());c.set_editor_property('AbilityMontage',unreal.load_asset(MROOT+'/AM_K02_Kyokushin_M02'));c.set_editor_property('AbilityDamage',6);unreal.BlueprintEditorLibrary.compile_blueprint(bp);save(bp);grant(['Combo_4_1','Combo_4_2'])
pc=unreal.load_asset(ROOT+'/Blueprints/BP_K02_PlayerController');f=next((g for g in B.list_graphs(pc) if g.get_name()=='K02FrontKickInput'),None) or unreal.BlueprintEditorLibrary.add_function_graph(pc,'K02FrontKickInput')
B.write_graph_dsl(f,Path('A:/K-02 5.8/Tools/Protagonist/front_kick_input.dsl').read_text());unreal.BlueprintEditorLibrary.compile_blueprint(pc)
g=next(g for g in B.list_graphs(pc) if g.get_name()=='Abilities Classes');ed=unreal.BlueprintGraphEditor.get_graph_editor(g);n=next(x for x in B.find_nodes(g) if x.get_name()=='K2Node_CallFunction_24');up=n.find_execute_pin().list_connected_pins()[0]
call=ed.add_call_function_node(pc.generated_class().get_path_name()+':K02FrontKickInput');assert call
up.break_single_pin_link(n.find_execute_pin());assert up.try_create_connection(call.find_execute_pin());assert call.find_then_pin().try_create_connection(n.find_execute_pin())
unreal.BlueprintEditorLibrary.compile_blueprint(pc);save(pc)
Path('A:/K-02 5.8/Saved/Diagnostics/kyokushin-c03-build.json').write_text(json.dumps(r,indent=2));unreal.log('K02_KYOKUSHIN_C03_BUILT')
