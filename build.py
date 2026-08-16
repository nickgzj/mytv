from pathlib import Path
import re
SRC=Path('/tmp/index.m3u')
OUT=Path('mytv.m3u')
lines=SRC.read_text(encoding='utf-8',errors='ignore').splitlines()
entries=[]
for i,l in enumerate(lines):
    if l.startswith('#EXTINF') and i+1<len(lines):
        entries.append((l, lines[i+1], lines[i+2] if i+2<len(lines) and lines[i+2].startswith('#EXTVLCOPT') else None))

def meta(e):
    l,n,_=e
    return l.split(',',1)[1] if ',' in l else ''

def getid(l):
    m=re.search(r'tvg-id="([^"]*)"',l); return m.group(1) if m else ''

def flagged(l):
    return '[Geo-blocked]' in l or '[Not 24/7]' in l

def pick(pred, group, exclude_flag=True):
    seen=set(); out=[]
    for e in entries:
        l,u,opt=e; n=meta(e); tid=getid(l)
        if exclude_flag and flagged(l): continue
        if pred(l,n,tid):
            key=(tid or n,u)
            if key in seen: continue
            seen.add(key)
            l=re.sub(r'group-title="[^"]*"', f'group-title="{group}"', l)
            out.append((l,opt,u))
    return out

sections=[]
# CCTV
cctv=pick(lambda l,n,t: bool(re.match(r'CCTV-(?:[1-9]|1[0-7])(?:\s|\+|\(|$)',n)) or n.startswith('CCTV-4K') or n.startswith('CCTV-8K'), 'CCTV', True)
# prefer unique channel IDs but keep multiple quality variants
sections.append(('CCTV',cctv))

sat_keywords=['卫视','Satellite TV','SatelliteTV','Satellite Television']
# explicit satellite-like names, excluding non-satellite subchannels
sat=pick(lambda l,n,t: any(k.lower() in n.lower() for k in sat_keywords), '地方卫视', True)
# Add common Chinese satellite names where English metadata does not contain satellite
common=['Anhui TV','Hebei TV','Hunan TV','云南卫视','兵团卫视','内蒙古卫视','厦门卫视','四川卫视','天津卫视','宁夏卫视','山东卫视','新疆卫视','江苏卫视','江西卫视','浙江卫视','贵州卫视','辽宁卫视','陕西卫视','青海卫视','黑龙卫视','黑龙江','西藏卫视']
extra=pick(lambda l,n,t: any(n.startswith(x) for x in common), '地方卫视', True)
# merge
seen={(getid(l) or meta((l,u,o)),u) for l,o,u in sat}
for e in extra:
    l,o,u=e; key=(getid(l) or meta(e),u)
    if key not in seen: sat.append(e); seen.add(key)
sections.append(('地方卫视',sat))

# Taiwan all unflagged .tw entries
tw=pick(lambda l,n,t: '.tw@' in l, '台湾', True)
sections.append(('台湾',tw))
# Japan all unflagged .jp entries
jp=pick(lambda l,n,t: '.jp@' in l, '日本', True)
sections.append(('日本',jp))
# BBC: news-focused
bbc_names=['BBC News','BBC Parliament','BBC News Asia Pacific','BBC News North America','BBC News Latin America','BBC News UK HD']
bbc=pick(lambda l,n,t: any(n.startswith(x) for x in bbc_names), 'BBC', True)
sections.append(('BBC',bbc))
# US major news/business
us_ids={'ABCNewsLive1.us@SD','ABCNewsLive2.us@SD','ABCNewsLive3.us@SD','ABCNewsLive4.us@SD','ABCNewsLive5.us@SD','ABCNewsLive6.us@SD','ABCNewsLive7.us@SD','ABCNewsLive8.us@SD','ABCNewsLive9.us@SD','ABCNewsLive10.us@SD','BloombergTV.us@US','CBSNews247.us@SD','CNBC.us@SD','FoxNewsChannel.us@SD','NBCNewsNOW.us@SD'}
major=pick(lambda l,n,t: t in us_ids or n in {'ABC News (720p)','ABC News Live 1 (720p)','Bloomberg TV (1080p)','CBS News 24/7 (720p)','CNBC (720p)','CNBC (1080p)','Fox News Channel (720p)','NBC News NOW (1080p)'} or n.startswith('MSNBC') or n=='CNNi', '美国新闻财经', True)
# Bloomberg Asia is useful too
bloom=pick(lambda l,n,t: t.startswith('BloombergTV.us@Asia') and 'Live Event' not in n, '美国新闻财经', True)
seen={(getid(l) or meta((l,u,o)),u) for l,o,u in major}
for e in bloom:
    l,o,u=e; key=(getid(l) or meta(e),u)
    if key not in seen: major.append(e); seen.add(key)
sections.append(('美国新闻财经',major))

out=['#EXTM3U x-tvg-url="https://worker-9dd4.onrender.com/guide.xml.gz"']
counts={}
for title,items in sections:
    counts[title]=len(items)
    for l,opt,u in items:
        out.append(l)
        if opt: out.append(opt)
        out.append(u)
OUT.write_text('\n'.join(out)+'\n',encoding='utf-8')
print(counts, 'total entries', sum(counts.values()), 'size', OUT.stat().st_size)
