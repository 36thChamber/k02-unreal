"""Real window keyboard input -> block/slip; root authority and pace checks in fresh PIE."""
import unreal,json,ctypes,os,traceback
from pathlib import Path
class Test:
 def __init__(self):
  self.w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();assert self.w
  self.p=unreal.GameplayStatics.get_player_pawn(self.w,0);self.pc=unreal.GameplayStatics.get_player_controller(self.w,0);self.m=self.p.character_movement
  self.target=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(self.w,unreal.Character) if a.get_class().get_name()=='BP_K02_TrainingDummy_C')
  for a in unreal.GameplayStatics.get_all_actors_of_class(self.w,unreal.Character):
   if a not in [self.p,self.target]:a.destroy_actor()
  self.lib=unreal.get_default_object(unreal.load_class(None,'/Script/GameplayAbilities.AbilitySystemBlueprintLibrary'));self.asc=self.lib.call_method('GetAbilitySystemComponent',args=(self.p,));self.ins=unreal.get_default_object(unreal.load_class(None,'/Script/GASToolsets.AbilitySystemInspectorToolset'))
  self.perf=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));self.old=self.perf.get_editor_property('bThrottleCPUWhenNotForeground');self.perf.set_editor_property('bThrottleCPUWhenNotForeground',False)
  self.cap=unreal.SystemLibrary.get_console_variable_float_value('t.MaxFPS');unreal.SystemLibrary.execute_console_command(self.w,'t.MaxFPS 60')
  self.umg=unreal.get_default_object(unreal.load_class(None,'/Script/UMG.WidgetBlueprintLibrary'));self.umg.call_method('SetInputMode_GameOnly',args=(self.pc,True));self.umg.call_method('SetFocusToGameViewport')
  windows=[]
  def visit(h,p):
   pid=ctypes.c_ulong();ctypes.windll.user32.GetWindowThreadProcessId(h,ctypes.byref(pid));buf=ctypes.create_unicode_buffer(512);ctypes.windll.user32.GetWindowTextW(h,buf,512)
   if pid.value==os.getpid() and 'Unreal Editor' in buf.value:windows.append(h)
   return True
  ctypes.windll.user32.EnumWindows(ctypes.WINFUNCTYPE(ctypes.c_bool,ctypes.c_void_p,ctypes.c_void_p)(visit),0);assert windows;self.h=windows[0]
  self.vks={'W':0x57,'S':0x53,'A':0x41,'D':0x44,'Ctrl':0x11,'Shift':0x10};self.held=set();self.ge=unreal.load_class(None,'/Game/K02/Protagonist/Slip/GE_K02_SlipIFrames.GE_K02_SlipIFrames_C')
  self.cases=['block_free','block_locked','slip_W','slip_S','slip_A','slip_D','plant_W','plant_A','root_still','root_W','pace_free','pace_locked','pace_sprint','pace_sprint_locked','sprint_attack','sprint_slip']
  self.rows=[];self.i=-1;self.clock=unreal.GameplayStatics.get_time_seconds(self.w);self.next();self.cb=unreal.register_slate_post_tick_callback(self.tick)
 def key(self,k,down):
  v=self.vks[k]
  # Unreal reconciles modifier state with Windows each tick; PostMessage alone is insufficient.
  if k=='Shift':ctypes.windll.user32.keybd_event(0xA0,0x2A,0 if down else 2,0)
  lp=(ctypes.windll.user32.MapVirtualKeyW(v,0)<<16)|1
  if not down:lp|=0xC0000001
  ctypes.windll.user32.PostMessageW(self.h,0x100 if down else 0x101,v,lp)
  if down:self.held.add(k)
  else:self.held.discard(k)
 def next(self):
  for k in list(self.held):self.key(k,False)
  self.i+=1
  if self.i>=len(self.cases):self.finish();return
  self.name=self.cases[self.i];self.start=self.clock;self.sent=set();self.row={'case':self.name,'samples':[]};self.rows.append(self.row)
  self.p.set_actor_location_and_rotation(unreal.Vector(-500,-400,100),unreal.Rotator(),False,True);self.target.set_actor_location_and_rotation(unreal.Vector(500,-400,100),unreal.Rotator(pitch=0,yaw=180,roll=0),False,True);self.pc.set_control_rotation(unreal.Rotator());self.m.stop_movement_immediately()
  desired=1 if 'locked' in self.name else 0
  for _ in range(4):
   if self.pc.get_editor_property('LockonMode')==desired:break
   self.pc.call_method('LockOnTargetMode')
  self.umg.call_method('SetInputMode_GameOnly',args=(self.pc,True));self.umg.call_method('SetFocusToGameViewport')
 def tick(self,dt):
  try:
   now=unreal.GameplayStatics.get_time_seconds(self.w)
   if now<=self.clock:return
   self.clock=now;t=now-self.start
   if t>=.2 and 'start' not in self.sent:
    self.sent.add('start')
    if self.name.startswith(('block','slip')):self.key('Ctrl',True)
    elif self.name!='root_still':self.key('A' if self.name=='plant_A' else 'W',True)
    if 'sprint' in self.name:self.key('Shift',True)
   if t>=.3 and self.name.startswith('slip') and 'slip' not in self.sent:self.key(self.name[-1],True);self.sent.add('slip')
   if t>=.5 and self.name.startswith(('plant','root')) and 'attack' not in self.sent:
    self.sent.add('attack');self.row['attackOrigin']=self.p.get_actor_location().to_tuple();n='Combo_4_1' if self.name.startswith('root') else 'Combo_1_1';self.row['activated']=bool(self.asc.try_activate_ability_by_class(unreal.load_class(None,'/Game/K02/Protagonist/Abilities/GA_K02_'+n+'.GA_K02_'+n+'_C'),True))
   if t>=1.15 and 'release' not in self.sent:
    self.sent.add('release')
    for k in list(self.held):self.key(k,False)
   if t>=.7 and self.name in ['sprint_attack','sprint_slip'] and 'transition' not in self.sent:
    self.sent.add('transition')
    if self.name=='sprint_attack':self.row['attackActivated']=bool(self.asc.try_activate_ability_by_class(unreal.load_class(None,'/Game/K02/Protagonist/Abilities/GA_K02_Combo_1_1.GA_K02_Combo_1_1_C'),True))
    else:self.key('Ctrl',True)
   montage=self.p.mesh.get_anim_instance().get_current_active_montage();effect=self.asc.call_method('GetGameplayEffectCount',args=(self.ge,None,True));tags=list(self.ins.call_method('GetActiveTags',args=(self.p,)))
   self.row['samples'].append({'t':t,'position':self.p.get_actor_location().to_tuple(),'speed':self.p.get_velocity().length(),'montage':montage.get_name() if montage else None,'iframe':effect,'ctrl':self.pc.is_input_key_down(self.makekey('LeftControl')),'shift':self.pc.is_input_key_down(self.makekey('LeftShift')),'tags':tags})
   if t>=2:
    ss=self.row['samples'];ms=[x['montage'] or '' for x in ss];mid=[x for x in ss if .7<x['t']<1.0]
    if self.name.startswith('block'):ok=any('BlockHold_' in m for m in ms) and 'DefenseMode' not in ' '.join(ss[-1]['tags'])
    elif self.name.startswith('slip'):
     want={'W':'Forward','S':'Backward','A':'Left','D':'Right'}[self.name[-1]];ok=any('Slip_'+want in m for m in ms) and any(x['iframe']>0 for x in ss) and ss[-1]['iframe']==0
     self.row['iframeSampleDuration']=sum(b['t']-a['t'] for a,b in zip(ss,ss[1:]) if a['iframe']>0)
    elif self.name.startswith('plant'):
     pts=[unreal.Vector(*x['position']) for x in ss if .6<x['t']<1.0 and x['montage'] and 'M01' in x['montage']];self.row['plantedDrift']=max(((p-pts[0]).length() for p in pts),default=999);ok=self.row.get('activated') and self.row['plantedDrift']<3
    elif self.name.startswith('root'):
     pts=[unreal.Vector(*x['position']) for x in ss if .5<x['t']<1.1 and x['montage'] and 'M07' in x['montage']];self.row['rootTravel']=max(((p-unreal.Vector(*self.row['attackOrigin'])).length() for p in pts),default=0);ok=self.row.get('activated') and 20<self.row['rootTravel']<170
    elif self.name in ['sprint_attack','sprint_slip']:
     before=[x for x in ss if .55<x['t']<.7];during=[x for x in ss if .8<x['t']<1.0]
     expectedMontage='M01' if self.name=='sprint_attack' else 'Slip_Forward'
     ok=any(x['speed']>490 for x in before) and any(expectedMontage in (x['montage'] or '') for x in during) and all(not any(t.endswith('.Sprint') for t in x['tags']) for x in during)
     if self.name=='sprint_attack':
      pts=[unreal.Vector(*x['position']) for x in during];self.row['plantedDrift']=max(((p-pts[0]).length() for p in pts),default=999);ok=ok and self.row['plantedDrift']<3
    else:
     expected={'pace_free':420,'pace_locked':240,'pace_sprint':520,'pace_sprint_locked':320}[self.name];self.row['measuredSpeed']=sum(x['speed'] for x in mid)/max(1,len(mid));ok=abs(self.row['measuredSpeed']-expected)<30
    self.row['pass']=bool(ok);self.next()
  except Exception:self.finish(traceback.format_exc())
 def makekey(self,name):
  k=unreal.Key();k.import_text(name);return k
 def finish(self,error=None):
  if hasattr(self,'cb'):unreal.unregister_slate_post_tick_callback(self.cb)
  for k in list(self.held):self.key(k,False)
  self.perf.set_editor_property('bThrottleCPUWhenNotForeground',self.old);unreal.SystemLibrary.execute_console_command(self.w,'t.MaxFPS '+str(self.cap))
  r={'pass':not error and len(self.rows)==len(self.cases) and all(x.get('pass') for x in self.rows),'error':error,'rows':self.rows};Path('A:/K-02 5.8/Saved/Diagnostics/CombatSlip/input-test.json').write_text(json.dumps(r,indent=2));unreal.log('K02_SLIP_INPUT_TEST '+str(r['pass'])+' '+str(error))
k02_slip_input_test=Test()
