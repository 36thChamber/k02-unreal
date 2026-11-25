"""Atomically swap matching masked body + outfit on the game thread."""
import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
from editor_toolset.toolsets.actor import ActorTools as Actors
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
base='/Game/K02/Characters/Roster/B_1/v009';bp=unreal.load_asset(base+'/Blueprints/BP_B_1_Presentation')
assert bp
def link(a,b):assert a and b and a.try_create_connection(b)
comps={c.get_name().replace('_GEN_VARIABLE',''):c for c in Actors.get_components(B.get_default_object(bp))}
robe=comps.get('Robe') or Actors.add_component(comps['Body'],unreal.SkeletalMeshComponent.static_class(),'Robe')
robe.set_skeletal_mesh_asset(unreal.load_asset(base+'/Meshes/SK_B_1_RobeOnly_v009'))
robe.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
robe.set_visibility(False,False)
robe.set_editor_property('hidden_in_game',False)
robe.set_editor_property('bounds_scale',1.2)
B.compile_blueprint(bp,warnings_as_errors=True)
g=next(g for g in B.list_graphs(bp) if g.get_name()=='K02RefreshPresentation');ed=unreal.BlueprintGraphEditor.get_graph_editor(g)
if not any('Robe' in n.get_node_title() for n in B.find_nodes(g)):
 last=next(n for n in B.find_nodes(g) if 'AddTickPrerequisiteComponent' in n.get_node_title().replace(' ','') and not n.find_then_pin().list_connected_pins())
 rv=ed.add_get_member_variable_node('Robe').find_output_pin_by_index(0);bv=ed.add_get_member_variable_node('Body').find_output_pin_by_index(0)
 leader=ed.add_call_function_node('/Script/Engine.SkinnedMeshComponent:SetLeaderPoseComponent');link(rv,leader.find_input_pin('self'));link(bv,leader.find_input_pin('NewLeaderBoneComponent'));leader.find_input_pin('bForceUpdate').set_pin_value('true');link(last.find_then_pin(),leader.find_execute_pin())
 tick=ed.add_call_function_node('/Script/Engine.ActorComponent:AddTickPrerequisiteComponent');link(rv,tick.find_input_pin('self'));link(bv,tick.find_input_pin('PrerequisiteComponent'));link(leader.find_then_pin(),tick.find_execute_pin())
if 'RobeEnabled' not in B.list_variables(bp):B.add_variable(bp,'RobeEnabled','bool')
B.compile_blueprint(bp,warnings_as_errors=True)
name='K02SetRobePresentation'
for old in list(B.list_graphs(bp)):
 if old.get_name().startswith(name):B.remove_function_graph(bp,old.get_name())
B.compile_blueprint(bp,warnings_as_errors=True)
if True:
 ed=unreal.BlueprintGraphEditor.create_and_edit_function_graph(bp,name);g=ed.get_graph();assert g.get_name()==name,g.get_name()
 B.add_function_param(g,'Enabled','bool',True)
 def link(a,b):assert a and b and a.try_create_connection(b)
 entry=ed.find_graph_entry_pin();enabled=entry.get_owning_node().find_output_pin('Enabled')
 state=ed.add_set_member_variable_node('RobeEnabled');link(enabled,state.find_input_pin('RobeEnabled'));link(entry,state.find_execute_pin())
 branch=ed.add_branch_node();link(enabled,branch.find_input_pin('Condition'));link(state.find_then_pin(),branch.find_execute_pin())
 body=ed.add_get_member_variable_node('Body').find_output_pin_by_index(0);outfit=ed.add_get_member_variable_node('Robe').find_output_pin_by_index(0)
 for start,kind1,kind2 in [(branch.find_then_pin(),'BodyForRobe','RobeOnly'),(branch.find_output_pin('else'),'BodyForCostume','OutfitOnly')]:
  prev=start
  for comp,kind in [(body,kind1)]:
   n=ed.add_call_function_node('/Script/Engine.SkeletalMeshComponent:SetSkeletalMeshAsset');link(comp,n.find_input_pin('self'));assert n.find_input_pin('NewMesh').set_pin_value(base+'/Meshes/SK_B_1_'+kind+'_v009');link(prev,n.find_execute_pin());prev=n.find_then_pin()
  visibility=ed.add_call_function_node('/Script/Engine.SceneComponent:SetVisibility');link(outfit,visibility.find_input_pin('self'));link(enabled,visibility.find_input_pin('bNewVisibility'));link(prev,visibility.find_execute_pin());prev=visibility.find_then_pin()
  refresh=ed.add_call_function_node(bp.generated_class().get_path_name()+':K02RefreshPresentation');link(prev,refresh.find_execute_pin())
 B.compile_blueprint(bp,warnings_as_errors=True)
assert bp.get_editor_property('Status')==unreal.BlueprintStatus.BS_UP_TO_DATE
unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
print('B1 robe switch compiled; matching body swapped and separate robe toggled in one synchronous call; combat outfit retained')
