"""Report an actually refused manual guard activation, without changing its legality."""
import unreal,json
from editor_toolset.toolsets.blueprint import BlueprintTools as B
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
A=unreal.EditorAssetLibrary;pc=A.load_asset('/Game/K02/Protagonist/Blueprints/BP_K02_PlayerController');ui=A.load_asset('/Game/K02/UI/Combat/WBP_K02_CombatNotice');assert ui
if 'K02CombatNotice' not in B.list_variables(pc):B.add_object_variable(pc,'K02CombatNotice',ui.generated_class())
if 'K02CombatNoticeText' not in B.list_variables(pc):B.add_variable(pc,'K02CombatNoticeText','text')
B.compile_blueprint(pc,warnings_as_errors=True)
def graph(n):return next((g for g in B.list_graphs(pc) if g.get_name()==n),None) or B.add_function_graph(pc,n)
def fn(n,body):
 g=graph(n);B.write_graph_dsl(g,'(fn '+n+' () '+body+')');assert len(B.find_nodes(g))>1,n;B.compile_blueprint(pc,warnings_as_errors=True);assert pc.get_editor_property('Status')==unreal.BlueprintStatus.BS_UP_TO_DATE;return g
fn('K02ClearCombatNotice','''(Utilities|Time|ClearTimerbyFunctionName self "K02ClearCombatNotice")
(Utilities|IsValid (Variables|Default|GetK02CombatNotice) (:"Is Valid" (Widget|SetVisibility (Variables|Default|GetK02CombatNotice) "Collapsed")))''')
fn('K02EnsureCombatNotice','''(Utilities|IsValid (Variables|Default|GetK02CombatNotice) (:"Is Not Valid"
(bind _ui (UserInterface|CreateWidget :Class "/Game/K02/UI/Combat/WBP_K02_CombatNotice.WBP_K02_CombatNotice_C" :OwningPlayer self))
(Variables|Default|SetK02CombatNotice _ui) (UserInterface|Viewport|AddtoViewport _ui 200)))''')
fn('K02ShowCombatNotice','''(CallFunction|K02EnsureCombatNotice)
(Widget|SetText(Text) (Class|WBPK02CombatNotice|GetNoticeText (Variables|Default|GetK02CombatNotice)) (Variables|Default|GetK02CombatNoticeText))
(Widget|SetVisibility (Variables|Default|GetK02CombatNotice) "HitTestInvisible")
(Utilities|Time|SetTimerbyFunctionName :Object self :FunctionName "K02ClearCombatNotice" :Time 2.75 :bLooping false)''')
attr='(AttributeName="Resource",Attribute=/Script/MAUT.MAUT_AttributeSet:Resource,AttributeOwner="/Script/CoreUObject.Class\'/Script/MAUT.MAUT_AttributeSet\'")'
fn('K02NotifyGuardRefused','''(if (Game|Player|WasInputKeyJustPressed self "LeftControl")
(bind (_found _resource) (Ability|Attribute|GetFloatAttribute (Variables|DoNotEdit|GetPawnRef) ATTR))
(if (and _found (< _resource 0.1))
(Variables|Default|SetK02CombatNoticeText "Sem recurso para bloquear. Aguarde a recuperação.")
(else (Variables|Default|SetK02CombatNoticeText "Defesa indisponível durante esta ação. Aguarde a recuperação.")))
(CallFunction|K02ShowCombatNotice))'''.replace('ATTR',json.dumps(attr)))
g=graph('K02CombatInputTick');ed=unreal.BlueprintGraphEditor.get_graph_editor(g);n=next(n for n in B.find_nodes(g) if n.get_node_title().replace(' ','')=='TryActivateAbilityByClass' and 'GA_K02_DefenseMode' in n.find_input_pin('InAbilityToActivate').get_pin_value())
if not n.find_then_pin().list_connected_pins():
 branch=ed.add_branch_node();assert n.find_then_pin().try_create_connection(branch.find_execute_pin());assert n.find_output_pin('ReturnValue').try_create_connection(branch.find_input_pin('Condition'))
 for out,method in [('then','K02ClearCombatNotice'),('else','K02NotifyGuardRefused')]:
  call=ed.add_call_function_node(pc.generated_class().get_path_name()+':'+method);assert branch.find_output_pin(out).try_create_connection(call.find_execute_pin())
# A menu always clears stale combat notices and their timer.
g=graph('K02ShowTrainingMenu');entry=next(n for n in B.find_nodes(g) if n.get_class().get_name()=='K2Node_FunctionEntry');pin=entry.find_then_pin();old=pin.list_connected_pins();assert len(old)==1
if 'K02ClearCombatNotice' not in old[0].get_owning_node().get_node_title().replace(' ',''):
 call=unreal.BlueprintGraphEditor.get_graph_editor(g).add_call_function_node(pc.generated_class().get_path_name()+':K02ClearCombatNotice');pin.break_single_pin_link(old[0]);assert pin.try_create_connection(call.find_execute_pin());assert call.find_then_pin().try_create_connection(old[0])
B.compile_blueprint(pc,warnings_as_errors=True);assert pc.get_editor_property('Status')==unreal.BlueprintStatus.BS_UP_TO_DATE;assert A.save_loaded_asset(pc,False);print('DEFENSE_NOTICE_BOUND')
