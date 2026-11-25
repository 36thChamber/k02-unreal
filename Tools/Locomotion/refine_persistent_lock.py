"""Own K02 idle and persistent target-framing camera; preserve native acquisition and GAS."""
import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
A=unreal.EditorAssetLibrary;D=Path('A:/K-02 5.8/Saved/Diagnostics/PersistentLock');assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(),'Stop PIE'
def props(o,k):return json.loads(unreal.ToolsetLibrary.get_object_properties(o,k))
def put(o,v):assert unreal.ToolsetLibrary.set_object_properties(o,json.dumps(v))
def save(o):assert A.save_loaded_asset(o,only_if_is_dirty=False)
assert not any(g.get_name()=='K02TrackLockedTarget' for g in B.list_graphs(unreal.load_asset('/Game/K02/Protagonist/Blueprints/BP_K02_PlayerController'))),'Already integrated; restore a reviewed checkpoint before rebuilding'
src='/Game/MACS/Animations/Fighter/AS_MACS_Fighter_Idle';dst='/Game/K02/Protagonist/Locomotion/Sequences/AS_K02_Fighter_Idle';idle=unreal.load_asset(dst) if A.does_asset_exist(dst) else A.duplicate_asset(src,dst);unreal.AnimationLibrary.set_root_motion_enabled(idle,False);idle.set_editor_property('bForceRootLock',True);save(idle)
bp=unreal.load_asset('/Game/K02/Protagonist/Locomotion/ABP_K02_Commun')
for g in B.list_graphs(bp):
 if g.get_name()!='MM_Idle':continue
 selector=next(n for n in B.find_nodes(g) if n.get_class().get_name()=='AnimGraphNode_BlendListByBool');n=selector.find_input_pin('BlendPose_0').list_connected_pins()[0].get_owning_node();v=props(n,['node']);v['node']['sequence']={'refPath':idle.get_path_name()};put(n,v)
B.compile_blueprint(bp,warnings_as_errors=True);save(bp)
for name in ['FullBody','UpperBody']:
 m=unreal.load_asset('/Game/K02/Protagonist/Defense/Montages/AM_K02_Guard_'+name);v=props(m,['slotAnimTracks']);seg=v['slotAnimTracks'][0]['animTrack']['animSegments'][0];duration=(seg['animEndTime']-seg['animStartTime'])/seg['animPlayRate'];seg.update({'animReference':{'refPath':idle.get_path_name()},'animStartTime':0,'animEndTime':idle.get_play_length(),'animPlayRate':idle.get_play_length()/duration,'cachedPlayLength':idle.get_play_length()});put(m,v);save(m)
bp=unreal.load_asset('/Game/K02/Protagonist/Blueprints/BP_K02_PlayerController')
for name,typ in [('K02CameraLocked','bool'),('K02SavedArm','float'),('K02SavedSocket','vector'),('K02SavedTargetOffset','vector'),('K02SavedCameraLag','bool'),('K02SavedRotationLag','bool')]:B.add_variable(bp,name,typ)
def graph(name):return next((g for g in B.list_graphs(bp) if g.get_name()==name),None) or unreal.BlueprintEditorLibrary.add_function_graph(bp,name)
pre='''(bind _pawn (Variables|DoNotEdit|GetPawnRef))
(bind _arm (Utilities|Casting|CastToSpringArmComponent (Actor|GetComponentByClass _pawn "/Script/Engine.SpringArmComponent")))'''
code={
'K02EnterCameraLock':'''(if (not (Variables|Default|GetK02CameraLocked))
 (Variables|Default|SetK02SavedArm (Class|SpringArmComponent|GetTargetArmLength _arm))
 (Variables|Default|SetK02SavedSocket (Class|SpringArmComponent|GetSocketOffset _arm))
 (Variables|Default|SetK02SavedTargetOffset (Class|SpringArmComponent|GetTargetOffset _arm))
 (Variables|Default|SetK02SavedCameraLag (Class|SpringArmComponent|GetEnableCameraLag _arm))
 (Variables|Default|SetK02SavedRotationLag (Class|SpringArmComponent|GetEnableCameraRotationLag _arm))
 (Input|SetIgnoreLookInput self true)
 (Variables|Default|SetK02CameraLocked true))''',
'K02ExitCameraLock':'''(if (Variables|Default|GetK02CameraLocked)
 (Class|SpringArmComponent|SetTargetArmLength (Variables|Default|GetK02SavedArm) _arm)
 (Class|SpringArmComponent|SetSocketOffset (Variables|Default|GetK02SavedSocket) _arm)
 (Class|SpringArmComponent|SetTargetOffset (Variables|Default|GetK02SavedTargetOffset) _arm)
 (Class|SpringArmComponent|SetEnableCameraLag (Variables|Default|GetK02SavedCameraLag) _arm)
 (Class|SpringArmComponent|SetEnableCameraRotationLag (Variables|Default|GetK02SavedRotationLag) _arm)
 (Input|SetIgnoreLookInput self false)
 (Variables|Default|SetK02CameraLocked false))''',
'K02ApplyLockedFraming':'''(Class|SpringArmComponent|SetEnableCameraLag false _arm)
(Class|SpringArmComponent|SetEnableCameraRotationLag false _arm)
(Class|SpringArmComponent|SetSocketOffset (Math|Vector|MakeVector 0 0 15) _arm)
(bind _target (Variables|DoNotEdit|GetCurrentTarget))
(bind _a (Transformation|GetActorLocation _pawn))
(bind _b (Transformation|GetActorLocation _target))
(bind _height (- (.z _b) (.z _a)))
(Class|SpringArmComponent|SetTargetOffset (+ (Variables|Default|GetK02SavedTargetOffset) (Math|Vector|MakeVector 0 0 (Math|Float|Max(Float) 0 _height))) _arm)
(Class|SpringArmComponent|SetTargetArmLength (Math|Float|Max(Float) 400 (+ 200 (* 2 (Math|Float|Absolute(Float) _height)))) _arm)
(bind _facing (Math|Rotator|FindLookatRotation _a _b))
(bind _aim (Math|Rotator|FindLookatRotation (+ (Transformation|GetWorldLocation _arm) (Class|SpringArmComponent|GetTargetOffset _arm)) _b))
(Pawn|SetControlRotation self (Math|Rotator|MakeRotator 0 (.pitch _aim) (.yaw _facing)))
(Transformation|SetActorRotation _pawn (Math|Rotator|MakeRotator 0 0 (.yaw _facing)) false)'''
}
# Register helpers before building functions that call them.
for name,body in code.items():
 g=graph(name);B.write_graph_dsl(g,'(fn '+name+' () '+pre+' '+body+')');assert len(B.find_nodes(g))>4,'Incomplete helper '+name
