"""Keep montage interruption notification alive through slip blend-out."""
import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
assert 'K-02 5.8' in unreal.Paths.project_dir()
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
bp=unreal.load_asset('/Game/K02/Protagonist/Abilities/GA_K02_Slip');g=next(g for g in B.list_graphs(bp) if g.get_name()=='EventGraph')
n=next(n for n in B.find_nodes(g) if 'PlayMontageAndWait' in n.get_node_title().replace(' ',''))
info=B._get_node_info(n);pin=next(p for p in info.input_pins if p.name=='bAllowInterruptAfterBlendOut');B.set_pin_value(pin.pin_id,'true')
B.compile_blueprint(bp,warnings_as_errors=True);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
Path('A:/K-02 5.8/Saved/Diagnostics/LiveBlock/build.json').write_text(json.dumps({'asset':bp.get_path_name(),'allowInterruptAfterBlendOut':True},indent=2));unreal.log('K02_SLIP_LATE_INTERRUPT_FIXED')
