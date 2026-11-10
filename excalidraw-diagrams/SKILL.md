---
name: excalidraw-diagrams
description: Use ONLY when the deliverable is an editable .excalidraw file, a Lavish whiteboard, or a Sketchy sketch, and not for a plain Mermaid diagram in a README or docs page. Covers .excalidraw JSON, Lavish, Sketchy, whiteboard editing, and image export.
---

# Excalidraw architecture diagrams

Each diagram ships as `<name>.excalidraw` (the editable scene) plus `<name>.png` and `.svg` (the image). There are two modes: hand-laid-out (default for architecture and walkthrough diagrams) and Mermaid-to-Excalidraw (fast iteration and Lavish whiteboards). State which mode you used and why. Store diagrams where the repo keeps them (`docs/diagrams/` by convention).

## 1. Ground the content

Read the code, manifests or docs the diagram describes. Do not invent edges. Target 10-14 nodes, labels of 1-4 words, and check uncertain claims against the files before drawing them.

Mermaid labels cannot carry hover text, so put the numbered steps and the notes in HTML beside the diagram, not inside it.

## 2. Build the Lavish page

- One `.mermaid` block per diagram in `.lavish/<name>.html`.
- Run `lavish-axi design` and paste its `mermaid_cdn_snippet` into the page. It renders Mermaid 11, theme-aware, and is what Lavish turns into an Excalidraw whiteboard.
- Do not author the whiteboard scene yourself; Lavish converts the Mermaid at load time.
- Design source, in order: the look the user asked for → the project's own tokens/components (read its CSS or component library) → DaisyUI/Tailwind CDN fallback. Say which one you used and why.
- Keep each diagram card readable: no fixed pixel widths, `svg { max-width: 100% }`, and no horizontal overflow at narrow widths.

## 3. Review loop

```
lavish-axi .lavish/<name>.html          # returns the URL
lavish-axi poll .lavish/<name>.html     # foreground, leave running
```

- Apply whiteboard feedback by editing the Mermaid source. Never write the scene back into the artifact.
- After each change reply with `lavish-axi poll <file> --agent-reply "<what changed>"` and keep waiting.
- A whiteboard feedback payload carries `scenePath` (the real `.excalidraw`) and `previewPath` (PNG). That is the only way to capture the exact browser scene, and the user must send an edit to trigger it. Without it, generate the files from the Mermaid (section 5) and say the image is a render of the geometry, not the browser scene.

## 4. Hand-laid-out mode (default for architecture and walkthrough diagrams)

Use this when layout quality, groups, routed arrows, notes on the canvas or source links matter. Use the Mermaid converter (section 5) when the user wants to edit in a Lavish whiteboard or iterate fast.

Build the scene with `scripts/excalidraw_scene.py`. It generalises the reference generator saved at `reference/gen_excalidraw.py`.

Rules:

- Explicit coordinates. Nodes are 220x80 by default. Columns are about 300 apart (an 80px gap), widened to 100-120px when the arrow label is long. Rows are about 190-200 apart, with a larger 300+ gap where a routed edge needs room.
- Groups are dashed, tinted rectangles with a label at the top-left, emitted before their nodes so they sit behind them. They can nest (cluster > namespace). Each area gets its own colour: host yellow, k8s blue (lighter blue for an inner namespace), outside network green, shared purple.
- Node labels have two lines: the name, then a concrete identifier (IP:port, resource name, CRD state).
- Bind node and arrow-label text to its container: the text has `containerId` and the container lists it in `boundElements`. Group labels stay free text.
- Bind arrows at both ends (`startBinding`/`endBinding`). Endpoints sit on the box border with a 6px gap, not at the centre. Route loops and under-passes with `via` waypoints. Negative relative points are fine; Excalidraw and its official converter both emit them.
- Visual grammar: solid = control flow, dashed = data path. One or two accent (red) nodes for the key components; grey muted for failure paths.
- Walkthroughs put circled step numbers (① ② …) on the nodes, with a "Steps" block and a "Notes" block under the diagram. Notes wrap at about 110 characters and end with a "Left out:" line.
- Nodes that represent code carry `link = "vscode://file<absolute path>"` plus `customData.file` (repo-relative). `Scene(root)` builds both.
- Title and subtitle are free notes above the diagram.

