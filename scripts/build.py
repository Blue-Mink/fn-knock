#!/usr/bin/env python3
"""
fn-knock fnOS FPK 定制构建脚本
用法: python3 scripts/build.py <官方fn-knock的FPK路径> [输出目录=dist]

输入官方 fn-knock fnOS 包 (upstream 2.4.12.x)，产出定制版 2.4.12.7：
  1. ui/www/index.html  注入脚本：?apps=1 全屏"应用"图标页(钉标题"敲门应用"、
     官方squircle裁切图标底板、隐藏弹窗标题栏/关闭钮)
  2. ui/config          桌面三入口：敲门knock(控制台) / 敲门应用(全屏图标页) /
     敲门门户(直连7999门户)
  3. go-reauth-proxy    等长二进制补丁：门户页 <title> 中文"选择访问入口"→"敲门门户"，
     6处 " - Go Reauth Proxy" 标题后缀→空格（窗口标题=敲门门户）
  4. 图标 5 落点         官方 squircle 圆角重制（满幅+mask，mask见 assets/）
  5. manifest           版本 2.4.12.7；maintainer_url→GitHub 项目；
     distributor_url→https://www.fnknock.cn

依赖: python3 + Pillow
"""
import io, json, pathlib, re, sys, tarfile
from PIL import Image

if len(sys.argv) < 2:
    sys.exit(__doc__)
SRC = pathlib.Path(sys.argv[1])
root = pathlib.Path(__file__).resolve().parent.parent
OUT = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else root / 'dist'
OUT.mkdir(parents=True, exist_ok=True)
VER = '2.4.12.7'

# ---------- load upstream fpk ----------
with tarfile.open(SRC) as fk:
    outer = [(m, fk.extractfile(m).read() if m.isreg() else None) for m in fk]
def member(name):
    for m, data in outer:
        if m.isreg() and m.name == name:
            return data
    raise KeyError(name)
app_orig = member('app.tgz')
with tarfile.open(fileobj=io.BytesIO(app_orig)) as t:
    payload = {m.name: (t.extractfile(m).read() if m.isreg() else None) for m in t if m.isreg()}

# ---------- 1) index.html injection ----------
css = (root / 'assets/apps-overlay.css').read_text(encoding='utf-8')
js = (root / 'assets/apps-overlay.js').read_text(encoding='utf-8').replace('__APPS_CSS__', json.dumps(css))
script = '<script>\n    (function(){\n' + js + '\n    })();\n    </script>\n</body>'
s = payload['ui/www/index.html'].decode('utf-8')
assert '</body>' in s and 'aria-haspopup' not in s
payload['ui/www/index.html'] = s.replace('</body>', script, 1).encode('utf-8')

# ---------- 2) ui/config: three desktop entries ----------
cfg = json.loads(payload['ui/config'])
u = cfg['.url']
u['fn-knock.Portal'] = {
    "noDisplay": False, "allUsers": False, "fileTypes": [],
    "control": {"accessPerm": "readonly"},
    "protocol": "http", "title": "敲门应用",
    "desc": "敲门可用应用图标页（直达，无需登录）",
    "icon": "images/ICON.PNG", "type": "iframe",
    "url": "/cgi/ThirdParty/fn-knock/index.cgi/?apps=1",
}
u['fn-knock.Gateway'] = {
    "noDisplay": False, "allUsers": False, "fileTypes": [],
    "control": {"accessPerm": "readonly"},
    "protocol": "http", "port": "7999", "title": "敲门门户",
    "desc": "敲门应用门户：全部已配置子域/应用图标入口",
    "icon": "images/ICON.PNG", "type": "url", "url": "/__select__",
}
payload['ui/config'] = json.dumps(cfg, ensure_ascii=False, indent=2).encode('utf-8')

