"""Bind own pause/help/restart menu, with real pause and input flushing."""
import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
A=unreal.EditorAssetLibrary;pc=A.load_asset('/Game/K02/Protagonist/Blueprints/BP_K02_PlayerController');ui=A.load_asset('/Game/K02/UI/Training/WBP_K02_TrainingMenu');U=unreal.get_default_object(unreal.load_class(None,'/Script/UMGToolSet.UMGToolSet'))
def graph(bp,n):return next((g for g in B.list_graphs(bp) if g.get_name()==n),None) or B.add_function_graph(bp,n)
def fn(bp,n,body):g=graph(bp,n);B.write_graph_dsl(g,'(fn '+n+' () '+body+')');assert len(B.find_nodes(g))>1, 'Empty generated graph: '+n;B.compile_blueprint(bp,warnings_as_errors=True);return g
fn(ui,'K02FocusResume','(Widget|SetUserFocus (Variables|WBP_K02_TrainingMenu|GetResume) (Widget|GetOwningPlayer)) (Widget|SetKeyboardFocus (Variables|WBP_K02_TrainingMenu|GetResume))')
for n in ['K02TrainingMenuOpen','K02TrainingMenuInitialized']:
 if n not in B.list_variables(pc):B.add_variable(pc,n,'bool')
if 'K02TrainingMenu' not in B.list_variables(pc):B.add_object_variable(pc,'K02TrainingMenu',ui.generated_class())
B.compile_blueprint(pc,warnings_as_errors=True)
fn(pc,'K02CloseTrainingMenu','''(if (Variables|Default|GetK02TrainingMenuOpen)
(Widget|RemovefromParent (Variables|Default|GetK02TrainingMenu))
(Variables|Default|SetK02TrainingMenuOpen false)
(Variables|Default|SetK02BufferedP -100)
(Variables|Default|SetK02BufferedF -100)
(Variables|Default|SetK02BufferedK -100)
(Variables|Default|SetK02BufferedT -100)
(Game|SetGamePaused false)
(Input|SetInputModeGameOnly self true)
(Variables|MouseInterface|SetShowMouseCursor false)
(Focus|SetFocustoGameViewport))''')
fn(pc,'K02ShowTrainingMenu','''(if (not (Variables|Default|GetK02TrainingMenuOpen))
(bind _menu (UserInterface|CreateWidget :Class "/Game/K02/UI/Training/WBP_K02_TrainingMenu.WBP_K02_TrainingMenu_C" :OwningPlayer self))
(Variables|Default|SetK02TrainingMenu _menu)
(Variables|Default|SetK02TrainingMenuOpen true)
(UserInterface|Viewport|AddtoViewport _menu 1000)
(Input|SetInputModeUIOnly :PlayerController self :InWidgetToFocus (Class|WBPK02TrainingMenu|GetResume _menu) :InMouseLockMode "DoNotLock" :bFlushInput true)
(Variables|MouseInterface|SetShowMouseCursor true)
(Game|SetGamePaused true)
(Class|WBPK02TrainingMenu|K02FocusResume _menu))''')
fn(pc,'K02ToggleTrainingMenu','''(if (Variables|Default|GetK02TrainingMenuOpen) (CallFunction|K02CloseTrainingMenu) (else (CallFunction|K02ShowTrainingMenu)))''')
fn(pc,'K02EnsureTrainingMenu','''(if (not (Variables|Default|GetK02TrainingMenuInitialized))
(Utilities|IsValid (Variables|DoNotEdit|GetPawnRef) (:"Is Valid"
(Variables|Default|SetK02TrainingMenuInitialized true)
(CallFunction|K02ShowTrainingMenu))))''')
# Menu actions live in the widget, not an editor-only test script.
fn(ui,'K02Resume','''(bind _pc (Utilities|Casting|CastToBP_K02_PlayerController (Widget|GetOwningPlayer))) (Class|BPK02PlayerController|K02CloseTrainingMenu _pc)''')
fn(ui,'K02Restart','''(bind _pc (Utilities|Casting|CastToBP_K02_PlayerController (Widget|GetOwningPlayer))) (Class|BPK02PlayerController|K02CloseTrainingMenu _pc) (Game|OpenLevel(byName) :LevelName "/Game/K02/Prototype/Levels/L_K02_CombatArena" :bAbsolute true)''')
g=graph(ui,'OnPreviewKeyDown');B.write_graph_dsl(g,'''(fn OnPreviewKeyDown (MyGeometry InKeyEvent)
(bind _pc (Utilities|Casting|CastToBP_K02_PlayerController (Widget|GetOwningPlayer)))
(bind _key (Input|KeyEvent|GetKey InKeyEvent))
(if (or (or (Class|BPK02PlayerController|K02KeysEqual _pc _key "Escape") (Class|BPK02PlayerController|K02KeysEqual _pc _key "Gamepad_Special_Right")) (Class|BPK02PlayerController|K02KeysEqual _pc _key "Gamepad_FaceButton_Right"))
(CallFunction|K02Resume) (return (Widget|EventReply|Handled)))
(return (Widget|EventReply|Unhandled)))''');B.compile_blueprint(ui,warnings_as_errors=True)
g=graph(ui,'OnMouseButtonDown');B.write_graph_dsl(g,'(fn OnMouseButtonDown (MyGeometry MouseEvent) (CallFunction|K02FocusResume) (return (Widget|EventReply|Handled)))');B.compile_blueprint(ui,warnings_as_errors=True)
for name,method in [('Resume','K02Resume'),('Restart','K02Restart')]:
 U.call_method('BindToEventProperty',args=(ui,'OnClicked',name,unreal.Button.static_class()))
 g=graph(ui,'EventGraph');event=next(n for n in B.find_nodes(g) if n.get_class().get_name()=='K2Node_ComponentBoundEvent' and name in n.get_node_title())
 if not event.find_then_pin().list_connected_pins():
  n=unreal.BlueprintGraphEditor.get_graph_editor(g).add_call_function_node(ui.generated_class().get_path_name()+':'+method);assert event.find_then_pin().try_create_connection(n.find_execute_pin())
