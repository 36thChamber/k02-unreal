"""Fresh controlled combat sessions; preserve failures without adjusting gameplay."""
import sys,json,time,subprocess
from pathlib import Path
from mcp_client import call
ROOT=Path('/mnt/a/K-02 5.8');results=[];tag=sys.argv[1] if len(sys.argv)>1 else 'native-roster';assert tag.replace('-','').isalnum()
for ident in ['B_1','B_2','B_3','B_K02','K02_F']:
 call('tools/call',{'name':'call_tool','arguments':{'toolset_name':'EditorToolset.EditorAppToolset','tool_name':'StopPIE','arguments':{}}})
 name=tag+'-'+ident+'-defense-verified-input-60';params={'cases':['low_right','low_left','low_parry'],'output':name,'enemy_presentation':ident,'fps':60,'parry_press_time':1.3}
 assert not (ROOT/'Saved/Diagnostics/C05'/(name+'.json')).exists(),'Preserve existing result; choose a new run name'
 r=subprocess.run(['python3',str(ROOT/'Tools/Integration/run_native_defense_session.py'),json.dumps(params)],capture_output=True,text=True)
 if r.returncode:print(r.stdout,r.stderr,flush=True);raise RuntimeError('Session failed')
 out=ROOT/'Saved/Diagnostics/C05'/(name+'.json');deadline=time.time()+60
 while not out.exists() and time.time()<deadline:time.sleep(.5)
 assert out.exists(),'No result; stop and inspect before retry'
 d=json.loads(out.read_text());jobs=[json.loads((ROOT/'Saved/NativeInputBridge'/(job+'.result.json')).read_text(encoding='utf-8-sig')) for row in d['rows'] for job in row.get('native_inputs',[])];summary={'character':ident,'pass':d['pass'] and all(j['ok'] for j in jobs),'native_inputs':len(jobs),'native_input_errors':[j for j in jobs if not j['ok']],'error':d['error'],'cases':[(x['case'],x.get('pass')) for x in d['rows']]};results.append(summary);print(json.dumps(summary),flush=True)
 (ROOT/'Saved/Diagnostics/Integration'/(tag+'-contact-matrix.json')).write_text(json.dumps(results,indent=2))
call('tools/call',{'name':'call_tool','arguments':{'toolset_name':'EditorToolset.EditorAppToolset','tool_name':'StopPIE','arguments':{}}})
print('Matrix complete; individual failures retained',flush=True)
