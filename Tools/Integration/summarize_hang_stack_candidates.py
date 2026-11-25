"""Offline dump analysis: executable stack pointers + nearest PE exports, NOT an unwind/PDB stack."""
from pathlib import Path
import logging,struct,bisect,json,sys
import pefile
from minidump.minidumpfile import MinidumpFile
logging.disable(logging.CRITICAL)
p=Path(sys.argv[1]);d=MinidumpFile.parse(str(p));cache={}
def locate(addr):
 m=next((m for m in d.modules.modules if m.baseaddress<=addr<m.endaddress),None)
 if not m:return
 name=m.name.split('\\')[-1];path=Path('/mnt/'+m.name[0].lower()+m.name[2:].replace('\\','/'))
 if name not in cache:
  try:
   pe=pefile.PE(str(path),fast_load=True);pe.parse_data_directories(directories=[0]);syms=sorted((x.address,x.name.decode(errors='replace')) for x in getattr(pe,'DIRECTORY_ENTRY_EXPORT',type('',(),{'symbols':[]})()).symbols if x.name);sections=[(s.VirtualAddress,s.VirtualAddress+s.Misc_VirtualSize) for s in pe.sections if s.Characteristics&0x20000000];cache[name]=(syms,sections)
  except Exception:cache[name]=([],[])
 syms,sections=cache[name];offset=addr-m.baseaddress
 if not any(a<=offset<b for a,b in sections):return
 i=bisect.bisect_right([a for a,b in syms],offset)-1
 return {'module':name,'offset':hex(offset),'nearest_export':syms[i][1] if i>=0 else None,'export_delta':hex(offset-syms[i][0]) if i>=0 else None}
rows=[]
for t in d.threads.threads:
 d.file_handle.seek(t.Stack.Rva);data=d.file_handle.read(t.Stack.DataSize);items=[]
 for i in range(0,len(data)-8,8):
  a=struct.unpack_from('<Q',data,i)[0];v=locate(a)
  if v:items.append(dict(stack_offset=hex(i),**v))
 rows.append({'thread':t.ThreadId,'instruction':locate(t.ContextObject.Rip),'candidates':items[:80]})
out=p.with_name('stack-candidates.json');out.write_text(json.dumps({'warning':'Heuristic executable pointer scan; nearest exports are not verified call frames and may include stale stack data. No private PDBs available.','threads':rows},indent=2));print(out)
print(json.dumps(rows[0],indent=2)[:6500])
