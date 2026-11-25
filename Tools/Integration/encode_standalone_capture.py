"""Encode actual client captures using measured wall-clock intervals, without interpolation."""
import json,subprocess,sys
from pathlib import Path
import imageio_ffmpeg
folder=Path(sys.argv[1]);r=json.loads((folder/'manifest.json').read_text(encoding='utf-8-sig'));assert r['error'] is None and r['frames'];out=folder/'K02-playtest.mp4';assert not out.exists()
concat=folder/'frames.ffconcat';lines=['ffconcat version 1.0']
for i,f in enumerate(r['frames']):
 assert '/' not in f['file'] and "'" not in f['file']
 lines.append("file '"+f['file']+"'");end=r['frames'][i+1]['t'] if i+1<len(r['frames']) else r['seconds'];lines.append('duration '+str(max(.001,end-f['t'])))
lines.append("file '"+r['frames'][-1]['file']+"'");concat.write_text('\n'.join(lines)+'\n')
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','warning','-f','concat','-safe','0','-i',str(concat),'-vf','fps=30','-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],check=True)
print(out)
