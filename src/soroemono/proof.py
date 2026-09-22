"""Self-contained proof: copy one HTML file to a VM; no font installation."""

import base64
import html
import json
from pathlib import Path
import subprocess

from fontTools.ttLib import TTFont

from .sources import baseline_path, digest
from .validation import check

SAMPLES = [
    ("字形 / 14px・16px・20px", "元 元元 元気な日本語\n日 国 語 あいうえお アイウエオ", "sizes"),
    ("半角カナ / 1:2のセル", "|12345678901234567890|\n|ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄ|\n|日本語全角十文字確認|\n|ｶﾞｷﾞｸﾞｹﾞｺﾞﾊﾟﾋﾟﾌﾟﾍﾟﾎﾟ|", "grid"),
    ("コード / calt ON", "const message = '日本語';\nif (a !== b && x >= 10) {\n  return value => value + 1;\n}\n// 0 O 1 I l : != === -> =>", "code"),
    ("結合文字・異体字・全角記号", "ガ ガ パ パ あ゙ か゚\ná Ä i̇́  葛 葛󠄀 辻 辻󠄀\n｛全角｝ {ASCII} ⚡ ﹢\n┌────┬────┐\n│日本│語幅│\n└────┴────┘", "marks"),
    ("通常の行送り / line-height: normal", "日本語とEnglish、元の字形\nAgjqp あいうえお ｱｲｳｴｵ\n日本語とEnglish、元の字形\nAgjqp あいうえお ｱｲｳｴｵ", "normal"),
]


def make_proof(root: Path, candidate: Path, output: Path | None = None) -> Path:
    output = output or root / "build" / "proofs" / "regular"
    baseline = baseline_path(root)
    checks = check(root, candidate)
    for font_path in [baseline, candidate]:
        font = TTFont(font_path)
        cmap = font.getBestCmap()
        uvs = {(cp, vs) for t in font["cmap"].tables if t.format == 14
               for vs, entries in t.uvsDict.items() for cp, _ in entries}
        for _, text, _ in SAMPLES:
            for i, char in enumerate(text):
                cp = ord(char)
                if char == "\n":
                    continue
                if 0xE0100 <= cp <= 0xE01EF:
                    if not i or (ord(text[i-1]), cp) not in uvs:
                        raise ValueError(f"Missing proof IVS: {font_path}, U+{cp:X}")
                elif cp not in cmap:
                    raise ValueError(f"Missing proof character: {font_path}, U+{cp:04X}")
    fonts = {"before": baseline, "after": candidate}
    manifest = {
        "fonts": {key: {"sha256": digest(path.read_bytes()), "filename": path.name}
                  for key, path in fonts.items()},
        "checks": checks, "samples": SAMPLES,
        "settings": {"font_sizes_css_px": [14, 16, 20], "font_weight": 400,
                     "font_synthesis": "none", "calt": True, "letter_spacing": 0,
                     "line_height": "1.65; normal in the last specimen"},
        "capture": None,
    }
    try:
        manifest["commit"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        manifest["working_tree_dirty"] = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip())
    except (OSError, subprocess.CalledProcessError):
        manifest["commit"] = None
    font_css = "\n".join(
        f"@font-face {{font-family: Proof{key}; src: url(data:font/ttf;base64,{base64.b64encode(path.read_bytes()).decode()}) format('truetype'); font-weight:400; font-style:normal;}}"
        for key, path in fonts.items()
    )
    cards = []
    for label, text, kind in SAMPLES:
        specimens = []
        for mode in fonts:
            sizes = [14, 16, 20] if kind == "sizes" else [16]
            content = "".join(f'<pre class="specimen {kind}" style="font-size:{size}px">{html.escape(text)}</pre>' for size in sizes)
            specimens.append(f'<div class="cell {mode}" data-mode="{mode}">{content}</div>')
        cards.append(f'<section><h2>{html.escape(label)}</h2><div class="pair">{"".join(specimens)}</div></section>')
    document = TEMPLATE.replace("__FONT_CSS__", font_css).replace("__CARDS__", "".join(cards))
    document = document.replace("__MANIFEST__", json.dumps(manifest, ensure_ascii=False).replace("<", "\\u003c"))
    licenses = "\n\n".join((root / "resource" / name / "OFL.txt").read_text()
                            for name in ["JetBrainsMono", "BIZUDGothic"])
    document = document.replace("__LICENSES__", html.escape(licenses))
    output.mkdir(parents=True, exist_ok=True)
    (output / "report.html").write_text(document, encoding="utf-8")
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output / "report.html"


