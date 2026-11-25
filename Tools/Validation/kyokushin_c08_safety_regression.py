"""Apply existing equipment/trace/active-frame interruption checks to the new terminal hook."""
from pathlib import Path
source=Path('A:/K-02 5.8/Tools/Validation/protagonist_interruptions_regression.py').read_text().split('k02_interruptions=')[0].replace("'Combo_1_1'","'C08_HookBodyLeft'").replace('protagonist-interruptions.json','C08/safety-test.json')
exec(source,globals())
k02_c08_safety=K02Interruptions()
k02_c08_safety.cases=['startup_equip','active_equip','defense_during_active','stagger']
