"""WSL orchestration: fresh PIE and input focus immediately before native test."""
import sys,json,subprocess
from pathlib import Path
from mcp_client import call
root=Path('/mnt/a/K-02 5.8');params=json.loads(sys.argv[1]);pid=json.loads((root/'Saved/IntegrationBridge/heartbeat.json').read_text())['pid']
r=call('tools/call',{'name':'call_tool','arguments':{'toolset_name':'EditorToolset.EditorAppToolset','tool_name':'StartPIE','arguments':{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':0}}}});print(r)
subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File','A:\\K-02 5.8\\Tools\\Integration\\focus_editor_window.ps1','-EditorPid',str(pid)],check=True)
for script,args in [('Tools/Integration/focus_pie_input.py',[]),('Tools/Validation/kyokushin_c05_native_defense.py',['--params',json.dumps(params)])]:
 subprocess.run(['python3',str(root/'Tools/Integration/submit.py'),script,'--timeout','30',*args],check=True)
