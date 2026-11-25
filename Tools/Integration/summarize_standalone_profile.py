"""Archive a completed CSV and review its paired Standalone log."""
from pathlib import Path
import json,csv,statistics,shutil,re,argparse
p=Path(__file__).resolve().parents[2];a=argparse.ArgumentParser();a.add_argument('log');a.add_argument('evidence');args=a.parse_args();log=(p/'Saved/Logs'/args.log).read_text(errors='replace');out=p/'Saved/Diagnostics/Integration'/args.evidence;out.mkdir(exist_ok=True)
win=re.search(r'Writing CSV to file : (.*)',log).group(1).strip()
src=p/'Saved/Profiling/CSV'/Path(win.replace('\\','/')).name if win.startswith('..') else Path('/mnt/'+win[0].lower()+win[2:].replace('\\','/'))
dest=out/'performance.csv';shutil.copy2(src,dest)
with dest.open() as f:reader=csv.DictReader(f);cols=reader.fieldnames;rows=[row for row in reader if not row.get('EVENTS','').startswith('[') and row.get('FrameTime')!='FrameTime']
keys=['FrameTime','GPUTime','Exclusive/GameThread/Animation','Exclusive/GameThread/Camera','MemoryFreeMB','GPUMem/LocalUsedMB'];stats={}
for k in keys:
 vals=[]
 for row in rows[300:]:
  try:vals.append(float(row[k]))
  except (ValueError,TypeError,KeyError):pass
 if vals:stats[k]={'n':len(vals),'mean':statistics.mean(vals),'p95':sorted(vals)[int(.95*(len(vals)-1))],'p99':sorted(vals)[int(.99*(len(vals)-1))],'max':max(vals)}
manifest=out/'manifest.json';recording=json.loads(manifest.read_text(encoding='utf-8-sig')).get('recording') if manifest.exists() else None
capture_note='screen recording concurrently' if recording else 'periodic window captures; no continuous recording' if recording is False else 'capture mode not supplied'
r={'hardware':'i5-12400, 32 GB RAM, RTX 5060 Ti 16 GB','resolution':'1280x720 windowed','fps_cap':int(re.search(r't.MaxFPS = "(\d+)"',log).group(1)),'capture':'Standalone uncooked; '+capture_note+'; first 300 frames excluded from steady metrics','source_csv':win,'frame_count':len(rows),'startup_frame_max_ms':max(float(row['FrameTime']) for row in rows[:300]),'stats':stats,'errors':[s for s in log.splitlines() if 'Error:' in s or 'Accessed None' in s],'material_warnings':[s for s in log.splitlines() if 'missing usage' in s]};(out/'performance-summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
