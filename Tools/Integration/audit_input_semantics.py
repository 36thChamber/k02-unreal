"""Read native graph pins and Enhanced Input metadata. Never deserialize asset bytes."""
import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
A=unreal.EditorAssetLibrary;registry=unreal.AssetRegistryHelpers.get_asset_registry();rows=[];scanned=0
for data in registry.get_assets_by_path('/Game/K02',True):
 if str(data.asset_class_path.asset_name) not in ['Blueprint','AnimBlueprint','GameplayAbilityBlueprint']:continue
 bp=data.get_asset();scanned+=1
 for g in B.list_graphs(bp):
  for n in B.find_nodes(g):
   title=n.get_node_title();compact=title.replace(' ','')
   if not any(s in compact for s in ['IsInputKeyDown','WasInputKeyJustPressed','WasInputKeyJustReleased','GetInputKeyTimeDown']):continue
   pin=n.find_input_pin('Key');rows.append({'asset':bp.get_path_name(),'graph':g.get_name(),'node':n.get_name(),'function':title,'key':pin.get_pin_value() if pin else None,'connections':[(p.get_owning_node().get_node_title(),str(p.get_pin_name())) for p in pin.list_connected_pins()] if pin else []})
contexts=[]
for path in ['/Game/K02/Protagonist/Inputs/IMC_K02_Abilities','/Game/MACS/Inputs/Movements/IMC_MACS_Movements','/Game/MACS/Inputs/Inventory/IMC_MACS_Inventory']:
 a=unreal.load_asset(path);contexts.append({'path':path,'data':json.loads(unreal.ToolsetLibrary.get_object_properties(a,['DefaultKeyMappings']))})
r={'scanned_blueprints':scanned,'queries':rows,'contexts':contexts,'note':'Read-only inventory for semantic remapping; no new input routing implemented'};(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/input-semantics-audit-v2.json').write_text(json.dumps(r,indent=2));print('Blueprints',scanned,'physical key queries',len(rows),'assets',sorted(set(v['asset'] for v in rows)))
