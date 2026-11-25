"""Parameterize default Fighter effect and route player classes to own copies."""
import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
A=unreal.EditorAssetLibrary
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
ROOT='/Game/K02/Protagonist';report={'copies':{},'connections':[]}
assert not A.does_asset_exist(ROOT+'/Abilities/GE_K02_Fighter'),'Initial installation already exists; use update scripts'
def dup(src,dst):
 a=unreal.load_asset(dst) if A.does_asset_exist(dst) else A.duplicate_asset(src,dst);assert a;return a
def save(a):assert A.save_loaded_asset(a,only_if_is_dirty=False)
def props(a,ks):return json.loads(unreal.ToolsetLibrary.get_object_properties(a,ks))
def setprops(a,v):assert unreal.ToolsetLibrary.set_object_properties(a,json.dumps(v))
oldge='/Game/MACS/GAS/Effects/States/WeaponClass/GE_MACS_WeaponClass_Fighter'
ge=dup(oldge,ROOT+'/Abilities/GE_K02_Fighter');cdo=unreal.get_default_object(ge.generated_class())
comp=next(c for c in cdo.get_editor_property('GEComponents') if 'AbilitiesGameplayEffect' in c.get_class().get_name())
v=props(comp,['grantAbilityConfigs'])
for row in v['grantAbilityConfigs']:
 src=row['ability']['refPath'];base=src.split('.')[0];name=base.rsplit('/',1)[1].replace('GA_MACS_Fighter_','GA_K02_')
 bp=dup(base,ROOT+'/Abilities/'+name);save(bp);report['copies'][src]=bp.generated_class().get_path_name();row['ability']={'refPath':bp.generated_class().get_path_name()}
setprops(comp,v);unreal.BlueprintEditorLibrary.compile_blueprint(ge);save(ge)
# Shared characters keep the original default. Only player overrides this data.
base=unreal.load_asset('/Game/MACS/Classes/BP_MACS_Character_Base')
if 'K02FighterStyleEffect' not in B.list_variables(base):
 typ=unreal.BlueprintEditorLibrary.get_class_reference_type(unreal.GameplayEffect.static_class())
 assert unreal.BlueprintEditorLibrary.add_member_variable(base,'K02FighterStyleEffect',typ)
unreal.BlueprintEditorLibrary.compile_blueprint(base)
unreal.get_default_object(base.generated_class()).set_editor_property('K02FighterStyleEffect',A.load_blueprint_class(oldge))
g=next(g for g in B.list_graphs(base) if g.get_name()=='EventGraph');ed=unreal.BlueprintGraphEditor.get_graph_editor(g)
for n in B.find_nodes(g):
 pin=n.find_input_pin('GameplayEffectClass')
 if pin.is_valid() and oldge in pin.get_pin_value():
  getter=ed.add_get_member_variable_node('K02FighterStyleEffect');getter.set_node_pos(unreal.IntPoint(1100,-250))
  assert getter.find_output_pin('K02FighterStyleEffect').try_create_connection(pin);report['connections'].append(n.get_path_name())
unreal.BlueprintEditorLibrary.compile_blueprint(base);save(base)
inv=unreal.load_asset('/Game/MACS/Classes/Components/BP_MACS_Inventory_Comp');g=next(g for g in B.list_graphs(inv) if g.get_name()=='UpdateItemGE');ed=unreal.BlueprintGraphEditor.get_graph_editor(g)
for n in B.find_nodes(g):
 pin=n.find_input_pin('GameplayEffectClass')
 if pin.is_valid() and oldge in pin.get_pin_value():
  getter=next((x for x in B.find_nodes(g) if x.get_node_title()=='Get K02FighterStyleEffect'),None) or ed.add_get_member_variable_node('K02FighterStyleEffect',base.generated_class().get_path_name());getter.set_node_pos(unreal.IntPoint(1250,1200))
  pawn=next(x for x in B.find_nodes(g) if x.get_node_title()=='Get PawnRef')
  cast=B.create_node(g,'Utilities|Casting|CastToBP_MACS_Character_Base',unreal.IntPoint(1050,1100))
  assert pawn.find_output_pin('PawnRef').try_create_connection(cast.find_input_pin('Object'))
  assert cast.find_output_pin('AsBP MACS Character Base').try_create_connection(getter.find_self_pin())
  upstream=n.find_execute_pin().list_connected_pins()[0]
  upstream.break_single_pin_link(n.find_execute_pin())
  assert upstream.try_create_connection(cast.find_execute_pin())
  assert cast.find_then_pin().try_create_connection(n.find_execute_pin())
  assert getter.find_output_pin('K02FighterStyleEffect').try_create_connection(pin);report['connections'].append(n.get_path_name())
unreal.BlueprintEditorLibrary.compile_blueprint(inv);save(inv)
player=unreal.load_asset('/Game/K02/Prototype/Blueprints/BP_K02_Player');unreal.BlueprintEditorLibrary.compile_blueprint(player)
unreal.get_default_object(player.generated_class()).set_editor_property('K02FighterStyleEffect',ge.generated_class());save(player)
pc=dup('/Game/MACS/Classes/BP_MACS_PC',ROOT+'/Blueprints/BP_K02_PlayerController')
report['inputRoutes']=[]
for g in B.list_graphs(pc):
 for n in B.find_nodes(g):
  for pin in n.list_input_pins():
   value=pin.get_pin_value()
   if value in report['copies']:
    assert pin.set_pin_value(report['copies'][value]);report['inputRoutes'].append(n.get_path_name())
unreal.BlueprintEditorLibrary.compile_blueprint(pc);save(pc)
gm=unreal.load_asset('/Game/K02/Prototype/Blueprints/BP_K02_ArenaGameMode');unreal.get_default_object(gm.generated_class()).set_editor_property('PlayerControllerClass',pc.generated_class());unreal.BlueprintEditorLibrary.compile_blueprint(gm);save(gm)
Path('A:/K-02 5.8/Saved/Diagnostics/protagonist-isolation.json').write_text(json.dumps(report,indent=2));unreal.log('K02_PROTAGONIST_ISOLATED')
