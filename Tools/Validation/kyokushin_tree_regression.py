"""Physical input -> protagonist Enhanced Input -> MACS/GAS -> real contact."""
import unreal,json,time,traceback,ctypes,os
from pathlib import Path
class K02TreeTest:
 def __init__(self):
  self.w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();assert self.w
  self.p=unreal.GameplayStatics.get_player_pawn(self.w,0);self.pc=unreal.GameplayStatics.get_player_controller(self.w,0);self.target=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(self.w,unreal.Pawn) if a.get_class().get_name()=='BP_K02_TrainingDummy_C')
  for a in unreal.GameplayStatics.get_all_actors_of_class(self.w,unreal.Pawn):
   if a==self.p:continue
   c=a.get_controller()
   if c:
    c.stop_movement();brain=c.get_editor_property('BrainComponent')
    if brain:brain.stop_logic('Kyokushin regression')
  self.ins=unreal.get_default_object(unreal.load_class(None,'/Script/GASToolsets.AbilitySystemInspectorToolset'));self.slate=unreal.get_default_object(unreal.load_class(None,'/Script/SlateInspectorToolset.SlateInspectorToolset'));self.mods=unreal.SlateInspectorToolsetModifierKeys()
  self.settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));self.old=self.settings.get_editor_property('bThrottleCPUWhenNotForeground');self.settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
  for a in [self.p,self.target]:a.mesh.set_editor_property('VisibilityBasedAnimTickOption',unreal.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)
  self.oldcap=unreal.SystemLibrary.get_console_variable_float_value('t.MaxFPS');self.fps=int(Path('A:/K-02 5.8/Saved/Diagnostics/kyokushin-test-fps.txt').read_text());unreal.SystemLibrary.execute_console_command(self.w,'t.MaxFPS '+str(self.fps))
  self.cases=[('C01',[(0,'P'),(.46,'F'),(.92,'K')],['M01','M02','M06'],False),('C04',[(0,'P'),(.46,'F'),(.92,'T')],['M01','M02','M10'],False),('neutral_T',[(0,'T')],['M10'],False),('C04_miss',[(0,'P'),(.46,'F'),(.92,'T')],['M01','M02','M10'],True)]
  self.cases += [('C02',[(0,'P'),(.46,'P'),(.92,'K')],['M01','M04','M05'],False),('C02_miss',[(0,'P'),(.46,'P'),(.92,'K')],['M01','M04','M05'],True)]
  self.cases += [('C03',[(0,'FRONT_T'),(.58,'F'),(1.04,'K')],['M07','M02','M06'],False),('C03_miss',[(0,'FRONT_T'),(.58,'F'),(1.04,'K')],['M07','M02','M06'],True)]
  self.clock=unreal.GameplayStatics.get_time_seconds(self.w)
  self.mouse_release=None;self.i=-1;self.rows=[];self.cur=None;self.wait=self.clock+1.2;self.handle=unreal.register_slate_post_tick_callback(self.tick)
 def health(self):return sum(x.get_editor_property('CurrentValue') for x in self.ins.call_method('GetAttributeValues',args=(self.target,)) if x.get_editor_property('AttributeName') in ['Health','Shield'])
 def pulse(self,key):
  if key=='FRONT_T':
   self.prev_foreground=ctypes.windll.user32.GetForegroundWindow();hwnd=ctypes.windll.user32.GetForegroundWindow();ctypes.windll.user32.SetForegroundWindow(hwnd);ctypes.windll.user32.PostMessageW(getattr(self,'input_hwnd',hwnd),0x100,0x57,(ctypes.windll.user32.MapVirtualKeyW(0x57,0)<<16)|1);self.front_held=True;self.front_pending=self.clock+.12
  elif key in ['P','F']:
   down,up,flag=(0x201,0x202,1) if key=='P' else (0x204,0x205,2)
   pos=(450<<16)|600;ctypes.windll.user32.PostMessageW(self.input_hwnd,down,flag,pos);self.mouse_release=(self.clock+.05,up,pos)
  else:assert self.slate.call_method('PressKey',args=('E' if key=='K' else 'R',))
 def begin(self):
  self.i+=1
  if self.i==len(self.cases):self.finish();return
  unreal.get_default_object(unreal.load_class(None,'/Script/UMG.WidgetBlueprintLibrary')).call_method('SetInputMode_GameOnly',args=(self.pc,True));unreal.GameplayStatics.set_viewport_mouse_capture_mode(self.w,unreal.MouseCaptureMode.CAPTURE_PERMANENTLY_INCLUDING_INITIAL_MOUSE_DOWN)
  windows=[]
  def visit(hwnd,param):
   pid=ctypes.c_ulong();ctypes.windll.user32.GetWindowThreadProcessId(hwnd,ctypes.byref(pid));buf=ctypes.create_unicode_buffer(512);ctypes.windll.user32.GetWindowTextW(hwnd,buf,512)
   if pid.value==os.getpid() and ctypes.windll.user32.IsWindowVisible(hwnd):windows.append((hwnd,buf.value))
   return True
  enum=ctypes.WINFUNCTYPE(ctypes.c_bool,ctypes.c_void_p,ctypes.c_void_p)(visit);ctypes.windll.user32.EnumWindows(enum,0);h=next((h for h,title in windows if 'Preview' in title or 'Standalone' in title),ctypes.windll.user32.FindWindowW(None,'MultiplayerActionCombatSy - Unreal Editor'));current_thread=ctypes.windll.kernel32.GetCurrentThreadId();foreground_thread=ctypes.windll.user32.GetWindowThreadProcessId(ctypes.windll.user32.GetForegroundWindow(),None);attached=bool(current_thread!=foreground_thread and ctypes.windll.user32.AttachThreadInput(current_thread,foreground_thread,True));ctypes.windll.user32.BringWindowToTop(h);ctypes.windll.user32.SetForegroundWindow(h);self.input_hwnd=h
  if attached:ctypes.windll.user32.AttachThreadInput(current_thread,foreground_thread,False)
  unreal.get_default_object(unreal.load_class(None,'/Script/UMG.WidgetBlueprintLibrary')).call_method('SetInputMode_GameOnly',args=(self.pc,True));unreal.GameplayStatics.set_viewport_mouse_capture_mode(self.w,unreal.MouseCaptureMode.CAPTURE_PERMANENTLY_INCLUDING_INITIAL_MOUSE_DOWN)
  name,inputs,expected,far=self.cases[self.i];self.front_pending=None;self.front_held=False;self.release_w=None;self.p.character_movement.stop_movement_immediately();self.target.character_movement.stop_movement_immediately()
  self.p.set_actor_location_and_rotation(unreal.Vector(-710,-500,92),unreal.Rotator(pitch=0,yaw=0,roll=0),False,True);self.pc.set_control_rotation(unreal.Rotator(pitch=0,yaw=0,roll=0));self.target.set_actor_location_and_rotation(unreal.Vector(290 if far else (-540 if name.startswith('C03') else -600),-500,92),unreal.Rotator(pitch=0,yaw=180,roll=0),False,True)
  self.cur={'case':name,'inputs':inputs,'expected':expected,'far':far,'moves':[],'damageEvents':[],'before':self.health(),'minimum':self.health(),'samples':0,'frameTimes':[]};self.prev=self.health();self.fired=set();self.start=self.clock
 def tick(self,dt):
  try:
   now=unreal.GameplayStatics.get_time_seconds(self.w)
   if now<=self.clock:return
   self.clock=now
   if self.mouse_release and now>=self.mouse_release[0]:
    ctypes.windll.user32.PostMessageW(self.input_hwnd,self.mouse_release[1],0,self.mouse_release[2]);self.mouse_release=None
   if not self.cur:
    if now>=self.wait:self.begin()
    return
   row=self.cur;t=now-self.start
   if self.front_pending and now>=self.front_pending:
    assert self.slate.call_method('PressKey',args=('R',));self.front_pending=None;self.release_w=now+.1
   if self.front_held and self.release_w is not None and now>=self.release_w:
    ctypes.windll.user32.PostMessageW(getattr(self,'input_hwnd',ctypes.windll.user32.GetForegroundWindow()),0x101,0x57,(ctypes.windll.user32.MapVirtualKeyW(0x57,0)<<16)|0xC0000001);self.front_held=False
   row['samples']+=1;row['frameTimes'].append(dt)
   for i,(when,key) in enumerate(row['inputs']):
    if t>=when and i not in self.fired:self.pulse(key);self.fired.add(i)
   m=self.p.mesh.get_anim_instance().get_current_active_montage()
   if m and m.get_name().startswith('AM_K02_Kyokushin_'):
    mid=m.get_name().replace('AM_K02_Kyokushin_','')
    if not row['moves'] or mid!=row['moves'][-1]:row['moves'].append(mid)
   h=self.health();row['minimum']=min(row['minimum'],h)
   if h<self.prev-.1:row['damageEvents'].append({'time':t,'amount':self.prev-h})
   self.prev=h
   if t<2.6:return
   tags=list(self.ins.call_method('GetActiveTags',args=(self.p,)));row['ended']=not any('WeaponClass.Fighter.Combo' in x for x in tags);row['maxRootDisplacement']=self.p.get_actor_location().distance(unreal.Vector(-710,-500,92));row['pass']=row['moves']==row['expected'] and row['ended'] and (not row['damageEvents'] if row['far'] else len(row['damageEvents'])==len(row['expected']))
   row['meanFPS']=len(row['frameTimes'])/sum(row['frameTimes']);row.pop('frameTimes');self.rows.append(row);self.cur=None;self.wait=now+.6
  except Exception:self.finish(traceback.format_exc())
 def finish(self,error=None):
  ctypes.windll.user32.PostMessageW(getattr(self,'input_hwnd',ctypes.windll.user32.GetForegroundWindow()),0x101,0x57,(ctypes.windll.user32.MapVirtualKeyW(0x57,0)<<16)|0xC0000001)
  if hasattr(self,'prev_foreground'):ctypes.windll.user32.SetForegroundWindow(self.prev_foreground)
  unreal.unregister_slate_post_tick_callback(self.handle);self.settings.set_editor_property('bThrottleCPUWhenNotForeground',self.old)
  unreal.SystemLibrary.execute_console_command(self.w,'t.MaxFPS '+str(self.oldcap))
  r={'fpsCap':self.fps,'pass':not error and len(self.rows)==len(self.cases) and all(x['pass'] for x in self.rows),'error':error,'rows':self.rows};Path('A:/K-02 5.8/Saved/Diagnostics/kyokushin-tree-results.json').write_text(json.dumps(r,indent=2));unreal.log('K02_KYOKUSHIN_TREE_TEST '+str(r['pass'])+' cases='+str(len(self.rows)))
k02_tree_test=K02TreeTest()
