"""Fresh PIE per FPS; no focus calls from Editor tick. Preserve every run's evidence."""
from pathlib import Path
import sys,json,time,subprocess
from mcp_client import call
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'Saved/Diagnostics/C05';base=ROOT/'Tools/Integration';tag=sys.argv[1] if len(sys.argv)>1 else 'integrated-final-tree';assert tag.replace('-','').isalnum()
def pie(name,args={}):return call('tools/call',{'name':'call_tool','arguments':{'toolset_name':'EditorToolset.EditorAppToolset','tool_name':name,'arguments':args}})
def submit(script,params={}):
 r=subprocess.run([sys.executable,str(base/'submit.py'),script,'--timeout','90','--params',json.dumps(params)],capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
results=[]
for fps in [60,30]:
 name=tag+'-'+str(fps);out=D/(name+'.json');assert not out.exists(),str(out)
 pie('StopPIE');pie('StartPIE',{'options':{'bSimulate':False,'playMode':'PlayMode_InViewPort','warmupSeconds':0}})
 subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File','A:\\K-02 5.8\\Tools\\Integration\\focus_editor_window.ps1','-EditorPid',str(json.loads((ROOT/'Saved/IntegrationBridge/heartbeat.json').read_text())['pid'])],check=True,capture_output=True)
 submit('Tools/Integration/focus_pie_input.py');(ROOT/'Saved/Diagnostics/kyokushin-test-fps.txt').write_text(str(fps))
 submit('Tools/Validation/kyokushin_c05_native_tree.py',{'output':name,'c03_distance':190,'c02_distance':100})
 deadline=time.monotonic()+100
 while not out.exists():
  if time.monotonic()>deadline:raise TimeoutError(name)
  time.sleep(1)
 r=json.loads(out.read_text());jobs=[]
 for row in r['rows']:
  for ident in row.get('native_inputs',[]):
   p=ROOT/'Saved/NativeInputBridge'/(ident+'.result.json');jobs.append(json.loads(p.read_text(encoding='utf-8-sig')) if p.exists() else {'ok':False,'id':ident})
 s={'fps':fps,'pass':r['pass'] and all(x['ok'] for x in jobs),'cases':len(r['rows']),'error':r['error'],'failed':[x['case'] for x in r['rows'] if not x['pass']],'native_inputs':len(jobs),'native_input_errors':[x for x in jobs if not x['ok']]};results.append(s);print(json.dumps(s),flush=True)
 # Stop before leaving fixture or starting the next one.
 pie('StopPIE')
 if not s['pass']:break
(ROOT/'Saved/Diagnostics/Integration'/(tag+'-summary.json')).write_text(json.dumps(results,indent=2))
