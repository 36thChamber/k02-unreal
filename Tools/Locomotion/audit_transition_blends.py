import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
D=Path('A:/K-02 5.8/Saved/Diagnostics/TransitionBlends');D.mkdir(parents=True,exist_ok=True);r={'pie':bool(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()),'blueprints':{},'montages':{},'abilities':{}}
for path in ['/Game/K02/Protagonist/Locomotion/ABP_K02_Player','/Game/K02/Protagonist/Locomotion/ABP_K02_Commun','/Game/K02/Protagonist/Locomotion/ABP_K02_Locomotion','/Game/MACS/Animations/ABP_MACS_Jump']:
 bp=unreal.load_asset(path);nodes=[];graphs=[]
 for g in B.list_graphs(bp):
  graphs.append(g.get_name())
  for n in B.find_nodes(g):
   cls=n.get_class().get_name()
   if cls.startswith('AnimGraphNode') or cls=='AnimStateTransitionNode':
    keys=list(json.loads(unreal.ToolsetLibrary.list_struct_properties(n.get_class())));keys=[k for k in keys if k=='node' or any(s in k.lower() for s in ['blend','crossfade','duration','interrupt','inertial'])]
    nodes.append({'path':n.get_path_name(),'class':cls,'values':json.loads(unreal.ToolsetLibrary.get_object_properties(n,keys))})
 r['blueprints'][path]={'graphs':graphs,'nodes':nodes}
for root in ['/Game/K02/Protagonist','/Game/K02/Animations/Montages/Kyokushin']:
 for path in unreal.EditorAssetLibrary.list_assets(root,recursive=True):
  a=unreal.load_asset(path)
  if isinstance(a,unreal.AnimMontage):r['montages'][a.get_path_name()]={'length':a.get_play_length(),'values':json.loads(unreal.ToolsetLibrary.get_object_properties(a,['blendIn','blendOut','blendOutTriggerTime','bEnableAutoBlendOut','blendModeIn','blendModeOut','blendProfileIn','blendProfileOut','slotAnimTracks']))}
  elif isinstance(a,unreal.Blueprint) and '/Abilities/' in path:
   c=unreal.get_default_object(a.generated_class());keys=list(json.loads(unreal.ToolsetLibrary.list_struct_properties(c.get_class())));keys=[k for k in keys if any(s in k.lower() for s in ['blend','montage','stop'])];r['abilities'][a.get_path_name()]=json.loads(unreal.ToolsetLibrary.get_object_properties(c,keys))
(D/'audit.json').write_text(json.dumps(r,indent=2));unreal.log('K02_TRANSITION_BLENDS_AUDITED')
