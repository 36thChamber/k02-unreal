"""Fresh native-input sessions for defensive regressions; unique evidence per run."""
from pathlib import Path
import sys,json,time,subprocess
from mcp_client import call
ROOT=Path(__file__).resolve().parents[2];tag=sys.argv[1];assert tag.replace('-','').isalnum()
cases=['low_right','low_left','body_block','middle_block','front_block','low_miss','no_attack','no_guard','expired','direct_denied','followup_denied','mash','equip','slip_after','other_attack','far','rear','low_parry'];results=[]
def stop():
 return call('tools/call',{'name':'call_tool','arguments':{'toolset_name':'EditorToolset.EditorAppToolset','tool_name':'StopPIE','arguments':{}}})
for fps in [60,30]:
 for group in [0,1]:
  stop();name=f'{tag}-{fps}-g{group+1}';out=ROOT/'Saved/Diagnostics/C05'/(name+'.json');assert not out.exists()
  params={'cases':cases[group*9:(group+1)*9],'output':name,'fps':fps,'parry_press_time':1.3}
  r=subprocess.run([sys.executable,str(ROOT/'Tools/Integration/run_native_defense_session.py'),json.dumps(params)],capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
  deadline=time.monotonic()+110
  while not out.exists():
   if time.monotonic()>deadline:raise TimeoutError(name)
   time.sleep(.5)
  d=json.loads(out.read_text());jobs=[json.loads((ROOT/'Saved/NativeInputBridge'/(j+'.result.json')).read_text(encoding='utf-8-sig')) for row in d['rows'] for j in row.get('native_inputs',[])];summary={'name':name,'pass':d['pass'] and all(j['ok'] for j in jobs),'cases':len(d['rows']),'failed':[r['case'] for r in d['rows'] if not r['pass']],'error':d['error'],'native_inputs':len(jobs),'native_input_errors':[j for j in jobs if not j['ok']]};results.append(summary);print(json.dumps(summary),flush=True)
  stop();(ROOT/'Saved/Diagnostics/Integration'/(tag+'-summary.json')).write_text(json.dumps(results,indent=2))
  if not summary['pass']:raise RuntimeError('Regression failure; evidence preserved')
