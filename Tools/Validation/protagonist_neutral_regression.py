from pathlib import Path
exec(Path('A:/K-02 5.8/Tools/Validation/kyokushin_tree_regression.py').read_text().split('k02_tree_test=')[0].replace('kyokushin-tree-results.json','kyokushin-neutral-results.json'),globals())
k02_neutral_test=K02TreeTest()
k02_neutral_test.cases=[('neutral_F',[(0,'F')],['M02'],False),('neutral_K',[(0,'K')],['M06'],False),('K_then_early_P',[(0,'K'),(.28,'P')],['M06'],False)]
