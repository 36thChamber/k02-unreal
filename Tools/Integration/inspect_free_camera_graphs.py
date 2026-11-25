import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
bp=unreal.load_asset('/Game/K02/Protagonist/Blueprints/BP_K02_PlayerController')
r={g.get_name():B.read_graph_dsl(g) for g in B.list_graphs(bp) if g.get_name() in ['K02ApplyFreeOrientation','K02TrackLockedTarget','K02EnterCameraLock','K02ExitCameraLock','K02ApplyLockedFraming','K02ConsiderCameraOrbit']}
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/free-camera-graphs-before.json').write_text(json.dumps(r,indent=2));print(r)
