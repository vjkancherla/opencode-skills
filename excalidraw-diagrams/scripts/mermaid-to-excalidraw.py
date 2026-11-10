#!/usr/bin/env python3
"""Convert a Mermaid flowchart to .excalidraw JSON + .svg + .png.

Uses Excalidraw's official @excalidraw/mermaid-to-excalidraw converter inside
headless Chrome (it needs a real DOM), then renders the resulting element
geometry to SVG and rasterizes it.

Usage:
    mermaid-to-excalidraw.py <input.mmd> <out-dir> [--scale 2]

Requires python3, Google Chrome, and network access to esm.sh.
Set CHROME=/path/to/chrome if auto-detection fails.
"""

import base64
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

CHROME_CANDIDATES = [
    os.environ.get("CHROME", ""),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
]

REQUIRED = set(
    "id type x y width height seed version versionNonce strokeColor "
    "backgroundColor fillStyle strokeWidth strokeStyle roughness opacity "
    "groupIds roundness isDeleted".split()
)

# Runs in the browser. Kept in one place so the Python side stays dumb.
BROWSER_JS = r"""
const SRC = __SOURCE__;
const esc = (s) => String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;")
  .replace(/>/g,"&gt;").replace(/"/g,"&quot;");

function render(elements) {
  let minX = 1e9, minY = 1e9, maxX = -1e9, maxY = -1e9;
  for (const e of elements) {
    minX = Math.min(minX, e.x); minY = Math.min(minY, e.y);
    maxX = Math.max(maxX, e.x + e.width); maxY = Math.max(maxY, e.y + e.height);
  }
  const pad = 28;
  const W = Math.ceil(maxX - minX + pad * 2);
  const H = Math.ceil(maxY - minY + pad * 2);
  const ox = pad - minX, oy = pad - minY;
  let body = "";
  const unknown = {};

  for (const e of elements) {
    const stroke = e.strokeColor || "#1e1e1e";
    const sw = e.strokeWidth || 2;
    const dash = e.strokeStyle === "dashed" ? ' stroke-dasharray="8 6"' : "";
    const fill = (e.backgroundColor && e.backgroundColor !== "transparent")
      ? e.backgroundColor : "none";

    if (e.type === "rectangle") {
      const r = e.roundness ? Math.min(14, Math.min(e.width, e.height) * 0.18) : 0;
      body += `<rect x="${e.x + ox}" y="${e.y + oy}" width="${e.width}" height="${e.height}"`
        + ` rx="${r}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}"${dash}/>`;
    } else if (e.type === "arrow") {
      const pts = (e.points || [[0, 0], [e.width, e.height]])
        .map((p) => [e.x + ox + p[0], e.y + oy + p[1]]);
      const d = pts.map((p, i) => (i ? "L" : "M") + p[0].toFixed(1) + " " + p[1].toFixed(1)).join(" ");
      body += `<path d="${d}" fill="none" stroke="${stroke}" stroke-width="${sw}"${dash}`
        + ` stroke-linecap="round" stroke-linejoin="round"/>`;
      if (e.endArrowhead === "arrow" && pts.length > 1) {
        const [x1, y1] = pts[pts.length - 2];
        const [x2, y2] = pts[pts.length - 1];
        const a = Math.atan2(y2 - y1, x2 - x1), L = 13, Wd = 5.5;
        const p1 = [x2 - Math.cos(a) * L - Math.sin(a) * Wd, y2 - Math.sin(a) * L + Math.cos(a) * Wd];
        const p2 = [x2 - Math.cos(a) * L + Math.sin(a) * Wd, y2 - Math.sin(a) * L - Math.cos(a) * Wd];
        body += `<path d="M${x2.toFixed(1)} ${y2.toFixed(1)} L${p1[0].toFixed(1)} ${p1[1].toFixed(1)}`
          + ` L${p2[0].toFixed(1)} ${p2[1].toFixed(1)} Z" fill="${stroke}"/>`;
      }
    } else if (e.type === "text") {
      const fs = e.fontSize || 20;
      const lh = (e.lineHeight || 1.25) * fs;
      const lines = String(e.text || "").split("\n");
      const total = lines.length * lh;
      let startY = e.y + oy;
      if (e.verticalAlign === "middle") startY += (e.height - total) / 2;
      const anchor = e.textAlign === "center" ? "middle" : e.textAlign === "right" ? "end" : "start";
      const tx = e.textAlign === "center" ? e.x + ox + e.width / 2
        : e.textAlign === "right" ? e.x + ox + e.width : e.x + ox;
      const spans = lines.map((ln, i) =>
        `<tspan x="${tx.toFixed(1)}" y="${(startY + i * lh + fs * 0.82).toFixed(1)}">${esc(ln)}</tspan>`
      ).join("");
      body += `<text paint-order="stroke" stroke="#ffffff" stroke-width="6" stroke-linejoin="round"`
        + ` font-family="Inter, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="${fs}"`
        + ` fill="${stroke}" text-anchor="${anchor}">${spans}</text>`;
    } else if (e.type === "diamond") {
      const x1 = e.x + ox, y1 = e.y + oy, w = e.width, h = e.height;
      const pts = [[x1 + w / 2, y1], [x1 + w, y1 + h / 2], [x1 + w / 2, y1 + h], [x1, y1 + h / 2]];
      const attr = pts.map((p) => p.map((v) => v.toFixed(1)).join(",")).join(" ");
      body += `<polygon points="${attr}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}"${dash}/>`;
    } else if (e.type === "ellipse") {
      body += `<ellipse cx="${(e.x + ox + e.width / 2).toFixed(1)}" cy="${(e.y + oy + e.height / 2).toFixed(1)}"`
        + ` rx="${(e.width / 2).toFixed(1)}" ry="${(e.height / 2).toFixed(1)}"`
        + ` fill="${fill}" stroke="${stroke}" stroke-width="${sw}"${dash}/>`;
    } else if (e.type === "line") {
      const pts = (e.points || [[0, 0], [e.width, e.height]])
        .map((p) => [e.x + ox + p[0], e.y + oy + p[1]]);
      const d = pts.map((p, i) => (i ? "L" : "M") + p[0].toFixed(1) + " " + p[1].toFixed(1)).join(" ");
      body += `<path d="${d}" fill="none" stroke="${stroke}" stroke-width="${sw}"${dash}`
        + ` stroke-linecap="round" stroke-linejoin="round"/>`;
    } else {
      unknown[e.type] = (unknown[e.type] || 0) + 1;
    }
  }
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}"`
    + ` viewBox="0 0 ${W} ${H}"><rect width="${W}" height="${H}" fill="#ffffff"/>${body}</svg>`;
  return { svg, unknown };
}

const b64 = (s) => btoa(unescape(encodeURIComponent(s)));

try {
  const { parseMermaidToExcalidraw } =
    await import("https://esm.sh/@excalidraw/mermaid-to-excalidraw@1.1.2");
  const X = await import("https://esm.sh/@excalidraw/excalidraw@0.18.0");

  const { elements: skeleton } = await parseMermaidToExcalidraw(SRC);
  const elements = X.convertToExcalidrawElements(skeleton);
  const scene = {
    type: "excalidraw", version: 2, source: "https://excalidraw.com",
    elements, appState: { gridSize: null, viewBackgroundColor: "#ffffff" }, files: {},
  };
  const rendered = render(elements);
  document.getElementById("out").textContent = JSON.stringify({
    json: b64(JSON.stringify(scene, null, 1)),
    svg: b64(rendered.svg),
    unknown: rendered.unknown,
    count: elements.length,
  });
} catch (e) {
  document.getElementById("out").textContent = "ERR " + e.message + " :: " + String(e.stack).slice(0, 300);
}
"""


