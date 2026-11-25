import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
r={}
for p in ['/Game/MACS/GAS/Abilities/Base/GA_MACS_Base_DefenseMode','/Game/K02/Protagonist/Abilities/GA_K02_Base_Combo','/Game/K02/Protagonist/Abilities/GA_K02_DefenseMode']:
 bp=unreal.load_asset(p);rows=[]
 for g in B.list_graphs(bp):
  for n in B.find_nodes(g):
   title=n.get_node_title()
   if any(k in title.lower() for k in ['stop','montage','blend']):
    row={'graph':g.get_name(),'title':title,'pins':{}}
    names=[p.name for p in B._get_node_info(n).input_pins]
    for name in [k for k in names if 'blend' in k.lower() or 'rate' in k.lower()]:
     pin=n.find_input_pin(name)
     if pin:row['pins'][name]=pin.get_pin_value()
    rows.append(row)
 r[p]=rows
Path('A:/K-02 5.8/Saved/Diagnostics/TransitionBlends/stops.json').write_text(json.dumps(r,indent=2));unreal.log('K02_TRANSITION_STOPS_AUDITED')