TEMPLATE = r'''<!doctype html>
<html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SOROEMONO · Regular proof</title>
<style>
__FONT_CSS__
* {box-sizing:border-box} body {margin:0;background:#f2f3f5;color:#17212b;font:14px system-ui,sans-serif}
main {max-width:1160px;margin:auto;padding:32px} h1 {font-size:28px;margin:0 0 8px} p {line-height:1.8}
.eyebrow {color:#56706a;font-size:12px;font-weight:700;letter-spacing:.12em} .muted {color:#62717e}
nav {display:flex;gap:10px;margin:20px 0} a {color:#236f61} nav a {background:white;padding:8px 16px;border-radius:6px;text-decoration:none}
#status {padding:12px;background:#fff1ca;border-radius:6px;margin:16px 0} #status.ready {background:#ddefe9} #status.error {background:#ffd9d9}
.pair {display:grid;grid-template-columns:1fr 1fr;gap:20px} .labels {font-weight:650;margin:20px 0 8px}
section {background:white;border:1px solid #dce2e6;border-radius:8px;padding:16px 20px;margin:12px 0}
h2 {font:600 12px system-ui;color:#62717e;margin:0 0 12px;letter-spacing:.04em}
.cell {min-width:0;overflow:visible}.before {font-family:Proofbefore}.after {font-family:Proofafter}
pre {font-family:inherit;font-weight:400;font-style:normal;font-synthesis:none;letter-spacing:0;line-height:1.65;margin:6px 0;white-space:pre;font-feature-settings:'calt' 1;font-kerning:none}
.sizes + .sizes {margin-top:16px} .normal {line-height:normal}
.single main {max-width:1160px} .single .pair {grid-template-columns:1fr} .single .cell {min-height:0}
.single section {min-height:0} .single.before-only .after,.single.after-only .before {display:none}
details {margin:20px 0} #metadata {font:12px/1.5 ui-monospace,monospace;white-space:pre-wrap;overflow-wrap:anywhere}
</style><main>
<div class="eyebrow">SOROEMONO / REGULAR / FIRST PREVIEW</div>
<h1>日本語の見た目を保ち、文字幅を揃える。</h1>
<p class="muted">公開 v1.0.0 と新ビルドの比較。フォントはこのHTMLから読み込み、OSへのインストールは不要です。</p>
<nav><a href="?mode=overview">並べて比較</a><a href="?mode=before">旧版のみ</a><a href="?mode=after">新版のみ</a></nav>
<div id="status" role="status">フォントを読み込んでいます…</div>
<div class="pair labels"><div class="before">BEFORE · v1.0.0</div><div class="after">AFTER · Preview Regular</div></div>
<div id="specimens">__CARDS__</div>
<p class="muted">確認点：元の字形／半角カナの500→600／全角1200／濁点とIVS／通常行送り。Windows実アプリでの受け入れ確認は別途必要です。</p>
<details><summary>フォントと表示環境の記録</summary><pre id="metadata"></pre></details>
<details><summary>入力フォントの著作権表示・OFL</summary><pre style="font:12px/1.5 monospace;white-space:pre-wrap">__LICENSES__</pre></details>
</main><script>
const manifest = __MANIFEST__;
window.proofState = {ready:false,error:null};
const mode = new URLSearchParams(location.search).get('mode');
if (mode === 'before' || mode === 'after') document.body.className = `single ${mode}-only`;
(async () => {
 try {
   for (const family of ['Proofbefore','Proofafter']) {
     const faces = await document.fonts.load(`16px ${family}`, '元ｱAあ゙');
     if (faces.length !== 1 || faces[0].status !== 'loaded') throw Error(`Font load failed: ${family}`);
   }
   await document.fonts.ready;
   await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
   const canvas = document.createElement('canvas'), ctx = canvas.getContext('2d');
   const metrics = {};
   for (const key of ['before','after']) {
     ctx.font = `100px Proof${key}`;
     metrics[key] = Object.fromEntries(['A','日','ｱ'].map(s => [s,ctx.measureText(s).width]));
   }
   if (Math.abs(metrics.after.A-60)>.01 || Math.abs(metrics.after['日']-120)>.01 || Math.abs(metrics.after['ｱ']-60)>.01) throw Error('Unexpected preview cell widths');
   window.proofState = {ready:true,error:null,metrics,userAgent:navigator.userAgent,
     devicePixelRatio,viewport:[innerWidth,innerHeight],screen:[screen.width,screen.height],
     normalLineBoxes:[...document.querySelectorAll('.normal')].map(e=>({mode:e.parentElement.dataset.mode,height:e.getBoundingClientRect().height}))};
   document.querySelector('#status').className='ready';
   document.querySelector('#status').textContent='読み込み・文字幅確認 OK · 半角600 / 全角1200 · Regular';
   document.querySelector('#metadata').textContent=JSON.stringify({manifest,environment:window.proofState},null,2);
 } catch (error) {
   window.proofState.error=String(error);
   document.querySelector('#status').className='error';
   document.querySelector('#status').textContent=String(error);
 }
})();
</script></html>'''