def find_chrome() -> str:
    for p in CHROME_CANDIDATES:
        if p and os.path.exists(p):
            return p
    sys.exit("Chrome not found; set CHROME=/path/to/chrome")


def chrome(chrome_bin: str, url: str, *args: str) -> str:
    cmd = [chrome_bin, "--headless=new", "--disable-gpu", *args, url]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=300).stdout


def convert(src_path: str, out_dir: str, scale: int) -> None:
    src = open(src_path).read().replace("<br/>", "\n").replace("<br>", "\n")
    name = os.path.splitext(os.path.basename(src_path))[0]
    os.makedirs(out_dir, exist_ok=True)
    chrome_bin = find_chrome()
    page = (
        '<!doctype html><meta charset="utf-8"><pre id="out">start</pre>'
        "<script type=\"module\">" + BROWSER_JS.replace("__SOURCE__", json.dumps(src)) + "</script>"
    )

    with tempfile.TemporaryDirectory() as tmp:
        html = os.path.join(tmp, "convert.html")
        open(html, "w").write(page)

        for attempt in (1, 2):
            dom = chrome(chrome_bin, "file://" + html,
                         "--virtual-time-budget=120000", "--dump-dom")
            m = re.search(r'<pre id="out">(.*?)</pre>', dom, re.S)
            raw = m.group(1) if m else ""
            if raw and not raw.startswith("start") and not raw.startswith("ERR"):
                break
            if attempt == 2:
                sys.exit(f"conversion failed (run {attempt}): {raw[:400] or 'no output'}")

    data = json.loads(raw)
    for kind, n in sorted(data.get("unknown", {}).items()):
        print(f"warning: unsupported element type {kind!r} x{n}: not drawn", file=sys.stderr)
    scene = json.loads(base64.b64decode(data["json"]))
    missing = {k for e in scene["elements"] for k in REQUIRED - set(e)}
    if missing:
        sys.exit(f"invalid Excalidraw elements, missing: {sorted(missing)}")

    json_path = os.path.join(out_dir, name + ".excalidraw")
    svg_path = os.path.join(out_dir, name + ".svg")
    png_path = os.path.join(out_dir, name + ".png")
    json.dump(scene, open(json_path, "w"), indent=1)
    svg = base64.b64decode(data["svg"]).decode()
    open(svg_path, "w").write(svg)

    w = int(float(re.search(r'width="([\d.]+)"', svg).group(1)))
    h = int(float(re.search(r'height="([\d.]+)"', svg).group(1)))
    chrome(chrome_bin, "file://" + os.path.abspath(svg_path),
           "--hide-scrollbars", f"--force-device-scale-factor={scale}",
           f"--window-size={w},{h}", f"--screenshot={os.path.abspath(png_path)}")

    if not os.path.exists(png_path):
        sys.exit("PNG screenshot did not run")
    print(f"{name}: {data['count']} elements, {w}x{h} -> {json_path}, .svg, .png")


def main() -> None:
    args = sys.argv[1:]
    if len(args) < 2:
        sys.exit(__doc__)
    scale = 2
    if "--scale" in args:
        i = args.index("--scale")
        scale = int(args[i + 1])
        del args[i:i + 2]
    convert(args[0], args[1], scale)


if __name__ == "__main__":
    main()
