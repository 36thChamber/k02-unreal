"""C08: retain C02 low-kick branch and add terminal left body hook (P,P,F)."""
import unreal,json,sys
from pathlib import Path
sys.path.insert(0,'A:/K-02 5.8/Tools/Protagonist')
from kyokushin_assets import *
from editor_toolset.toolsets.blueprint import BlueprintTools as B
assert 'K-02 5.8' in unreal.Paths.project_dir()
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
name='C08_HookBodyLeft';dst=ROOT+'/Abilities/GA_K02_'+name
assert not A.does_asset_exist(dst),'C08 already authored; use targeted refinements'
bp=A.duplicate_asset(ROOT+'/Abilities/GA_K02_Combo_2_3',dst);assert bp
c=unreal.get_default_object(bp.generated_class());v=props(c,['abilityTags','activationOwnedTags'])
for container in v.values():
 for tag in container['gameplayTags']:
  if tag['tagName'].endswith('.Combo.2.3'):tag['tagName']=tag['tagName'].replace('.Combo.2.3','.Combo.4.4')
setprops(c,v);B.compile_blueprint(bp,warnings_as_errors=True)
r=move('M03','A_HookBody_L_IP','hand_l_Trace_Sphere',name,7,7,11,True)
# Keep the same smooth blending as the existing right hook.
m=unreal.load_asset(MROOT+'/AM_K02_Kyokushin_M03');right=unreal.load_asset(MROOT+'/AM_K02_Kyokushin_M04');setprops(m,props(right,['blendIn','blendOut']));save(m)
branches('M04',[('IA_MACS_Kick','2.3'),('IA_MACS_HeavyAttack_1','4.4')])
grant([name]);B.compile_blueprint(bp,warnings_as_errors=True);save(bp)
ge=unreal.load_asset(ROOT+'/Abilities/GE_K02_Fighter');B.compile_blueprint(ge,warnings_as_errors=True);save(ge)
r['branchFrom']='M04';r['input']='P,P,F';r['terminal']=True;r['blend']=props(m,['blendIn','blendOut']);r['abilityConfig']=props(c,['abilityTags','activationOwnedTags','activationRequiredTags','AbilityDamage'])
Path('A:/K-02 5.8/Saved/Diagnostics/C08/build.json').write_text(json.dumps(r,indent=2));unreal.log('K02_C08_BUILT')