B.compile_blueprint(bp,warnings_as_errors=True)
B.write_graph_dsl(graph('K02TrackLockedTarget'),'''(fn K02TrackLockedTarget ()
 (CallFunction|K02CheckCombatLock)
 (if (Variables|Default|GetK02HasCombatLock)
  (CallFunction|K02EnterCameraLock)
  (CallFunction|K02ApplyLockedFraming)
  (else (CallFunction|K02ExitCameraLock))))''');B.compile_blueprint(bp,warnings_as_errors=True)
# Native acquisition remains available when there is no current lock. Valid locks bypass filtering.
g=graph('CameraLockOnTargetLoop');ed=unreal.BlueprintGraphEditor.get_graph_editor(g)
macros=[n for n in B.find_nodes(g) if n.get_class().get_name()=='K2Node_CallFunction']
acquire=next(n for n in macros if 'GetValidTargetToLockOn' in ''.join(n.get_node_title().split()));select=next(n for n in macros if 'SetOrClearLockOnTarget' in ''.join(n.get_node_title().split()))
old=select.find_then_pin().list_connected_pins()[0];select.find_then_pin().break_single_pin_link(old)
track=ed.add_call_function_node(bp.generated_class().get_path_name()+':K02TrackLockedTarget');assert select.find_then_pin().try_create_connection(track.find_execute_pin())
before=acquire.find_execute_pin().list_connected_pins()[0];before.break_single_pin_link(acquire.find_execute_pin());check=ed.add_call_function_node(bp.generated_class().get_path_name()+':K02CheckCombatLock');branch=B.create_node(g,'Utilities|FlowControl|Branch',unreal.IntPoint(0,0));flag=B.create_node(g,'Variables|Default|GetK02HasCombatLock',unreal.IntPoint(0,0));assert before.try_create_connection(check.find_execute_pin());assert check.find_then_pin().try_create_connection(branch.find_execute_pin());assert flag.find_output_pin_by_index(0).try_create_connection(branch.find_input_pin('Condition'));assert branch.find_output_pin('then').try_create_connection(track.find_execute_pin());assert branch.find_output_pin('else').try_create_connection(acquire.find_execute_pin())
# Toggle the existing manual lock directly between OFF and ON; reuse MACS cleanup.
g=graph('LockOnTargetMode');ed=unreal.BlueprintGraphEditor.get_graph_editor(g);entry=next(n for n in B.find_nodes(g) if n.get_class().get_name()=='K2Node_FunctionEntry');pin=entry.find_then_pin();old=pin.list_connected_pins()[0];pin.break_single_pin_link(old)
zero=next(n for n in B.find_nodes(g) if n.get_class().get_name()=='K2Node_VariableSet' and 'lockonmode' in ''.join(n.get_node_title().split()).lower());incoming=zero.find_execute_pin().list_connected_pins()
for p in incoming:p.break_single_pin_link(zero.find_execute_pin())
get=B.create_node(g,'Variables|DoNotEdit|GetLockonMode',unreal.IntPoint(0,0));compare=ed.add_call_function_node('/Script/Engine.KismetMathLibrary:Greater_IntInt');assert get.find_output_pin_by_index(0).try_create_connection(compare.find_input_pin('A'));branch=B.create_node(g,'Utilities|FlowControl|Branch',unreal.IntPoint(0,0));one=B.create_node(g,'Variables|DoNotEdit|SetLockonMode',unreal.IntPoint(0,0));assert one.find_input_pin('LockonMode').set_pin_value('1');assert pin.try_create_connection(branch.find_execute_pin());assert compare.find_output_pin('ReturnValue').try_create_connection(branch.find_input_pin('Condition'));assert branch.find_output_pin('then').try_create_connection(zero.find_execute_pin());assert branch.find_output_pin('else').try_create_connection(one.find_execute_pin())
B.arrange_nodes(B.find_nodes(g));B.compile_blueprint(bp,warnings_as_errors=True);save(bp)
(D/'build.json').write_text(json.dumps({'idle':idle.get_path_name(),'toggle':'0/1','persistentTarget':True},indent=2));unreal.log('K02_PERSISTENT_LOCK_BUILT')
