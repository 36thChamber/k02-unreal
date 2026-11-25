"""Native manual defense, native GAS resource-cost fixture, recovery and notice cleanup."""
import unreal,json,time,datetime,uuid,traceback
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());D=ROOT/'Saved/Diagnostics/Integration';Q=ROOT/'Saved/NativeInputBridge';W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();assert W
class Test:
 def __init__(self):
  assert time.time()-(Q/'heartbeat.txt').stat().st_mtime<2
  self.pc=unreal.GameplayStatics.get_player_controller(W,0);self.p=unreal.GameplayStatics.get_player_pawn(W,0);self.ins=unreal.get_default_object(unreal.load_class(None,'/Script/GASToolsets.AbilitySystemInspectorToolset'));lib=unreal.get_default_object(unreal.load_class(None,'/Script/GameplayAbilities.AbilitySystemBlueprintLibrary'));self.asc=lib.call_method('GetAbilitySystemComponent',args=(self.p,));self.cost=unreal.load_class(None,'/Game/MACS/GAS/Effects/AbilityCosts/GE_MACS_Base_Cost_DefenseMode.GE_MACS_Base_Cost_DefenseMode_C');self.ctx=self.asc.make_effect_context();self.start=time.monotonic();self.jobs=[];self.done=set();self.rows=[];self.checks={}
  for a in unreal.GameplayStatics.get_all_actors_of_class(W,unreal.Character):
   if a!=self.p and a.get_controller():
    c=a.get_controller();c.stop_movement();brain=c.get_editor_property('BrainComponent')
    if brain:brain.stop_logic('Defense refusal feedback fixture')
  self.handle=unreal.register_slate_post_tick_callback(self.tick)
 def send(self,key):
  ident=str(time.time_ns())+'-'+uuid.uuid4().hex[:6];p=Q/(ident+'.tmp');p.write_text(json.dumps({'id':ident,'key':key,'created':datetime.datetime.now(datetime.timezone.utc).isoformat(),'hold_seconds':8}));p.rename(Q/(ident+'.pending.json'));self.jobs.append(ident)
 def tick(self,dt):
  try:
   t=time.monotonic()-self.start
   for at,key in [(.2,'CtrlDown'),(.7,'CtrlUp'),(1.2,'CtrlDown'),(4.6,'CtrlUp'),(5.2,'CtrlDown'),(6,'CtrlUp')]:
    if t>=at and key+str(at) not in self.done:self.done.add(key+str(at));self.send(key)
   if 1<t<3.3:
    count=1002 if 'drained' not in self.done else 5;self.done.add('drained')
    for _ in range(count):self.asc.call_method('BP_ApplyGameplayEffectToSelf',args=(self.cost,1,self.ctx))
   tags=list(self.ins.call_method('GetActiveTags',args=(self.p,)));attrs={x.attribute_name:x.current_value for x in self.ins.call_method('GetAttributeValues',args=(self.p,))};u=self.pc.get_editor_property('K02CombatNotice');m=self.p.mesh.get_anim_instance().get_current_active_montage();s={'t':t,'resource':attrs['Resource'],'guard':any(x.endswith('.DefenseMode') for x in tags),'montage':m.get_name() if m else None,'notice_visible':bool(u and u.is_visible()),'notice_text':str(u.get_editor_property('NoticeText').get_text()) if u else None,'notice_visibility':str(u.get_visibility()) if u else None};self.rows.append(s)
   for at,n in [(.5,'guard_before'),(1.8,'refused_with_notice'),(4.4,'notice_cleared'),(5.7,'guard_after'),(6.5,'released')]:
    if t>=at and n not in self.done:
     self.done.add(n)
     if n=='guard_before':self.checks[n]=s['guard'] and not s['notice_visible']
     if n=='refused_with_notice':self.checks[n]=not s['guard'] and s['resource']<.1 and s['notice_visible'] and s['notice_text'].startswith('Sem recurso') and u.get_visibility()==unreal.SlateVisibility.HIT_TEST_INVISIBLE
     if n=='notice_cleared':self.checks[n]=not s['notice_visible']
     if n=='guard_after':self.checks[n]=s['resource']>=.1 and s['guard'] and not s['notice_visible']
     if n=='released':self.checks[n]=not s['guard']
   if t>6.8:self.finish()
  except Exception:self.finish(traceback.format_exc())
 def finish(self,error=None):
  unreal.unregister_slate_post_tick_callback(self.handle);jobs=[]
  for name in self.jobs:
   f=Q/(name+'.result.json');jobs.append(json.loads(f.read_text(encoding='utf-8-sig')) if f.exists() else {'id':name,'ok':False})
  r={'pass':not error and len(self.checks)==5 and all(self.checks.values()) and all(j['ok'] for j in jobs),'checks':self.checks,'error':error,'fixture':'Native existing 0.1 Resource cost applied only in PIE to keep Resource exhausted for 2.3 seconds; no asset, health or gameplay cost changes. Ctrl delivered by independent native OS worker.','native_inputs':jobs,'samples':self.rows};(D/'defense-notice-validation.json').write_text(json.dumps(r,indent=2));unreal.log('K02_DEFENSE_NOTICE '+str(r['pass']))
test=Test()
