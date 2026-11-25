"""Compile/save explicit changed assets and read native runtime references back."""
import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
A=unreal.EditorAssetLibrary;assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
paths=list(A.list_assets('/Game/K02/Protagonist',recursive=True,include_folder=False))+list(A.list_assets('/Game/K02/Animations/Montages/Kyokushin',recursive=True,include_folder=False))+['/Game/K02/Prototype/Blueprints/BP_K02_Player','/Game/K02/Prototype/Blueprints/BP_K02_ArenaGameMode','/Game/MACS/Classes/BP_MACS_Character_Base','/Game/MACS/Classes/Components/BP_MACS_Inventory_Comp']
r={'assets':[],'blueprints':[]}
for path in paths:
 o=unreal.load_asset(path)
 if isinstance(o,unreal.Blueprint):
  B.compile_blueprint(o,warnings_as_errors=True);r['blueprints'].append(o.get_path_name())
 assert A.save_loaded_asset(o,only_if_is_dirty=False);r['assets'].append(o.get_path_name())
r['playerAnim']=unreal.get_default_object(A.load_blueprint_class('/Game/K02/Prototype/Blueprints/BP_K02_Player')).mesh.get_editor_property('AnimClass').get_path_name()
r['montages']={}
for p in A.list_assets('/Game/K02/Animations/Montages/Kyokushin',recursive=True,include_folder=False):
 m=unreal.load_asset(p);r['montages'][m.get_path_name()]={'duration':m.get_play_length(),'data':json.loads(unreal.ToolsetLibrary.get_object_properties(m,['slotAnimTracks']))}
Path('A:/K-02 5.8/Saved/Diagnostics/protagonist-final-assets.json').write_text(json.dumps(r,indent=2));unreal.log('K02_PROTAGONIST_FINAL_ASSETS_SAVED '+str(len(paths)))
