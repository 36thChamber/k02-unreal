"""Serialized local Windows loopback MCP calls from WSL; no editor focus changes."""
import base64
import json
import subprocess
import sys

def call(method, params=None):
    payload=json.dumps({'jsonrpc':'2.0','id':1,'method':method,'params':params or {}})
    encoded=base64.b64encode(payload.encode()).decode()
    ps="$ProgressPreference='SilentlyContinue'; if (!(Test-Path 'A:/K-02 5.8/Saved/k02-mcp-session.txt')) { $init=Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8000/mcp' -Method POST -ContentType 'application/json' -Body '{\"jsonrpc\":\"2.0\",\"id\":0,\"method\":\"initialize\",\"params\":{\"protocolVersion\":\"2024-11-05\",\"capabilities\":{},\"clientInfo\":{\"name\":\"K02Local\",\"version\":\"1\"}}}'; $init.Headers['Mcp-Session-Id'] | Set-Content 'A:/K-02 5.8/Saved/k02-mcp-session.txt' }; $sid=(Get-Content 'A:/K-02 5.8/Saved/k02-mcp-session.txt').Trim(); $body=[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('"+encoded+"')); (Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8000/mcp' -Method POST -ContentType 'application/json' -Headers @{Accept='application/json, text/event-stream'; 'Mcp-Session-Id'=$sid} -Body $body -TimeoutSec 60).Content"
    r=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',base64.b64encode(ps.encode('utf-16le')).decode()],capture_output=True)
    if r.returncode: raise RuntimeError(r.stderr.decode(errors='replace'))
    raw=r.stdout.decode('utf-8-sig',errors='replace').strip()
    if raw.startswith('event:') or raw.startswith('data:'):
        raw=next(x[5:].strip() for x in raw.splitlines() if x.startswith('data:'))
    return json.loads(raw)

if __name__=='__main__':
    print(json.dumps(call(sys.argv[1],json.loads(sys.argv[2]) if len(sys.argv)>2 else None),ensure_ascii=False,indent=2))
