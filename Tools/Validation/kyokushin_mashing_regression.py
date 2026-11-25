from pathlib import Path
source=Path('A:/K-02 5.8/Tools/Validation/kyokushin_tree_regression.py').read_text().split('k02_tree_test=')[0].replace('kyokushin-tree-results.json','CombatSlip/mashing-test.json')
exec(source,globals())
k02_mashing=K02TreeTest()
k02_mashing.cases=[
 ('single_P',[(0,'P')],['M01'],False),
 ('mash_C01',[(0,'P'),(.15,'F'),(.23,'F'),(.31,'F'),(.58,'K'),(.66,'K')],['M01','M02','M06'],False),
 ('mash_C02',[(0,'P'),(.15,'P'),(.23,'P'),(.31,'P'),(.58,'K'),(.66,'K')],['M01','M04','M05'],False),
 ('mash_C04',[(0,'P'),(.15,'F'),(.23,'F'),(.31,'F'),(.58,'T'),(.66,'T')],['M01','M02','M10'],False),
 ('mash_miss',[(0,'P'),(.15,'F'),(.23,'F'),(.31,'F'),(.58,'K'),(.66,'K')],['M01','M02','M06'],True)
]
