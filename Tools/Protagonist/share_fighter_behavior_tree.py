"""Own copy of MACS tree; replace only Fighter ability references with the shared K02 moveset."""
import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
A=unreal.EditorAssetLibrary;assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
p='/Game/K02/Prototype/AI/BT_K02_Fighter';bt=unreal.load_asset(p) if A.does_asset_exist(p) else A.duplicate_asset('/Game/MACS/AI/BT_MACS_Demo',p);assert bt;rows=[]
for o in unreal.ObjectIterator(unreal.BTTaskNode):
 if not o.get_path_name().startswith(bt.get_path_name()+':') or 'TryToActivateAbility' not in o.get_class().get_name():continue
 abilities=list(o.get_editor_property('Ability'));new=[]
 for cls in abilities:
  src=cls.get_path_name()
  if '/Game/MACS/GAS/Abilities/Fighter/' in src:
   n=src.rsplit('.',1)[-1].replace('GA_MACS_Fighter_','GA_K02_');dst='/Game/K02/Protagonist/Abilities/'+n[:-2]+'.'+n;cls=unreal.load_class(None,dst);assert cls;rows.append({'node':o.get_name(),'before':src,'after':dst})
  new.append(cls)
 # Both native-style escape and the new short slip are available to the defensive branch.
 if any(c.get_name()=='GA_K02_Escape_C' for c in new) and not any(c.get_name()=='GA_K02_Slip_C' for c in new):new.append(A.load_blueprint_class('/Game/K02/Protagonist/Abilities/GA_K02_Slip'))
 o.set_editor_property('Ability',new)
assert A.save_loaded_asset(bt,only_if_is_dirty=False)
bp=unreal.load_asset('/Game/K02/Prototype/Blueprints/BP_K02_EnemyController');found=0
for g in B.list_graphs(bp):
 for n in B.find_nodes(g):
  if 'Run Behavior Tree' not in n.get_node_title():continue
  pin=n.find_input_pin('BTAsset')
  if pin.is_valid() and 'BT_' in pin.get_pin_value():assert pin.set_pin_value(bt.get_path_name());found+=1
assert found==1;B.compile_blueprint(bp,warnings_as_errors=True);assert A.save_loaded_asset(bp,only_if_is_dirty=False)
Path('A:/K-02 5.8/Saved/Diagnostics/CombatSlip/ai-tree-remap.json').write_text(json.dumps(rows,indent=2));unreal.log('K02_SHARED_TREE_READY')