# ---------- 3) go-reauth-proxy equal-length string patch ----------
bin_data = payload['server/go-reauth-proxy-linux-amd64']
ZH_OLD = 'gateway.selectTitle": "选择访问入口'.encode()
ZH_NEW = 'gateway.selectTitle": "敲门门户      '.encode()
SUF_OLD = b'{{.Title}} - Go Reauth Proxy</title>'
SUF_NEW = b'{{.Title}}                  </title>'
assert len(ZH_OLD) == len(ZH_NEW) and len(SUF_OLD) == len(SUF_NEW)
n1, n2 = bin_data.count(ZH_OLD), bin_data.count(SUF_OLD)
assert n1 == 1 and n2 == 6, f'upstream strings mismatch: zh={n1} suffix={n2} (版本不匹配?)'
bin_data = bin_data.replace(ZH_OLD, ZH_NEW).replace(SUF_OLD, SUF_NEW)
assert len(bin_data) == len(payload['server/go-reauth-proxy-linux-amd64'])
payload['server/go-reauth-proxy-linux-amd64'] = bin_data

# ---------- 4) squircle icons (5 targets) ----------
art = Image.open(io.BytesIO(payload['ui/images/ICON_256.PNG'])).convert('RGBA').resize((512, 512), Image.LANCZOS)
mask = Image.open(root / 'assets/squircle-mask-512-alpha.png').convert('L')
out512 = art.copy(); out512.putalpha(mask)
def png(im):
    b = io.BytesIO(); im.save(b, 'PNG'); return b.getvalue()
i_root = png(out512.resize((192, 192), Image.LANCZOS))
i_256 = png(out512.resize((256, 256), Image.LANCZOS))
i_64 = png(out512.resize((64, 64), Image.LANCZOS))
for k, v in {'ui/images/ICON.PNG': i_root, 'ui/images/ICON_256.PNG': i_256, 'ui/images/ICON_64.PNG': i_64}.items():
    if k in payload:
        payload[k] = v

# ---------- 5) manifest ----------
mm = member('manifest').decode('utf-8')
mm = re.sub(r'(?m)^version(\s*)=.*$', r'version\1= ' + VER, mm)
if 'maintainer_url' in mm:
    mm = re.sub(r'(?m)^maintainer_url\s*=.*$', 'maintainer_url        = https://github.com/kci-lnk/fn-knock-turborepo', mm)
else:
    mm = mm.replace('maintainer            = kci-lnk\n',
                    'maintainer            = kci-lnk\nmaintainer_url        = https://github.com/kci-lnk/fn-knock-turborepo\n')
mm = re.sub(r'(?m)^distributor(\s*)=.*$', r'distributor\1= kci-lnk', mm)
mm = re.sub(r'(?m)^distributor_url\s*=.*$', 'distributor_url       = https://www.fnknock.cn', mm)
manifest = mm.encode('utf-8')
checksum = member('checksum') if 'checksum' in [m.name for m, _ in outer] else None

# ---------- rebuild app.tgz (member order preserved) ----------
buf = io.BytesIO()
with tarfile.open(fileobj=io.BytesIO(app_orig)) as src, tarfile.open(fileobj=buf, mode='w:gz', compresslevel=9) as dst:
    for m in src:
        if m.isreg() and m.name in payload:
            m.size = len(payload[m.name]); dst.addfile(m, io.BytesIO(payload[m.name]))
        else:
            dst.addfile(m, src.extractfile(m) if m.isreg() else None)
app_bytes = buf.getvalue()

# ---------- rebuild outer fpk ----------
repl = {'app.tgz': app_bytes, 'manifest': manifest, 'ICON.PNG': i_root, 'ICON_256.PNG': i_256}
fpk = OUT / f'fn-knock-{VER}-fnos-amd64.fpk'
with tarfile.open(fpk, 'w:gz', compresslevel=9) as dst:
    for m, data in outer:
        if m.isreg() and m.name in repl:
            m.size = len(repl[m.name]); dst.addfile(m, io.BytesIO(repl[m.name]))
        elif m.isreg():
            dst.addfile(m, io.BytesIO(data))
        else:
            dst.addfile(m, None)
print('built:', fpk)
