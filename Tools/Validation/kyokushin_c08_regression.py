"""Physical P/P/F inputs, short-range contacts, terminal recovery and existing tree."""
from pathlib import Path
source=Path('A:/K-02 5.8/Tools/Validation/kyokushin_tree_regression.py').read_text().split('k02_tree_test=')[0].replace('kyokushin-tree-results.json','C08/tree-test.json')
exec(source,globals())
class C08TreeTest(K02TreeTest):
 def begin(self):
  super().begin()
  if self.cur and 'C08' in self.cur['case'] and not self.cur['far']:
   self.target.set_actor_location(unreal.Vector(-640,-500,92),False,True)
   self.cur['initialDistanceCm']=70
 def tick(self,dt):
  if self.cur and 'C08' in self.cur['case']:
   m=self.p.mesh.get_anim_instance().get_current_active_montage()
   if m and 'M03' in m.get_name():self.cur.setdefault('contactSamples',[]).append({'t':self.clock-self.start,'targetDistance':self.target.get_actor_location().distance(self.p.get_actor_location()),'hand':self.p.mesh.get_socket_location('hand_l_Trace_Sphere').to_tuple(),'target':self.target.get_actor_location().to_tuple(),'montagePosition':self.p.mesh.get_anim_instance().montage_get_position(m)})
  super().tick(dt)
k02_c08_test=C08TreeTest()
k02_c08_test.cases += [
 ('C08',[(0,'P'),(.46,'P'),(.92,'F')],['M01','M04','M03'],False),
 ('C08_miss',[(0,'P'),(.46,'P'),(.92,'F')],['M01','M04','M03'],True),
 ('C08_partial',[(0,'P'),(.46,'P')],['M01','M04'],False),
 ('mash_C08',[(0,'P'),(.15,'P'),(.23,'P'),(.31,'P'),(.58,'F'),(.66,'F')],['M01','M04','M03'],False),
 ('mash_C08_miss',[(0,'P'),(.15,'P'),(.23,'P'),(.31,'P'),(.58,'F'),(.66,'F')],['M01','M04','M03'],True)
]