B.compile_blueprint(ui,warnings_as_errors=True)
g=graph(pc,'EventGraph');ed=unreal.BlueprintGraphEditor.get_graph_editor(g)
for key,typ in [('Escape','Input|KeyboardEvents|Escape'),('Gamepad Special Right','Input|GamepadEvents|GamepadSpecialRight')]:
 if any(n.get_node_title()==key for n in B.find_nodes(g)):continue
 event=B.create_node(g,typ,unreal.IntPoint(-2200,1000))
 assert unreal.ToolsetLibrary.set_object_properties(event,json.dumps({'bExecuteWhenPaused':True,'bConsumeInput':True}))
 n=ed.add_call_function_node(pc.generated_class().get_path_name()+':K02ToggleTrainingMenu');assert event.find_output_pin('Pressed').try_create_connection(n.find_execute_pin())
# Insert before own tick; original initialization and camera chains are retained.
event=next(n for n in B.find_nodes(g) if n.get_node_title()=='Event Tick');pin=event.find_then_pin();old=pin.list_connected_pins();assert len(old)==1
if 'K02EnsureTrainingMenu' not in old[0].get_owning_node().get_node_title().replace(' ',''):
 n=ed.add_call_function_node(pc.generated_class().get_path_name()+':K02EnsureTrainingMenu');pin.break_single_pin_link(old[0]);assert pin.try_create_connection(n.find_execute_pin());assert n.find_then_pin().try_create_connection(old[0])
for bp in [ui,pc]:B.compile_blueprint(bp,warnings_as_errors=True);assert bp.get_editor_property('Status')==unreal.BlueprintStatus.BS_UP_TO_DATE;assert A.save_loaded_asset(bp,False)
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/training-menu-binding.json').write_text(json.dumps({'widget':ui.get_path_name(),'controller':pc.get_path_name(),'startup':'Pause when possessed pawn is initialized','open':'Escape / Gamepad Special Right','close':'focused Resume / Escape / gamepad Back','restart':'Reload same arena, then pause again','input':'UI-only while paused, pressed inputs flushed on open and close, combo buffers cleared on close','status':'compiled, runtime validation pending'},indent=2))
print('TRAINING_MENU_BOUND')
