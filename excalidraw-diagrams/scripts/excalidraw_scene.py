#!/usr/bin/env python3
"""Hand-laid-out .excalidraw scenes: groups, nodes, bound arrows, notes, previews.

Generalised from the reference generator (reference/gen_excalidraw.py). Everything
repo-specific is gone; `Scene(root)` is the only project input, used for links.

    from excalidraw_scene import Scene
    s = Scene("/path/to/repo")
    s.group("g", "Host", 0, 0, 600, 200, palette="host")
    s.node("a", "Console\\n:8090", 30, 60, file="console/serve.py")
    s.node("b", "Runner\\n:8080", 330, 60)
    s.arrow("a", "b", "HTTP")
    s.save("/tmp/out", "demo", "Demo")
"""

import json
import math
import os
import random
import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

PALETTES = {
    "host": ("#f08c00", "#fff9db"),
    "k8s": ("#1971c2", "#e7f5ff"),
    "k8s2": ("#1971c2", "#d0ebff"),
    "out": ("#2f9e44", "#ebfbee"),
    "shared": ("#6741d9", "#f3f0ff"),
    "neutral": ("#495057", "#f8f9fa"),
}
NODE_STYLES = {
    "normal": ("#1e1e1e", "#ffffff"),
    "accent": ("#e03131", "#ffe3e3"),
    "muted": ("#868e96", "#f1f3f5"),
}
ARROW_STYLES = {"normal": "#1e1e1e", "accent": "#e03131", "muted": "#868e96"}

CHROME_CANDIDATES = [
    os.environ.get("CHROME", ""),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
]


