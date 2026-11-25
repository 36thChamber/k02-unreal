"""Measure real chain contact range; no synthetic damage or target teleport during hits."""
from pathlib import Path
source=Path('A:/K-02 5.8/Tools/Validation/kyokushin_tree_regression.py').read_text().split('k02_tree_test=')[0].replace('kyokushin-tree-results.json','C08/range-test.json')
exec(source,globals())
class RangeTest(K02TreeTest):
 def __init__(self):
  super().__init__();self.cases=[('range_'+str(d),[(0,'P'),(.46,'P'),(.92,'F')],['M01','M04','M03'],False) for d in [75,90,110,130]]
 def begin(self):
  super().begin()
  if self.cur:
   d=float(self.cur['case'].split('_')[-1]);self.target.set_actor_location(unreal.Vector(-710+d,-500,92),False,True);self.cur['distance']=d;self.cur['contactSamples']=[]
 def tick(self,dt):
  if self.cur:
   m=self.p.mesh.get_anim_instance().get_current_active_montage()
   if m and 'M03' in m.get_name():self.cur['contactSamples'].append({'t':self.clock-self.start,'player':self.p.get_actor_location().to_tuple(),'target':self.target.get_actor_location().to_tuple(),'hand':self.p.mesh.get_socket_location('hand_l_Trace_Sphere').to_tuple(),'montagePosition':self.p.mesh.get_anim_instance().montage_get_position(m)})
  super().tick(dt)
k02_c08_range=RangeTest()
