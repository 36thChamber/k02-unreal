import unreal,json,sys
from pathlib import Path
sys.path.insert(0,'A:/K-02 5.8/Tools/Protagonist')
from kyokushin_assets import *
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
r=move('M10','A_MiddleKick_R','foot_r_Trace_Sphere','Combo_4_3',10,7,11,True)
branches('M02',[('IA_MACS_Kick','1.3'),('IA_MACS_HeavyAttack_2','4.3')])
bp=ability('Combo_5_1');c=unreal.get_default_object(bp.generated_class());c.set_editor_property('AbilityMontage',unreal.load_asset(MROOT+'/AM_K02_Kyokushin_M10'));c.set_editor_property('AbilityDamage',10);unreal.BlueprintEditorLibrary.compile_blueprint(bp);save(bp)
grant(['Combo_4_3','Combo_5_1'])
Path('A:/K-02 5.8/Saved/Diagnostics/kyokushin-c04-build.json').write_text(json.dumps(r,indent=2));unreal.log('K02_KYOKUSHIN_C04_BUILT')
