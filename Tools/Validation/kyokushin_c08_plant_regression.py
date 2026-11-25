"""The new stationary punch must not translate under held movement input."""
from pathlib import Path
source=Path('A:/K-02 5.8/Tools/Validation/combat_slip_input_regression.py').read_text().split('k02_slip_input_test=')[0].replace("'Combo_1_1'","'C08_HookBodyLeft'").replace("'M01'","'M03'").replace('CombatSlip/input-test.json','C08/plant-test.json')
exec(source,globals())
class C08Plant(Test):
 def next(self):
  if self.i==-1:self.cases=['plant_W','plant_A']
  super().next()
k02_c08_plant=C08Plant()
