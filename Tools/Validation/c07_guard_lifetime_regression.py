"""Regression of sustained block and repeated slip/attack/guard after defense reparenting."""
from pathlib import Path
source=Path('A:/K-02 5.8/Tools/Validation/guard_lifetime_regression.py').read_text().split('k02_guard_lifetime=')[0].replace('GuardLifetime/soak.json','C07/guard-soak.json')
exec(source,globals())
class ShortGuard(GuardLifetime):
 def next(self):
  if self.i==-1:self.cases=['long_locked']+['repeat_locked','hit_locked','slip_locked','attack_locked']*2+['retry_locked']
  Test.next(self)
  if self.i<len(self.cases):self.row['index']=self.i
k02_c07_guard=ShortGuard()
