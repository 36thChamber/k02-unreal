import unreal,json
from editor_toolset.toolsets.blueprint import BlueprintTools as B
bp=unreal.load_asset('/Game/K02/Protagonist/Blueprints/BP_K02_PlayerController');name='K02KeysEqual';g=next((g for g in B.list_graphs(bp) if g.get_name()==name),None)
if g:unreal.BlueprintEditorLibrary.remove_function_graph(bp,name)
g=unreal.BlueprintEditorLibrary.add_function_graph(bp,name)
for p in ['A','B']:B.add_struct_function_param(g,p,unreal.load_object(None,'/Script/InputCore.Key'),True)
B.add_function_param(g,'ReturnValue','bool',False)
ed=unreal.BlueprintGraphEditor.get_graph_editor(g);n=ed.add_call_function_node('/Script/Engine.KismetInputLibrary:EqualEqual_KeyKey');assert n
entry=next(n for n in B.find_nodes(g) if n.get_class().get_name()=='K2Node_FunctionEntry');result=next(n for n in B.find_nodes(g) if n.get_class().get_name()=='K2Node_FunctionResult')
for key in ['A','B']:assert entry.find_output_pin(key).try_create_connection(n.find_input_pin(key))
assert n.find_output_pin('ReturnValue').try_create_connection(result.find_input_pin('ReturnValue'));assert entry.find_then_pin().try_create_connection(result.find_execute_pin())
B.compile_blueprint(bp,warnings_as_errors=True);unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False);unreal.log('K02_KEY_HELPER_OK')
