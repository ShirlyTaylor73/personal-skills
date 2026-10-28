"""技能包静态自检；不替代绘图和Office渲染验收。仅需Python标准库。"""
from pathlib import Path
import re,xml.etree.ElementTree as E,json,hashlib

root=Path(__file__).resolve().parents[1]
skill=(root/'SKILL.md').read_text(encoding='utf-8-sig')
assert skill.startswith('---\n')
front=skill.split('---',2)[1]
assert re.search(r'^name: nsfc-diagrams$',front,re.M)
desc=re.search(r'^description: "(.+)"$',front,re.M).group(1)
assert len(desc)<1024 and '<' not in desc and '>' not in desc
links=0
for p in root.rglob('*.md'):
    for link in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8-sig')):
        if '://' in link or link.startswith('#'):continue
        assert (p.parent/link.split('#')[0]).exists(),(p,link)
        links+=1
for p in root.rglob('*.svg'):
    d=E.parse(p);ids=[x.get('id') for x in d.iter() if x.get('id')]
    assert len(ids)==len(set(ids)),p
    assert list(d.iter('{http://www.w3.org/2000/svg}text')),p
    for x in d.iter():
        for val in x.attrib.values():
            for ident in re.findall(r'url\(#([^)]+)\)',val):assert ident in ids,(p,ident)
mech=(root/'references/templates/mechanism.md').read_text(encoding='utf-8-sig')
frame=(root/'references/templates/framework.md').read_text(encoding='utf-8-sig')
assert '宋体' in mech and '#0E2841' in frame and '不固定四块' in frame
assert 'Microsoft YaHei' in frame or '微软雅黑' in frame
assert 'tx2' in (root/'references/style.md').read_text(encoding='utf-8-sig')
print(f'通过：frontmatter简式检查、{links}个相对链接、全部SVG资源与两种模板规则。')
manifest=root/'assets/reference-manifest.json'
if manifest.exists():
    records=json.loads(manifest.read_text(encoding='utf-8'))
    for item in records:
        p=root/'assets'/item['asset'];assert p.exists(),p
        assert hashlib.sha256(p.read_bytes()).hexdigest()==item['asset_sha256'],p
    assert len(records)==19
    assert not (root/'assets/examples').exists()
    print('通过：19项真实参考的路径、哈希和来源清单；自制示例已移出主要assets。')
