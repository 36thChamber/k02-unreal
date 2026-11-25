import unreal,json,sys
from pathlib import Path
sys.path.insert(0,'A:/K-02 5.8/Tools/Protagonist')
from kyokushin_assets import *
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
r=[move('M04','A_HookBody_R_IP','hand_r_Trace_Sphere','Combo_2_2',6,7,11),move('M05','A_LowKick_L','foot_l_Trace_Sphere','Combo_2_3',8,7,11,True)]
branches('M01',[('IA_MACS_HeavyAttack_1','1.2'),('IA_MACS_LightAttack_1','2.2')]);branches('M04',[('IA_MACS_Kick','2.3')]);grant(['Combo_2_2','Combo_2_3'])
Path('A:/K-02 5.8/Saved/Diagnostics/kyokushin-c02-build.json').write_text(json.dumps(r,indent=2));unreal.log('K02_KYOKUSHIN_C02_BUILT')
