import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools as B
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
A=unreal.EditorAssetLibrary;pc=A.load_asset('/Game/K02/Protagonist/Blueprints/BP_K02_PlayerController');ui=A.load_asset('/Game/K02/UI/Settings/WBP_K02_ComfortOptions');menu=A.load_asset('/Game/K02/UI/Training/WBP_K02_TrainingMenu');U=unreal.get_default_object(unreal.load_class(None,'/Script/UMGToolSet.UMGToolSet'))
def graph(bp,n):return next((g for g in B.list_graphs(bp) if g.get_name()==n),None) or B.add_function_graph(bp,n)
def fn(bp,n,body,params=''):
 g=graph(bp,n);B.write_graph_dsl(g,'(fn '+n+' ('+params+') '+body+')');assert len(B.find_nodes(g))>1,n;B.compile_blueprint(bp,warnings_as_errors=True);assert bp.get_editor_property('Status')==unreal.BlueprintStatus.BS_UP_TO_DATE,n;return g
if 'K02ComfortOptions' not in B.list_variables(pc):B.add_object_variable(pc,'K02ComfortOptions',ui.generated_class())
if 'K02ComfortOpen' not in B.list_variables(pc):B.add_variable(pc,'K02ComfortOpen','bool')
B.compile_blueprint(pc,warnings_as_errors=True)
# Visible values and save outcome always come from runtime state.
body='(bind _pc (Utilities|Casting|CastToBP_K02_PlayerController (Widget|GetOwningPlayer)))\n'
for axis in ['X','Y']:
 body+=f'(Widget|SetText(Text) (Variables|WBP_K02_ComfortOptions|GetSensitivity{axis}Value) (Utilities|Text|ToText(Float) :Value (Class|BPK02PlayerController|GetK02Sensitivity{axis} _pc) :MinimumFractionalDigits 2 :MaximumFractionalDigits 2))\n'
 body+=f'(if (Class|BPK02PlayerController|GetK02Invert{axis} _pc) (Widget|SetText(Text) (Variables|WBP_K02_ComfortOptions|GetInvert{axis}Value) "Sim") (else (Widget|SetText(Text) (Variables|WBP_K02_ComfortOptions|GetInvert{axis}Value) "Não")))\n'
body+='(if (Class|BPK02PlayerController|GetK02PreferencesSaved _pc) (Widget|SetText(Text) (Variables|WBP_K02_ComfortOptions|GetSaveStatus) "Preferências salvas neste computador.") (else (Widget|SetText(Text) (Variables|WBP_K02_ComfortOptions|GetSaveStatus) "Preferências ainda não salvas. Selecione um ajuste ou restaure os padrões.")))'
fn(ui,'K02Refresh',body)
fn(ui,'K02FocusFirst','(Widget|SetUserFocus (Variables|WBP_K02_ComfortOptions|GetSensitivityX) (Widget|GetOwningPlayer)) (Widget|SetKeyboardFocus (Variables|WBP_K02_ComfortOptions|GetSensitivityX))')
fn(pc,'K02DismissComfortOptions','''(if (Variables|Default|GetK02ComfortOpen)
(Widget|RemovefromParent (Variables|Default|GetK02ComfortOptions)) (Variables|Default|SetK02ComfortOpen false))''')
fn(pc,'K02ReturnToTraining','''(CallFunction|K02DismissComfortOptions)
(bind _menu (Variables|Default|GetK02TrainingMenu))
(Widget|SetVisibility _menu "Visible")
(Input|SetInputModeUIOnly :PlayerController self :InWidgetToFocus (Class|WBPK02TrainingMenu|GetResume _menu) :InMouseLockMode "DoNotLock" :bFlushInput true)
(Class|WBPK02TrainingMenu|K02FocusResume _menu)''')
fn(pc,'K02ShowComfortOptions','''(if (and (Variables|Default|GetK02TrainingMenuOpen) (not (Variables|Default|GetK02ComfortOpen)))
(bind _ui (UserInterface|CreateWidget :Class "/Game/K02/UI/Settings/WBP_K02_ComfortOptions.WBP_K02_ComfortOptions_C" :OwningPlayer self))
(Variables|Default|SetK02ComfortOptions _ui)
(Variables|Default|SetK02ComfortOpen true)
(Widget|SetVisibility (Variables|Default|GetK02TrainingMenu) "Collapsed")
(UserInterface|Viewport|AddtoViewport _ui 1001)
(Class|WBPK02ComfortOptions|K02Refresh _ui)
(Input|SetInputModeUIOnly :PlayerController self :InWidgetToFocus (Class|WBPK02ComfortOptions|GetSensitivityX _ui) :InMouseLockMode "DoNotLock" :bFlushInput true)
(Class|WBPK02ComfortOptions|K02FocusFirst _ui))''')
fn(menu,'K02Options','(bind _pc (Utilities|Casting|CastToBP_K02_PlayerController (Widget|GetOwningPlayer))) (Class|BPK02PlayerController|K02ShowComfortOptions _pc)')
fn(ui,'K02Back','(bind _pc (Utilities|Casting|CastToBP_K02_PlayerController (Widget|GetOwningPlayer))) (Class|BPK02PlayerController|K02ReturnToTraining _pc)')
for name,method in [('SensitivityX','K02CycleSensitivityX'),('SensitivityY','K02CycleSensitivityY'),('InvertX','K02ToggleInvertX'),('InvertY','K02ToggleInvertY'),('Reset','K02ResetComfortPreferences')]:
 fn(ui,'K02'+name,'(bind _pc (Utilities|Casting|CastToBP_K02_PlayerController (Widget|GetOwningPlayer))) (Class|BPK02PlayerController|'+method+' _pc) (CallFunction|K02Refresh)')
