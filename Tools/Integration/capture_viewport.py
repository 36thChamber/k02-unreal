"""Save an actual editor viewport capture from supported MCP capture tooling."""
import base64
import json
from pathlib import Path
import sys
from mcp_client import call

out=Path(sys.argv[1])
r=call('tools/call',{'name':'call_tool','arguments':{'toolset_name':'EditorToolset.EditorAppToolset','tool_name':'CaptureViewport','arguments':{'captureTransform':None,'annotations':None,'bShowUI':False}}})
assert not r.get('result',{}).get('isError'),r
found=[]
def visit(x):
    if isinstance(x,dict):
        if 'data' in x and ('mimeType' in x or x.get('type')=='image'):
            found.append(base64.b64decode(x['data']))
        for v in x.values():visit(v)
    elif isinstance(x,list):
        for v in x:visit(v)
    elif isinstance(x,str) and x.startswith('{'):
        try:visit(json.loads(x))
        except json.JSONDecodeError:pass
visit(r)
assert len(found)==1,len(found)
out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(found[0]);print(out)
