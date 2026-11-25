import gc,ctypes,unreal
for o in gc.get_objects():
 if type(o).__name__=='SettledTree' and getattr(o,'cur',None):
  for msg in [0x202,0x205]:ctypes.windll.user32.PostMessageW(o.input_hwnd,msg,0,(450<<16)|600)
  o.mouse_release=None;o.finish('Aborted: game-time mouse release waited on world ticking; replacing with wall-clock release')
print('Released automation buttons and terminated stalled harness')
