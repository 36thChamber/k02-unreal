"""C07 regression after C05, with released mouse buttons and 0.5 s pose settling."""
from pathlib import Path
import unreal,ctypes,json,traceback,faulthandler
s=Path('A:/K-02 5.8/Tools/Validation/kyokushin_c07_regression.py').read_text().split('\nimport faulthandler')[0].replace('C07/test.json','C05/regression-c07.json')
exec(s,globals())
class SettledC07(C07Test):
 def next(self):
  super().next()
  if self.i<len(self.cases):
   self.mouse(False);ctypes.windll.user32.PostMessageW(self.h,0x202,0,(450<<16)|600)
   self.start=self.clock+.5
k02_settled_c07=SettledC07();k02_settled_c07.testfps=60