class Scene:
    def __init__(self, root="."):
        self.root = Path(root).resolve()
        self.els = []
        self.by_id = {}
        self.rng = random.Random(42)

    # ---------------------------------------------------------------- elements
    def _base(self, id_, type_, x, y, w, h, stroke, bg, **kw):
        if id_ in self.by_id:
            raise ValueError(f"duplicate element id: {id_}")
        el = {
            "id": id_, "type": type_, "x": x, "y": y, "width": w, "height": h,
            "angle": 0, "strokeColor": stroke, "backgroundColor": bg,
            "fillStyle": "solid", "strokeWidth": kw.get("sw", 2),
            "strokeStyle": kw.get("style", "solid"), "roughness": 1, "opacity": 100,
            "groupIds": [], "frameId": None,
            "roundness": kw.get("roundness", {"type": 3}),
            "seed": self.rng.randint(1, 2**31), "version": 1,
            "versionNonce": self.rng.randint(1, 2**31), "isDeleted": False,
            "boundElements": [], "updated": 1, "link": kw.get("link"), "locked": False,
        }
        self.els.append(el)
        self.by_id[id_] = el
        return el

    def _text(self, id_, x, y, w, h, text, size, container=None, align="center",
              valign="middle", color="#1e1e1e"):
        el = self._base(id_, "text", x, y, w, h, color, "transparent", roundness=None)
        el.update({"text": text, "fontSize": size, "fontFamily": 1,
                   "textAlign": align, "verticalAlign": valign,
                   "containerId": container, "originalText": text,
                   "lineHeight": 1.25, "autoResize": True})
        return el

    @staticmethod
    def _measure(text, size):
        lines = text.split("\n")
        return max(len(l) for l in lines) * size * 0.58, len(lines) * size * 1.25

    # ---------------------------------------------------------------- public
    def group(self, id_, label, x, y, w, h, palette="k8s"):
        """Dashed, tinted area with a top-left label. Call before its nodes."""
        stroke, bg = PALETTES[palette]
        self._base(id_, "rectangle", x, y, w, h, stroke, bg, style="dashed", sw=1)
        tw, th = self._measure(label, 18)
        self._text(id_ + "-label", x + 12, y + 8, tw, th, label, 18,
                   align="left", valign="top", color=stroke)

    def node(self, id_, label, x, y, w=220, h=80, kind="normal", file=None, size=18):
        """Two-line box; `file` adds a VS Code link and customData.file."""
        stroke, bg = NODE_STYLES[kind]
        link = None
        if file:
            link = "vscode://file" + str(self.root / file)
        box = self._base(id_, "rectangle", x, y, w, h, stroke, bg, link=link)
        if file:
            box["customData"] = {"file": file}
        tw, th = self._measure(label, size)
        tid = id_ + "-t"
        self._text(tid, x + (w - tw) / 2, y + (h - th) / 2, tw, th, label, size,
                   container=id_)
        box["boundElements"].append({"type": "text", "id": tid})

    def note(self, id_, text, x, y, size=15, color="#495057", wrap=110):
        """Free text, wrapped at `wrap` chars; bullet continuations indented."""
        out = []
        for line in text.split("\n"):
            ind = "  " if line.startswith("- ") or line.startswith("Left out") else ""
            out.extend(textwrap.wrap(line, wrap, subsequent_indent=ind) or [""])
        text = "\n".join(out)
        tw, th = self._measure(text, size)
        self._text(id_, x, y, tw, th, text, size, align="left", valign="top",
                   color=color)

    def _edge_point(self, el, tx, ty):
        cx = el["x"] + el["width"] / 2
        cy = el["y"] + el["height"] / 2
        dx, dy = tx - cx, ty - cy
        if dx == 0 and dy == 0:
            return cx, cy
        hw, hh = el["width"] / 2 + 6, el["height"] / 2 + 6
        t = min(hw / abs(dx) if dx else math.inf, hh / abs(dy) if dy else math.inf)
        return cx + dx * t, cy + dy * t

    def arrow(self, a, b, label=None, dashed=False, kind="normal", via=None,
              start=None, end=None):
        """Bound arrow a -> b. `via` is absolute waypoints; start/end override ends."""
        ea, eb = self.by_id[a], self.by_id[b]
        via = list(via or [])
        first = via[0] if via else (eb["x"] + eb["width"] / 2, eb["y"] + eb["height"] / 2)
        last = via[-1] if via else (ea["x"] + ea["width"] / 2, ea["y"] + ea["height"] / 2)
        p0 = start or self._edge_point(ea, *first)
        pn = end or self._edge_point(eb, *last)
        pts = [p0] + via + [pn]

        # Normalise so the element origin is the top-left of the point bounds.
        # This is a style choice for readable JSON, not an Excalidraw requirement:
        # negative relative points are valid and the official converter emits them.
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        x0, y0 = min(xs), min(ys)
        rel = [[px - x0, py - y0] for px, py in pts]

        stroke = ARROW_STYLES[kind]
        aid = f"arr-{a}-{b}-{len(self.els)}"
        el = self._base(aid, "arrow", x0, y0, max(xs) - x0, max(ys) - y0,
                        stroke, "transparent", style="dashed" if dashed else "solid",
                        roundness={"type": 2} if not via else None)
        el.update({
            "points": rel, "lastCommittedPoint": None,
            "startBinding": {"elementId": a, "focus": 0, "gap": 6},
            "endBinding": {"elementId": b, "focus": 0, "gap": 6},
            "startArrowhead": None, "endArrowhead": "arrow", "elbowed": False,
        })
        ea["boundElements"].append({"type": "arrow", "id": aid})
        eb["boundElements"].append({"type": "arrow", "id": aid})

        if label:
            i = (len(pts) - 1) // 2
            mx = (pts[i][0] + pts[i + 1][0]) / 2
            my = (pts[i][1] + pts[i + 1][1]) / 2
            tw, th = self._measure(label, 14)
            tid = aid + "-t"
            self._text(tid, mx - tw / 2, my - th / 2, tw, th, label, 14,
                       container=aid, color=stroke)
            el["boundElements"].append({"type": "text", "id": tid})

    # ---------------------------------------------------------------- checks
    def validate(self):
        """Return a list of structural errors; empty means the scene is sound."""
        errors = []
        ids = [e["id"] for e in self.els]
        if len(ids) != len(set(ids)):
            errors.append("duplicate element ids")
        for e in self.els:
            if e["width"] < 0 or e["height"] < 0:
                errors.append(f"{e['id']}: negative size")
            for b in e.get("boundElements") or []:
                target = self.by_id.get(b["id"])
                if target is None:
                    errors.append(f"{e['id']}: boundElements -> missing {b['id']}")
                elif b["type"] == "text" and target.get("containerId") != e["id"]:
                    errors.append(f"{e['id']}: text {b['id']} does not point back")
                elif b["type"] == "arrow" and e["id"] not in {
                        (target.get("startBinding") or {}).get("elementId"),
                        (target.get("endBinding") or {}).get("elementId")}:
                    errors.append(f"{e['id']}: arrow {b['id']} does not bind here")
            if e["type"] == "text" and e.get("containerId"):
                parent = self.by_id.get(e["containerId"])
                if parent is None:
                    errors.append(f"{e['id']}: containerId missing {e['containerId']}")
                elif e["id"] not in [x["id"] for x in parent.get("boundElements") or []]:
                    errors.append(f"{e['id']}: container does not list text")
            if e["type"] == "arrow":
                for key in ("startBinding", "endBinding"):
                    target = (e.get(key) or {}).get("elementId")
                    if target not in self.by_id:
                        errors.append(f"{e['id']}: {key} -> missing {target}")
        return errors

    # ---------------------------------------------------------------- output
    def save(self, out_dir, name, title=None):
        errors = self.validate()
        if errors:
            raise ValueError("scene is invalid:\n- " + "\n- ".join(errors))
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        doc = {"type": "excalidraw", "version": 2, "source": "https://excalidraw.com",
               "elements": self.els,
               "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None},
               "files": {}}
        (out / f"{name}.excalidraw").write_text(json.dumps(doc, indent=2))
        self.svg(out / f"{name}.svg", title)
        return out / f"{name}.excalidraw"

    def svg(self, path, title=None):
        xs = [e["x"] for e in self.els] + [e["x"] + e["width"] for e in self.els]
        ys = [e["y"] for e in self.els] + [e["y"] + e["height"] for e in self.els]
        minx, miny = min(xs) - 24, min(ys) - 24
        maxx, maxy = max(xs) + 24, max(ys) + 24
        out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{minx} {miny} '
               f'{maxx-minx} {maxy-miny}" width="{maxx-minx}" height="{maxy-miny}" '
               f'font-family="Helvetica"><rect x="{minx}" y="{miny}" width="100%" '
               f'height="100%" fill="white"/>'
               '<defs><marker id="h" markerWidth="10" markerHeight="8" refX="9" refY="4" '
               'orient="auto"><path d="M0,0 L10,4 L0,8z"/></marker></defs>']
        for e in self.els:
            dash = ' stroke-dasharray="6,4"' if e["strokeStyle"] == "dashed" else ""
            if e["type"] == "rectangle":
                out.append(f'<rect x="{e["x"]}" y="{e["y"]}" width="{e["width"]}" '
                           f'height="{e["height"]}" rx="8" fill="{e["backgroundColor"]}" '
                           f'stroke="{e["strokeColor"]}" stroke-width="{e["strokeWidth"]}"{dash}/>')
            elif e["type"] == "arrow":
                pts = " ".join(f'{e["x"]+p[0]},{e["y"]+p[1]}' for p in e["points"])
                out.append(f'<polyline points="{pts}" fill="none" stroke="{e["strokeColor"]}" '
                           f'stroke-width="2"{dash} marker-end="url(#h)"/>')
        for e in self.els:
            if e["type"] != "text":
                continue
            size = e["fontSize"]
            anchor = {"left": "start", "right": "end"}.get(e["textAlign"], "middle")
            if anchor == "start":
                x = e["x"]
            elif anchor == "end":
                x = e["x"] + e["width"]
            else:
                x = e["x"] + e["width"] / 2
            parent = self.by_id.get(e["containerId"]) if e["containerId"] else None
            on_arrow = parent is not None and parent["type"] == "arrow"
            for i, line in enumerate(e["text"].split("\n")):
                y = e["y"] + size * (i + 1) * 1.1
                line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                if on_arrow:
                    w = len(line) * size * 0.55
                    out.append(f'<rect x="{x-w/2}" y="{y-size}" width="{w}" '
                               f'height="{size*1.25}" fill="white" opacity="0.85"/>')
                out.append(f'<text x="{x}" y="{y}" font-size="{size}" '
                           f'text-anchor="{anchor}" fill="{e["strokeColor"]}">{line}</text>')
        if title:
            out.append(f'<title>{title}</title>')
        out.append("</svg>")
        Path(path).write_text("\n".join(out))

    def png(self, path, scale=2):
        """Rasterise the preview through headless Chrome."""
        svg = Path(path).with_suffix(".svg")
        self.svg(svg, None)
        chrome = next((p for p in CHROME_CANDIDATES if p and os.path.exists(p)), None)
        if not chrome:
            raise RuntimeError("Chrome not found; set CHROME=/path/to/chrome")
        head = svg.read_text()
        w = int(float(re.search(r'width="([\d.]+)"', head).group(1)))
        h = int(float(re.search(r'height="([\d.]+)"', head).group(1)))
        subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        f"--force-device-scale-factor={scale}",
                        f"--window-size={w},{h}",
                        f"--screenshot={Path(path).resolve()}", svg.resolve().as_uri()],
                       check=True, capture_output=True)
        return Path(path)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/excalidraw-demo"
    s = Scene(".")
    s.note("title", "Four-node demo", 0, -80, size=28, color="#1e1e1e")
    s.group("g", "One area", 0, 0, 1180, 200, palette="k8s")
    s.node("a", "First\n:1000", 30, 60)
    s.node("b", "Second\n:2000", 330, 60, kind="accent")
    s.node("c", "Third\n:3000", 630, 60)
    s.node("d", "Fourth\n:4000", 930, 60)
    s.arrow("a", "b", "call")
    s.arrow("b", "c", "call")
    s.arrow("c", "d", "call", dashed=True)
    s.note("n", "Notes\n- A short example of the hand-laid-out mode.\n\nLeft out: everything else.", 0, 250)
    s.save(out, "demo", "demo")
    s.png(Path(out) / "demo.png")
    print(f"wrote {out}/demo.excalidraw and demo.png")
