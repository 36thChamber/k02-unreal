"""Own local preferences; never stores campaign or combat progress."""
import unreal,json
from editor_toolset.toolsets.blueprint import BlueprintTools as B
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
A=unreal.EditorAssetLibrary;folder='/Game/K02/UI/Settings';path=folder+'/SG_K02_Preferences'
if A.does_asset_exist(path):save=A.load_asset(path)
else:
 f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.SaveGame.static_class());save=unreal.AssetToolsHelpers.get_asset_tools().create_asset('SG_K02_Preferences',folder,unreal.Blueprint.static_class(),f)
pc=A.load_asset('/Game/K02/Protagonist/Blueprints/BP_K02_PlayerController')
defs={'K02SensitivityX':('float',1.0),'K02SensitivityY':('float',1.0),'K02InvertX':('bool',False),'K02InvertY':('bool',False)}
for bp in [save,pc]:
 for n,(typ,val) in defs.items():
  if n not in B.list_variables(bp):B.add_variable(bp,n,typ)
 B.compile_blueprint(bp,warnings_as_errors=True)
 for n,(typ,val) in defs.items():B.get_default_object(bp).set_editor_property(n,val)
for n,typ,val in [('K02LookScaleX','float',1.0),('K02LookScaleY','float',1.0),('K02PreferencesLoaded','bool',False),('K02PreferencesSaved','bool',False)]:
 if n not in B.list_variables(pc):B.add_variable(pc,n,typ)
 B.compile_blueprint(pc,warnings_as_errors=True);B.get_default_object(pc).set_editor_property(n,val)
for bp in [save,pc]:assert A.save_loaded_asset(bp,False)
g=next(g for g in B.list_graphs(pc) if g.get_name()=='K02ShowTrainingMenu')
for q in ['CastToSG_K02_Preferences','GetK02SensitivityX','SetK02SensitivityX']:print(q,B.find_node_types(g,q))
print('PREFERENCE_ASSET_CREATED')
