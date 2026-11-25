from pathlib import Path
source=Path('A:/K-02 5.8/Tools/Validation/obstructed_lock_camera.py').read_text().split('k02_camera_test=')[0].replace("D/'test.json'","D/'input-state.json'")
exec(source,globals())
class InputCameraTest(CameraTest):
 cases=[('cursor_menu',(-1465,-102,92),(-600,-500,92)),('look_reset',(-1465,0,92),(-1355,0,92))]
 def next(self):
  super().next()
  if self.i<len(self.cases):self.triggered=False
 def tick(self,dt):
  if not self.triggered and unreal.GameplayStatics.get_time_seconds(self.w)-self.start>.7:
   self.triggered=True
   if self.name=='cursor_menu':self.pc.call_method('ToggleShowHideMouseCursor')
   else:self.pc.reset_ignore_look_input()
  super().tick(dt)
 def finish(self,error=None):
  for row in self.rows:row['pass']=row.get('pass',False) and all(s['ignored'] for s in row['samples'])
  super().finish(error)
k02_input_camera=InputCameraTest()