fn(ui,'OnPreviewKeyDown','''(bind _pc (Utilities|Casting|CastToBP_K02_PlayerController (Widget|GetOwningPlayer)))
(bind _key (Input|KeyEvent|GetKey InKeyEvent))
(if (or (or (Class|BPK02PlayerController|K02KeysEqual _pc _key "Escape") (Class|BPK02PlayerController|K02KeysEqual _pc _key "Gamepad_Special_Right")) (Class|BPK02PlayerController|K02KeysEqual _pc _key "Gamepad_FaceButton_Right"))
(CallFunction|K02Back) (return (Widget|EventReply|Handled))) (return (Widget|EventReply|Unhandled))''','MyGeometry InKeyEvent')
fn(ui,'OnMouseButtonDown','(CallFunction|K02FocusFirst) (return (Widget|EventReply|Handled))','MyGeometry MouseEvent')
for bp,names in [(ui,['SensitivityX','SensitivityY','InvertX','InvertY','Reset','Back']),(menu,['Options'])]:
 for name in names:
  U.call_method('BindToEventProperty',args=(bp,'OnClicked',name,unreal.Button.static_class()));g=graph(bp,'EventGraph');event=next(n for n in B.find_nodes(g) if n.get_class().get_name()=='K2Node_ComponentBoundEvent' and name in n.get_node_title())
  if not event.find_then_pin().list_connected_pins():
   call=unreal.BlueprintGraphEditor.get_graph_editor(g).add_call_function_node(bp.generated_class().get_path_name()+':K02'+name);assert event.find_then_pin().try_create_connection(call.find_execute_pin())
 B.compile_blueprint(bp,warnings_as_errors=True)
g=graph(pc,'K02CloseTrainingMenu');entry=next(n for n in B.find_nodes(g) if n.get_class().get_name()=='K2Node_FunctionEntry');pin=entry.find_then_pin();old=pin.list_connected_pins();assert len(old)==1
if 'K02DismissComfortOptions' not in old[0].get_owning_node().get_node_title().replace(' ',''):
 n=unreal.BlueprintGraphEditor.get_graph_editor(g).add_call_function_node(pc.generated_class().get_path_name()+':K02DismissComfortOptions');pin.break_single_pin_link(old[0]);assert pin.try_create_connection(n.find_execute_pin());assert n.find_then_pin().try_create_connection(old[0])
for bp in [ui,menu,pc]:B.compile_blueprint(bp,warnings_as_errors=True);assert bp.get_editor_property('Status')==unreal.BlueprintStatus.BS_UP_TO_DATE;assert A.save_loaded_asset(bp,False)
print('COMFORT_OPTIONS_BOUND')
