"""Fresh integration soak: native Ctrl/slip/attack, real enemy abilities, no asset writes."""
import unreal,json,time,datetime,uuid,traceback
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());params=REQUEST.get('params',{});fps=int(params.get('fps',60));assert fps in [30,60,120]
Q=ROOT/'Saved/NativeInputBridge';assert time.time()-(Q/'heartbeat.txt').stat().st_mtime<2
out=ROOT/'Saved/Diagnostics/Integration'/('guard-soak-native-rested-'+str(fps)+'.json');assert not out.exists(),'Keep prior evidence'
# Preserve the existing test conditions, replace all historical window injection/focus calls.
s=(ROOT/'Tools/Validation/combat_slip_input_regression.py').read_text().split('k02_slip_input_test=')[0]
s=s.replace('BP_K02_TrainingDummy_C','BP_K02_Enemy_C')
s=s.replace('  for a in unreal.GameplayStatics.get_all_actors_of_class','  controller=self.target.get_controller();controller.stop_movement();controller.get_editor_property("BrainComponent").stop_logic("Controlled integrated guard soak")\n  for a in unreal.GameplayStatics.get_all_actors_of_class',1)
s=s.replace("self.umg.call_method('SetInputMode_GameOnly',args=(self.pc,True));self.umg.call_method('SetFocusToGameViewport')",'pass')
exec(s,globals())
s=(ROOT/'Tools/Validation/guard_lifetime_regression.py').read_text();s=s[s.index('class GuardLifetime('):s.index('k02_guard_lifetime=')]
s=s.replace("'t.MaxFPS '+str(self.cap)","'t.MaxFPS '+str(self.cap)")
s=s.replace("self.row['attackActivated']=bool(self.asc.try_activate_ability_by_class(unreal.load_class(None,'/Game/K02/Protagonist/Abilities/GA_K02_Combo_1_1.GA_K02_Combo_1_1_C'),True))", "self.send_native('P');self.row['attackInput']='native left click'")
s=s.replace("Path('A:/K-02 5.8/Saved/Diagnostics/GuardLifetime/soak.json')",'out')
s=s.replace("['repeat_locked','hit_locked','slip_locked','attack_locked']*8+['recover_locked','retry_locked']","['repeat_locked','hit_locked','slip_locked','attack_locked','recover_locked']*8+['retry_locked']")
s=s.replace('/Game/MACS/GAS/Abilities/Fighter/GA_MACS_Fighter_Combo_1_1.GA_MACS_Fighter_Combo_1_1_C','/Game/K02/Protagonist/Abilities/GA_K02_Combo_1_1.GA_K02_Combo_1_1_C')
s=s.replace("'attributes':attrs}", "'attributes':attrs,'iframe':self.asc.call_method('GetGameplayEffectCount',args=(self.ge,None,True))}")
s=s.replace("self.row['pass']=self.row['releaseCheck'] and (self.row['heldCheck'] or self.name=='recover_locked');", """self.row['pass']=self.row['releaseCheck'] and (self.row['heldCheck'] or self.name=='recover_locked')
    ss=self.row['samples']
    if self.name=='hit_locked':
     before=[x['attributes']['Resource'] for x in ss if .6<x['t']<.79];during=[x['attributes']['Resource'] for x in ss if .9<x['t']<1.8];self.row['impactResourceDrop']=max(before,default=0)-min(during,default=999);self.row['pass']=self.row['pass'] and self.row.get('enemyActivated',False) and self.row['impactResourceDrop']>.05
    if self.name=='slip_locked':
     self.row['iframeDuration']=sum(b['t']-a['t'] for a,b in zip(ss,ss[1:]) if a['iframe']>0);self.row['slipObserved']=any('Slip_Left' in (x['montage'] or '') for x in ss);self.row['pass']=self.row['pass'] and self.row['slipObserved'] and .08<self.row['iframeDuration']<.25 and ss[-1]['iframe']==0
    if self.name=='attack_locked':
     self.row['attackObserved']=any('M01' in (x['montage'] or '') for x in ss);self.row['pass']=self.row['pass'] and self.row['attackObserved']
    """)
s=s.replace("end=13 if self.name=='long_locked' else (12 if self.name=='recover_locked' else 3)","end=13 if self.name=='long_locked' else (12 if self.name=='recover_locked' else (4.5 if self.name=='hit_locked' else 3))")
# Include native delivery results and exact frame-rate condition in the final evidence.
s=s.replace("result={'pass':", "jobs=[json.loads((Q/(j+'.result.json')).read_text(encoding='utf-8-sig')) if (Q/(j+'.result.json')).exists() else {'ok':False,'id':j} for j in self.jobs];result={'fps':fps,'native_inputs':jobs,'pass':all(j['ok'] for j in jobs) and ")
exec(s,globals())
class NativeGuardSoak(GuardLifetime):
 def __init__(self):self.jobs=[];super().__init__();unreal.SystemLibrary.execute_console_command(self.w,'t.MaxFPS '+str(fps))
 def send_native(self,key):
  ident=str(time.time_ns())+'-'+uuid.uuid4().hex[:6];tmp=Q/(ident+'.tmp');tmp.write_text(json.dumps({'id':ident,'key':key,'created':datetime.datetime.now(datetime.timezone.utc).isoformat(),'hold_seconds':15 if key=='CtrlDown' else 5}));tmp.rename(Q/(ident+'.pending.json'));self.jobs.append(ident)
 def key(self,key,down):
  self.send_native(key+('Down' if down else 'Up'))
  if down:self.held.add(key)
  else:self.held.discard(key)
k02_native_soak=NativeGuardSoak()
