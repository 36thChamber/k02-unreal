import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools as B
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
bp=unreal.load_asset('/Game/K02/UI/Training/WBP_K02_TrainingMenu');g=B.add_function_graph(bp,'OnMouseButtonDown');B.write_graph_dsl(g,'(fn OnMouseButtonDown (MyGeometry MouseEvent) (CallFunction|K02FocusResume) (return (Widget|EventReply|Handled)))');B.compile_blueprint(bp,warnings_as_errors=True);assert bp.get_editor_property('Status')==unreal.BlueprintStatus.BS_UP_TO_DATE;assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
print('BACKGROUND_CLICK_HANDLED')
