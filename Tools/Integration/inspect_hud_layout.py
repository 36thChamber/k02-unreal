import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
U=unreal.get_default_object(unreal.load_class(None,'/Script/UMGToolSet.UMGToolSet'));r={}
for path in unreal.EditorAssetLibrary.list_assets('/Game/MACS/UI',True,False):
 if not any(s in path.lower() for s in ['hud','control','command','wb_macs_ui','demokeys']):continue
 a=unreal.load_asset(path)
 if isinstance(a,unreal.WidgetBlueprint):r[path]=U.call_method('GetWidgetDescription',args=(a,)).description
 elif isinstance(a,unreal.Blueprint):r[path]={g.get_name():[n.get_node_title() for n in B.find_nodes(g)] for g in B.list_graphs(a)}
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/hud-layout.json').write_text(json.dumps(r,indent=2));print(r)
