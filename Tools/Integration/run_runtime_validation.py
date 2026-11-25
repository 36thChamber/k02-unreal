"""Fresh PIE, native focus, unique result, and paired log segment for one runtime test."""
from pathlib import Path
import argparse,json,time,subprocess,sys
from mcp_client import call
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('script');p.add_argument('result');p.add_argument('--params',default='{}');p.add_argument('--timeout',type=float,default=120);p.add_argument('--keep-menu',action='store_true');a=p.parse_args();out=ROOT/a.result;assert out.is_relative_to(ROOT/'Saved/Diagnostics') and not out.exists(),str(out)
log=ROOT/'Saved/Logs/MultiplayerActionCombatSy.log';offset=log.stat().st_size
args=json.loads(a.params)
def pie(n,arguments={}):return call('tools/call',{'name':'call_tool','arguments':{'toolset_name':'EditorToolset.EditorAppToolset','tool_name':n,'arguments':arguments}})
def submit(script,params={}):
 r=subprocess.run([sys.executable,str(ROOT/'Tools/Integration/submit.py'),script,'--timeout','90','--params',json.dumps(params)],capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
pie('StopPIE');pie('StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':0}})
pid=json.loads((ROOT/'Saved/IntegrationBridge/heartbeat.json').read_text())['pid'];subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File','A:\\K-02 5.8\\Tools\\Integration\\focus_editor_window.ps1','-EditorPid',str(pid)],check=True,capture_output=True)
if not a.keep_menu:submit('Tools/Integration/focus_pie_input.py')
submit(a.script,args)
deadline=time.monotonic()+a.timeout
while not out.exists():
 if time.monotonic()>deadline:raise TimeoutError('Result missing; inspect ongoing test before another PIE: '+str(out))
 time.sleep(.5)
r=json.loads(out.read_text());pie('StopPIE')
with log.open('rb') as f:f.seek(offset);segment=f.read().decode(errors='replace')
out.with_suffix('.log').write_text(segment);errors=[l for l in segment.splitlines() if 'Error:' in l or 'Accessed None' in l];print(json.dumps({'file':str(out),'pass':r.get('pass'),'error':r.get('error'),'log_errors':errors}),flush=True)
assert r.get('pass') and not errors
