"""Capture the repository's proof in an isolated Chromium context."""

from datetime import datetime, timezone
import json
import html
import platform
from pathlib import Path


def capture_proof(directory: Path, channel: str | None = None) -> Path:
    from PIL import Image, ImageChops, ImageOps
    from playwright.sync_api import sync_playwright

    directory = directory.resolve()
    manifest_path = directory / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel=channel)
        context = browser.new_context(viewport={"width": 1200, "height": 1100}, device_scale_factor=1,
                                      locale="ja-JP", color_scheme="light", reduced_motion="reduce")
        page = context.new_page()
        evidence = {}
        for mode in ["overview", "before", "after"]:
            page.goto((directory / "report.html").as_uri() + f"?mode={mode}")
            page.wait_for_function("window.proofState?.ready || window.proofState?.error")
            state = page.evaluate("window.proofState")
            if not state["ready"]:
                raise ValueError(f"Proof font loading failed: {state}")
            # Chromium reports the actual font used for each visible specimen.
            session = context.new_cdp_session(page)
            session.send("DOM.enable")
            session.send("CSS.enable")
            document = session.send("DOM.getDocument")
            selector = ".specimen" if mode == "overview" else f".{mode} .specimen"
            nodes = session.send("DOM.querySelectorAll", {"nodeId": document["root"]["nodeId"], "selector": selector})
            fonts = []
            for node in nodes["nodeIds"]:
                used = session.send("CSS.getPlatformFontsForNode", {"nodeId": node})["fonts"]
                if not used or any(not f["isCustomFont"] for f in used):
                    raise ValueError(f"Unexpected specimen fallback: {used}")
                fonts.append(used)
            session.detach()
            evidence[mode] = {**state, "platform_fonts": fonts}
            if mode == "overview":
                page.screenshot(path=directory / "overview.png", full_page=True)
                (directory / "details").mkdir(exist_ok=True)
                for index, section in enumerate(page.locator("#specimens section").all()):
                    section.screenshot(path=directory / "details" / f"{index + 1:02d}.png")
            else:
                page.locator("#specimens").screenshot(path=directory / f"{mode}.png")
        manifest["capture"] = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(), "os": platform.platform(),
            "browser": browser.version, "channel": channel or "playwright-chromium",
            "headless": True, "viewport_css_px": [1200, 1100], "device_scale_factor": 1,
            "browser_zoom": 1, "rasterization": "Browser default; no smoothing override",
            "os_dpi": "Not inferred from deviceScaleFactor; headless browser capture",
            "evidence": evidence,
        }
        browser.close()
    before, after = [Image.open(directory / f"{mode}.png").convert("RGB") for mode in ["before", "after"]]
    size = (max(before.width, after.width), max(before.height, after.height))
    padded = []
    for image in [before, after]:
        canvas = Image.new("RGB", size, "white")
        canvas.paste(image, (0, 0))
        padded.append(canvas)
    difference = ImageChops.difference(*padded)
    ImageOps.invert(difference.convert("L")).save(directory / "diff.png")
    manifest["difference"] = {"method": "absolute RGB difference converted to inverted grayscale; white means equal",
                              "bbox": difference.getbbox(), "padding": "white at bottom/right if dimensions differ"}
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    gallery = '<!doctype html><meta charset="utf-8"><title>SOROEMONO screenshots</title><style>body{max-width:1200px;margin:32px auto;font:16px system-ui}img{max-width:100%}pre{white-space:pre-wrap}</style><h1>SOROEMONO ' + html.escape(manifest.get("style", "Regular")) + ' 比較画像</h1><p><a href="report.html">フォントを直接表示する比較ページ</a> · <a href="manifest.json">環境情報</a></p>'
    gallery += f'<p>{html.escape(manifest["capture"]["os"])} / Chromium {manifest["capture"]["browser"]}</p>'
    for name in ["overview", "before", "after", "diff"]:
        gallery += f'<h2>{name}</h2><a href="{name}.png"><img alt="{name}" src="{name}.png"></a>'
    (directory / "screenshots.html").write_text(gallery, encoding="utf-8")
    return directory / "overview.png"
