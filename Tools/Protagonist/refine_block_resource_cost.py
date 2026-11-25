"""Holding a Fighter guard does not drain stamina; impacts and entry cost remain native."""
import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
assert 'K-02 5.8' in unreal.Paths.project_dir()
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
bp=unreal.load_asset('/Game/K02/Protagonist/Abilities/GA_K02_DefenseMode')
g=next((g for g in B.list_graphs(bp) if g.get_name()=='ApplyAbilityCost'),None)
if not g:g=unreal.BlueprintEditorLibrary.add_function_override(bp,'ApplyAbilityCost')
assert g
B.write_graph_dsl(g,'''(fn ApplyAbilityCost ()
 (if (Ability|CheckAbilityCost)
  (Ability|ApplyGameplayEffectToOwner :GameplayEffectClass "/Game/MACS/GAS/Effects/States/GE_MACS_RecentAbilityUse.GE_MACS_RecentAbilityUse_C")
  (else (Ability|EndAbility))))''')
B.compile_blueprint(bp,warnings_as_errors=True);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
r={'graph':g.get_path_name(),'nodes':[n.get_node_title() for n in B.find_nodes(g)],'cost':json.loads(unreal.ToolsetLibrary.get_object_properties(unreal.get_default_object(bp.generated_class()),['costGameplayEffectClass']))};assert any('CheckAbilityCost' in n for n in r['nodes']);assert not any('CommitAbilityCost' in n for n in r['nodes'])
Path('A:/K-02 5.8/Saved/Diagnostics/GuardLifetime/fix-readback.json').write_text(json.dumps(r,indent=2));unreal.log('K02_GUARD_RESOURCE_FIXED')
