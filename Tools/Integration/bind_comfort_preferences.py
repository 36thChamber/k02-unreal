"""Persist independent look multipliers without replacing MACS input/actions."""
import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools as B
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
A=unreal.EditorAssetLibrary;pc=A.load_asset('/Game/K02/Protagonist/Blueprints/BP_K02_PlayerController')
def graph(n):return next((g for g in B.list_graphs(pc) if g.get_name()==n),None) or B.add_function_graph(pc,n)
def fn(n,body):
 g=graph(n);B.write_graph_dsl(g,'(fn '+n+' () '+body+')');assert len(B.find_nodes(g))>1,n;B.compile_blueprint(pc,warnings_as_errors=True);assert pc.get_editor_property('Status')==unreal.BlueprintStatus.BS_UP_TO_DATE;return g
fields=['K02SensitivityX','K02SensitivityY','K02InvertX','K02InvertY']
body=''
for axis in ['X','Y']:
 body+=f'(Variables|Default|SetK02Sensitivity{axis} (Math|Float|Clamp(Float) (Variables|Default|GetK02Sensitivity{axis}) 0.25 2.0))\n'
 body+=f'(Variables|Default|SetK02LookScale{axis} (* (Variables|Default|GetK02Sensitivity{axis}) (Math|Float|SelectFloat -1.0 1.0 (Variables|Default|GetK02Invert{axis}))))\n'
fn('K02ApplyComfortPreferences',body)
fn('K02SaveComfortPreferences','''(CallFunction|K02ApplyComfortPreferences)
(bind _save (Utilities|Casting|CastToSG_K02_Preferences (SaveGame|CreateSaveGameObject "/Game/K02/UI/Settings/SG_K02_Preferences.SG_K02_Preferences_C")))
'''+''.join(f'(Class|SGK02Preferences|Set{n} (Variables|Default|Get{n}) _save)\n' for n in fields)+'''(Variables|Default|SetK02PreferencesSaved (SaveGame|SaveGametoSlot _save "K02_Preferences_v1" 0))''')
fn('K02LoadComfortPreferences','''(if (not (Variables|Default|GetK02PreferencesLoaded))
(Variables|Default|SetK02PreferencesLoaded true)
(if (SaveGame|DoesSaveGameExist "K02_Preferences_v1" 0)
(bind _save (Utilities|Casting|CastToSG_K02_Preferences (SaveGame|LoadGamefromSlot "K02_Preferences_v1" 0)))
'''+''.join(f'(Variables|Default|Set{n} (Class|SGK02Preferences|Get{n} _save))\n' for n in fields)+'''(Variables|Default|SetK02PreferencesSaved true))
(CallFunction|K02ApplyComfortPreferences))''')
for axis in ['X','Y']:
 fn('K02CycleSensitivity'+axis,f'''(Variables|Default|SetK02Sensitivity{axis} (+ (Variables|Default|GetK02Sensitivity{axis}) 0.25))
(if (> (Variables|Default|GetK02Sensitivity{axis}) 2.0) (Variables|Default|SetK02Sensitivity{axis} 0.25)) (CallFunction|K02SaveComfortPreferences)''')
 fn('K02ToggleInvert'+axis,f'''(Variables|Default|SetK02Invert{axis} (not (Variables|Default|GetK02Invert{axis}))) (CallFunction|K02SaveComfortPreferences)''')
fn('K02ResetComfortPreferences',''.join(f'(Variables|Default|Set{n} '+('1.0' if 'Sensitivity' in n else 'false')+')\n' for n in fields)+'(CallFunction|K02SaveComfortPreferences)')
# Load once before opening the initial menu, before any gameplay look is accepted.
g=graph('K02EnsureTrainingMenu');entry=next(n for n in B.find_nodes(g) if n.get_class().get_name()=='K2Node_FunctionEntry');pin=entry.find_then_pin();old=pin.list_connected_pins();assert len(old)==1
if 'K02LoadComfortPreferences' not in old[0].get_owning_node().get_node_title().replace(' ',''):
 n=unreal.BlueprintGraphEditor.get_graph_editor(g).add_call_function_node(pc.generated_class().get_path_name()+':K02LoadComfortPreferences');pin.break_single_pin_link(old[0]);assert pin.try_create_connection(n.find_execute_pin());assert n.find_then_pin().try_create_connection(old[0])
# Multiply existing Enhanced Input action values directly. Keep original execution, triggers, lock rules.
g=graph('Classic UE Inputs');ed=unreal.BlueprintGraphEditor.get_graph_editor(g)
for axis,function in [('X','AddControllerYawInput'),('Y','AddControllerPitchInput')]:
 n=next(n for n in B.find_nodes(g) if n.get_node_title()==function);val=n.find_input_pin('Val');source=val.list_connected_pins();assert len(source)==1
 if source[0].get_owning_node().get_node_title()=='float * float':continue
 assert source[0].get_owning_node().get_class().get_name()=='K2Node_EnhancedInputAction'
 mul=ed.add_call_function_node('/Script/Engine.KismetMathLibrary:Multiply_DoubleDouble');get=ed.add_get_member_variable_node('K02LookScale'+axis)
 assert source[0].try_create_connection(mul.find_input_pin('A'));assert get.find_output_pin_by_index(0).try_create_connection(mul.find_input_pin('B'))
 val.break_single_pin_link(source[0]);assert mul.find_output_pin('ReturnValue').try_create_connection(val)
 assert mul.find_input_pin('A').list_connected_pins() and mul.find_input_pin('B').list_connected_pins()
B.compile_blueprint(pc,warnings_as_errors=True);assert pc.get_editor_property('Status')==unreal.BlueprintStatus.BS_UP_TO_DATE;assert A.save_loaded_asset(pc,False)
print('COMFORT_PREFERENCES_BOUND')
