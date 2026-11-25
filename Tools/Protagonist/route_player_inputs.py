import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
A=unreal.EditorAssetLibrary;ROOT='/Game/K02/Protagonist';bp=unreal.load_asset(ROOT+'/Blueprints/BP_K02_PlayerController');rows=[]
for g in B.list_graphs(bp):
 for n in B.find_nodes(g):
  p=n.find_input_pin('InAbilityToActivate')
  if not p.is_valid():continue
  old=p.get_pin_value()
  if '/Game/MACS/GAS/Abilities/Fighter/' in old:
   name=old.rsplit('.',1)[1].replace('GA_MACS_Fighter_','GA_K02_')
   if name=='GA_K02_Combo_4_1_C':name='GA_K02_Combo_5_1_C'
   new=ROOT+'/Abilities/'+name[:-2]+'.'+name
   assert p.set_pin_value(new);rows.append({'node':n.get_name(),'from':old,'to':new})
unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert A.save_loaded_asset(bp,only_if_is_dirty=False)
Path('A:/K-02 5.8/Saved/Diagnostics/protagonist-input-routes-fixed.json').write_text(json.dumps(rows,indent=2));unreal.log('K02_PLAYER_INPUTS_ROUTED '+str(len(rows)))