Workflow:

1. Read the code the diagram describes.
2. List nodes, edges and groups; about 12 nodes.
3. Sketch a coordinate grid: columns, rows, group boxes, room for labels and routes.
4. Write a small generator script using `Scene`: `group`, `node`, `arrow(via=...)`, `note`, `save`.
5. `save()` validates unique ids and resolves every binding and `containerId`; it refuses a broken scene.
6. Render the preview (`save` writes `.svg`, `Scene.png()` rasterises it), look at the PNG, and fix cramped labels and overlaps. The first draft is always cramped; one fix pass is the minimum.
7. Repeat until clean. Report which mode you used and why.

API: `Scene(root)`, `group(id, label, x, y, w, h, palette)`, `node(id, label, x, y, w, h, kind, file)`, `note(id, text, x, y, size, color, wrap)`, `arrow(a, b, label, dashed, kind, via, start, end)`, `validate()`, `save(out_dir, name, title)`, `svg(path, title)`, `png(path, scale)`.

## 5. Mermaid-to-Excalidraw export

```
~/.config/opencode/skills/excalidraw-diagrams/scripts/mermaid-to-excalidraw.py \
  <diagram>.mmd <out-dir>
```

Writes `<name>.excalidraw`, `.svg`, and a 2x `.png`. It runs Excalidraw's official `@excalidraw/mermaid-to-excalidraw` converter in headless Chrome, then renders the resulting element geometry.

- Needs Python 3, Google Chrome (override with `CHROME=`), and network access to esm.sh.
- Mermaid labels cannot hold raw < > or quotes. Use #lt; #gt; #quot; inside quoted labels, then check that the converted text contains the real characters.
- `<br/>` becomes literal text in converted labels; the script turns it into real newlines. Prefer plain newlines in Mermaid labels.
- Excalidraw's own `exportToSvg` hangs in headless Chrome, which is why the script renders the geometry itself. It draws rectangle, diamond, ellipse, arrow, line and text, and warns on stderr about any other element type. The PNG has clean lines and a sans font, not Excalifont; the `.excalidraw` is authoritative and looks hand-drawn when opened in Excalidraw.
- The script refuses elements missing required fields. For an extra check, run `Excalidraw.restore({elements, appState})` and expect zero errors.
- Before overwriting files in `docs/diagrams/`, check `git status`: that directory is often untracked, so plain `cp` destroys the originals.

## 6. Sketchy (optional)

Sketchy is an MCP server (`npx -y @ddkbs/sketchy`), tool `sketch` with `{scene}`.

- It returns `content[0]` (a text sentence), `structuredContent.view` (a UUID), and `_meta["sketchy/scene"]` (node/edge geometry and inline icon SVG bodies). It returns no SVG, PNG, HTML, URL, or Excalidraw JSON.
- The drawing is an MCP-App resource (`ui://sketchy/viewer.html`). The client must support MCP Apps; a plain MCP client sees only the view ID.
- opencode does not register Sketchy by default. If no `sketch` tool exists, say plainly that it is unavailable and do not fabricate its output. If it does exist, you may hand-render the returned geometry, labelled as hand-rendered.
- `save_export` (SVG/PNG/Excalidraw) is viewer-only and cannot be driven from a normal tool call.

## Verify before reporting

- Screenshot the page headlessly at desktop and narrow widths; check no overflow and that Mermaid rendered (a blank pre means a parse error).
- Confirm the `.excalidraw` opens, the PNG exists, and labels are legible.
- Report what actually happened, including any tool that returned nothing usable.
