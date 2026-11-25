"""WSL client for the explicitly started local editor bridge."""
import argparse
import json
from pathlib import Path
import time
import uuid

p = argparse.ArgumentParser()
p.add_argument('script', help='Project-relative Python path')
p.add_argument('--timeout', type=float, default=60)
p.add_argument('--params', default='{}', help='JSON request parameters for the editor script')
a = p.parse_args()
root = Path(__file__).resolve().parents[2]
q = root/'Saved/IntegrationBridge'
h = json.loads((q/'heartbeat.json').read_text())
assert time.time()-h['time'] < 10, 'Editor bridge is not responsive; inspect editor/log before retrying'
name = time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8]
tmp = q/(name+'.tmp')
tmp.write_text(json.dumps({'script': a.script,'params':json.loads(a.params)}))
tmp.rename(q/(name+'.pending.json'))
result = q/(name+'.result.json')
start = time.monotonic()
while not result.exists():
    if time.monotonic()-start > a.timeout:
        raise TimeoutError(f'Job {name} still pending/running; do not resubmit mutations blindly')
    time.sleep(.25)
r = json.loads(result.read_text())
print(json.dumps(r, indent=2))
raise SystemExit(0 if r['ok'] else 1)
