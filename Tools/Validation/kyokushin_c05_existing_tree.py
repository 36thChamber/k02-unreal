"""Existing C01-C04/C08 through window inputs, without thread-input attachment.

The old test's AttachThreadInput/SetForegroundWindow path could block the editor.
This changes the automation only, retaining its sequences/contact assertions.
"""
from pathlib import Path
base=Path('A:/K-02 5.8/Tools/Validation/kyokushin_tree_regression.py').read_text().split('k02_tree_test=')[0]
base=base.replace('kyokushin-tree-results.json','C05/existing-tree.json')
params=globals().get('REQUEST',{}).get('params',{})
output=params.get('output','existing-tree')
assert output.replace('-','').replace('_','').isalnum()
base=base.replace('C05/existing-tree.json','C05/'+output+'.json')
base=base.replace("row.pop('frameTimes')", "row['maxFrameMs']=max(row['frameTimes'])*1000;row.pop('frameTimes')")
begin=base.index('  windows=[]')
end=base.index('  name,inputs',begin)
base=base[:begin]+'''  windows=[]
  def visit(h,p):
   pid=ctypes.c_ulong();ctypes.windll.user32.GetWindowThreadProcessId(h,ctypes.byref(pid));buf=ctypes.create_unicode_buffer(512);ctypes.windll.user32.GetWindowTextW(h,buf,512)
   if pid.value==os.getpid() and 'Unreal Editor' in buf.value:windows.append(h)
   return True
  ctypes.windll.user32.EnumWindows(ctypes.WINFUNCTYPE(ctypes.c_bool,ctypes.c_void_p,ctypes.c_void_p)(visit),0)
  assert windows
  self.input_hwnd=windows[0]
  unreal.get_default_object(unreal.load_class(None,'/Script/UMG.WidgetBlueprintLibrary')).call_method('SetFocusToGameViewport')
'''+base[end:]
# Keep all keys in the same window event path; do not send global desktop input.
base=base.replace("else:assert self.slate.call_method('PressKey',args=('E' if key=='K' else 'R',))", "else:\n   vk=0x45 if key=='K' else 0x52\n   ctypes.windll.user32.PostMessageW(self.input_hwnd,0x100,vk,(ctypes.windll.user32.MapVirtualKeyW(vk,0)<<16)|1)\n   self.key_release=(self.clock+.05,vk)")
base=base.replace("assert self.slate.call_method('PressKey',args=('R',));", "self.pulse('T');")
# Do not change focus/capture from a Slate tick; this can deadlock the Editor.
base=base.replace("  unreal.get_default_object(unreal.load_class(None,'/Script/UMG.WidgetBlueprintLibrary')).call_method('SetInputMode_GameOnly',args=(self.pc,True));unreal.GameplayStatics.set_viewport_mouse_capture_mode(self.w,unreal.MouseCaptureMode.CAPTURE_PERMANENTLY_INCLUDING_INITIAL_MOUSE_DOWN)\n",'')
base=base.replace("  unreal.get_default_object(unreal.load_class(None,'/Script/UMG.WidgetBlueprintLibrary')).call_method('SetFocusToGameViewport')\n",'')
base=base.replace('   self.clock=now\n', '''   self.clock=now
   if getattr(self,'key_release',None) and now>=self.key_release[0]:
    vk=self.key_release[1];ctypes.windll.user32.PostMessageW(self.input_hwnd,0x101,vk,(ctypes.windll.user32.MapVirtualKeyW(vk,0)<<16)|0xC0000001);self.key_release=None
''')
exec(base,globals())
s=Path('A:/K-02 5.8/Tools/Validation/kyokushin_c08_regression.py').read_text()
exec(s[s.index('class C08TreeTest'):].split('k02_c08_test=C08TreeTest()')[0],globals())
class SettledTree(C08TreeTest):
 def __init__(self):
  self.progress_wall=time.monotonic();super().__init__()
 def pulse(self,key):
  super().pulse(key)
  if self.mouse_release:self.mouse_release=(time.monotonic()+.05,*self.mouse_release[1:])
  if getattr(self,'key_release',None):self.key_release=(time.monotonic()+.05,self.key_release[1])
 def begin(self):
  super().begin()
  if self.cur:
   for msg in [0x202,0x205]:ctypes.windll.user32.PostMessageW(self.input_hwnd,msg,0,(450<<16)|600)
   self.start=self.clock+.5
 def tick(self,dt):
  wall=time.monotonic()
  # Releases must survive Editor/UI pauses; a game-time deadline deadlocks
  # when a mouse-down temporarily suspends world ticking in background PIE.
  if self.mouse_release and wall>=self.mouse_release[0]:
   ctypes.windll.user32.PostMessageW(self.input_hwnd,self.mouse_release[1],0,self.mouse_release[2]);self.mouse_release=None
  if getattr(self,'key_release',None) and wall>=self.key_release[0]:
   vk=self.key_release[1];ctypes.windll.user32.PostMessageW(self.input_hwnd,0x101,vk,(ctypes.windll.user32.MapVirtualKeyW(vk,0)<<16)|0xC0000001);self.key_release=None
  now=unreal.GameplayStatics.get_time_seconds(self.w)
  if now>self.clock:self.progress_wall=wall
  elif wall-self.progress_wall>3:
   self.finish('World clock stalled for 3 seconds; automation aborted without gameplay approval');return
  if self.cur:
   m=self.p.mesh.get_anim_instance().get_current_active_montage()
   if m and 'M02' in m.get_name():
    self.cur.setdefault('middlePunchContact',[]).append({'time':self.clock-self.start,'hand':self.p.mesh.get_socket_location('hand_r_Trace_Sphere').to_tuple(),'target':self.target.get_actor_location().to_tuple(),'montageTime':self.p.mesh.get_anim_instance().montage_get_position(m)})
  super().tick(dt)
k02_c08_test=SettledTree()
exec(s.split('k02_c08_test=C08TreeTest()')[1],globals())
if params.get('cases'):
 k02_c08_test.cases=[c for c in k02_c08_test.cases if c[0] in params['cases']]*int(params.get('repeat',1))
