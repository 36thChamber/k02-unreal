from pathlib import Path
exec(Path('A:/K-02 5.8/Tools/Validation/protagonist_interruptions_regression.py').read_text().split('k02_interruptions=')[0].replace('protagonist-interruptions.json','protagonist-neutral-kick-interruption.json'),globals())
k02_neutral_commitment=K02Interruptions()
k02_neutral_commitment.cases=['neutral_kick_defense']
