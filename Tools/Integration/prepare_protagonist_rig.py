"""Apply the proven pilot rig/ABP configuration to isolated versioned roster assets."""
import unreal,json
from pathlib import Path
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
ROOT=Path(unreal.Paths.project_dir());params=REQUEST.get('params',{})
R={'K02_Protagonist':'Dogi_v001'}
rows=[]
for ident,rev in R.items():
 if params.get('ids') and ident not in params['ids']:continue
 BASE='/Game/K02/Characters/Protagonist/'+rev
 for file in ['prepare_pilot_retarget.py','retarget_pilot_clips.py','build_pilot_runtime_abp.py']:
  path=ROOT/'Tools/Integration'/file;s=path.read_text()
  s=s.replace('/Game/K02/Validation/ImportProbeV3/B_1',BASE).replace('SK_B_1_Combined_v009','SK_K02_Dogi_Combined_v001').replace('IK_B_1','IK_'+ident).replace('RTG_Manny_B_1','RTG_Manny_'+ident).replace('ABP_B_1_Presentation','ABP_'+ident+'_Presentation').replace('_B1_Pilot','_'+ident+'_Validation')
  s=s.replace('pilot-retarget-setup.json',ident+'-retarget-setup.json').replace('pilot-clips.json',ident+'-clips.json').replace('pilot-runtime-abp.json',ident+'-runtime-abp.json')
  exec(compile(s,str(path),'exec'),{'__file__':str(path),'__name__':'__main__'})
 rows.append({'id':ident,'revision':rev,'rig':BASE+'/Rig/IK_'+ident,'retargeter':BASE+'/Rig/RTG_Manny_'+ident,'anim_blueprint':BASE+'/Animations/ABP_'+ident+'_Presentation','status':'compiled; per-character visual/contact approval pending'})
 (ROOT/'Saved/Diagnostics/Integration/protagonist-rigs.json').write_text(json.dumps(rows,indent=2))
print('Prepared',len(rows),'own presentation rigs; no combat classes changed')
