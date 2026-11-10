#!/usr/bin/env python3
"""Generate the three JIT architecture diagrams as .excalidraw files (+ SVG previews)."""
import json
import math
import random
import sys
from pathlib import Path

ROOT = "/Users/vkancherla/Downloads/Devops-Projects/k8s-just-in-time-infra"
OUT = Path(sys.argv[1])
PREVIEW = Path(sys.argv[2])

PAL = {
    "host": ("#f08c00", "#fff9db"),
    "k8s": ("#1971c2", "#e7f5ff"),
    "k8s2": ("#1971c2", "#d0ebff"),
    "out": ("#2f9e44", "#ebfbee"),
    "shared": ("#6741d9", "#f3f0ff"),
}
NODE_BG = {"normal": ("#1e1e1e", "#ffffff"), "accent": ("#e03131", "#ffe3e3"),
           "muted": ("#868e96", "#f1f3f5")}


class Scene:
    def __init__(self):
        self.els = []
        self.by_id = {}
        self.rng = random.Random(42)

    def _base(self, id_, type_, x, y, w, h, stroke, bg, **kw):
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

    def group(self, id_, label, x, y, w, h, pal):
        stroke, bg = PAL[pal]
        self._base(id_, "rectangle", x, y, w, h, stroke, bg, style="dashed", sw=1)
        tw, th = self._measure(label, 18)
        self._text(id_ + "-label", x + 12, y + 8, tw, th, label, 18,
                   align="left", valign="top", color=stroke)

    def node(self, id_, label, x, y, w=220, h=80, kind="normal", file=None, size=18):
        stroke, bg = NODE_BG[kind]
        link = f"vscode://file{ROOT}/{file}" if file else None
        box = self._base(id_, "rectangle", x, y, w, h, stroke, bg, link=link)
        if file:
            box["customData"] = {"file": file}
        tw, th = self._measure(label, size)
        tid = id_ + "-t"
        self._text(tid, x + (w - tw) / 2, y + (h - th) / 2, tw, th, label, size,
                   container=id_)
        box["boundElements"].append({"type": "text", "id": tid})

    def note(self, id_, text, x, y, size=15, color="#495057", wrap=110):
        import textwrap
        out = []
        for line in text.split("\n"):
            ind = "  " if line.startswith("- ") or line.startswith("Left out") else ""
            out.extend(textwrap.wrap(line, wrap, subsequent_indent=ind) or [""])
        text = "\n".join(out)
        tw, th = self._measure(text, size)
        self._text(id_, x, y, tw, th, text, size, align="left", valign="top",
                   color=color)

    def _edge_point(self, el, tx, ty):
        cx, cy = el["x"] + el["width"] / 2, el["y"] + el["height"] / 2
        dx, dy = tx - cx, ty - cy
        if dx == 0 and dy == 0:
            return cx, cy
        hw, hh = el["width"] / 2 + 6, el["height"] / 2 + 6
        t = min(hw / abs(dx) if dx else math.inf, hh / abs(dy) if dy else math.inf)
        return cx + dx * t, cy + dy * t

    def arrow(self, a, b, label=None, dashed=False, kind="normal", via=None,
              start=None, end=None):
        """Arrow from node a to node b. `via` = absolute waypoints; start/end override."""
        ea, eb = self.by_id[a], self.by_id[b]
        via = via or []
        first_target = via[0] if via else (eb["x"] + eb["width"] / 2,
                                           eb["y"] + eb["height"] / 2)
        last_source = via[-1] if via else (ea["x"] + ea["width"] / 2,
                                           ea["y"] + ea["height"] / 2)
        p0 = start or self._edge_point(ea, *first_target)
        pn = end or self._edge_point(eb, *last_source)
        pts = [p0] + list(via) + [pn]
        x0, y0 = pts[0]
        rel = [[px - x0, py - y0] for px, py in pts]
        xs, ys = [p[0] for p in rel], [p[1] for p in rel]
        stroke = {"normal": "#1e1e1e", "accent": "#e03131", "muted": "#868e96"}[kind]
        aid = f"arr-{a}-{b}-{len(self.els)}"
        el = self._base(aid, "arrow", x0, y0, max(xs) - min(xs), max(ys) - min(ys),
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
            # midpoint of the middle segment, which is where Excalidraw puts it
            i = (len(pts) - 1) // 2
            mx = (pts[i][0] + pts[i + 1][0]) / 2
            my = (pts[i][1] + pts[i + 1][1]) / 2
            tw, th = self._measure(label, 14)
            tid = aid + "-t"
            self._text(tid, mx - tw / 2, my - th / 2, tw, th, label, 14,
                       container=aid, color=stroke)
            el["boundElements"].append({"type": "text", "id": tid})
            el["_label_pos"] = (mx, my)

    def save(self, name, title):
        doc = {"type": "excalidraw", "version": 2, "source": "https://excalidraw.com",
               "elements": [{k: v for k, v in e.items() if not k.startswith("_")}
                            for e in self.els],
               "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None},
               "files": {}}
        (OUT / f"{name}.excalidraw").write_text(json.dumps(doc, indent=2))
        self.svg(PREVIEW / f"{name}.svg", title)

    def svg(self, path, title):
        xs = [e["x"] for e in self.els] + [e["x"] + e["width"] for e in self.els]
        ys = [e["y"] for e in self.els] + [e["y"] + e["height"] for e in self.els]
        minx, miny, maxx, maxy = min(xs) - 20, min(ys) - 20, max(xs) + 20, max(ys) + 20
        side = max(maxx - minx, maxy - miny)
        maxx, maxy = minx + side, miny + side
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
            lines = e["text"].split("\n")
            size = e["fontSize"]
            anchor = "start" if e["textAlign"] == "left" else "middle"
            x = e["x"] if anchor == "start" else e["x"] + e["width"] / 2
            parent = self.by_id.get(e["containerId"]) if e["containerId"] else None
            bg = parent and parent["type"] == "arrow"
            for i, line in enumerate(lines):
                y = e["y"] + size * (i + 1) * 1.1
                line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                if bg:
                    w = len(line) * size * 0.55
                    out.append(f'<rect x="{x-w/2}" y="{y-size}" width="{w}" '
                               f'height="{size*1.25}" fill="white" opacity="0.85"/>')
                out.append(f'<text x="{x}" y="{y}" font-size="{size}" '
                           f'text-anchor="{anchor}" fill="{e["strokeColor"]}">{line}</text>')
        out.append("</svg>")
        path.write_text("\n".join(out))


# ---------------------------------------------------------------- diagram 1
def static():
    s = Scene()
    s.note("title", "JIT infra: static architecture", 0, -70, size=28, color="#1e1e1e")
    s.note("sub", "As implemented in code. Solid = control, dashed = data path. "
           "Boxes with a link icon open their source file in VS Code.", 0, -30)

    s.group("g-host", "Host (macOS laptop)", 0, 80, 260, 200, "host")
    s.node("console", "Console :8090\nconsole/serve.py", 20, 150, file="console/serve.py")

    s.group("g-k3d", "k3d cluster voting-app", 290, 20, 620, 620, "k8s")
    s.group("g-ten", "ns voting-a / voting-b", 310, 64, 280, 560, "k8s2")
    s.node("apps", "vote / worker / result\nDeployments", 340, 110,
           file="app/kustomize/base/worker-deployment.yaml")
    s.node("claims", "InfraClaim\n<ns>-<module>", 340, 300,
           file="deploy/crd/infraclaim.yaml")
    s.node("jitres", "Secret + Svc + EPS\njit-<module>", 340, 490)
    s.group("g-def", "ns default", 610, 64, 280, 560, "k8s2")
    s.node("ctrl", "jit-controller\n(kopf)", 640, 200, kind="accent",
           file="jit-controller/main.py")
    s.node("ipam", "jit-ipam ConfigMap\n(IPAM ledger)", 640, 400,
           file="jit-controller/ipam.py")

    s.group("g-net", "Docker network k3d-voting-app\n172.19.0.0/16 (outside k3d)",
            950, 20, 280, 620, "out")
    s.node("runner", "jit-runner\n172.19.0.10:8080", 980, 110, kind="accent",
           file="jit-runner/main.py")
    s.node("minio", "MinIO 172.19.0.11:9000\nbucket jit-state", 980, 300,
           file="deploy/minio.sh")
    s.node("infra", "redis / postgres / pgadmin\ncontainers .100+", 980, 490)

    s.group("g-host2", "Host files + Docker", 1270, 20, 280, 620, "host")
    s.node("modules", "jit-modules (tofu)\nredis, postgres, pgadmin", 1300, 110,
           file="jit-modules/modules/redis/main.tf")
    s.node("docker", "Host Docker daemon\n/var/run/docker.sock", 1300, 490)

    s.arrow("console", "apps", "make / kubectl")
    s.arrow("apps", "ctrl", "annotations (watch)")
    s.arrow("ctrl", "claims", "create, patch status")
    s.arrow("ctrl", "ipam", "allocate / release")
    s.arrow("ctrl", "runner", "POST/DELETE /v1/runs\n(bearer)", kind="accent")
    s.arrow("modules", "runner", "copied per run")
    s.arrow("runner", "minio", "tofu state")
    s.arrow("runner", "docker", "docker.sock")
    s.arrow("docker", "infra", "creates")
    s.arrow("ctrl", "jitres", "writes from outputs")
    s.arrow("apps", "jitres", "secretKeyRef\n+ DNS", dashed=True,
            start=(334, 150), end=(334, 530), via=[(322, 150), (322, 530)])
    s.arrow("jitres", "infra", "EndpointSlice → IP", dashed=True)

    s.note("notes", NOTES_1, 0, 680)
    s.save("01-static-architecture", "static")


NOTES_1 = """Notes (hover text from the sketch)
- Console: python stdlib HTTP server on 127.0.0.1:8090. Runs only allowlisted `make` targets (demo-up, ns-delete, jit-up ...); reads state via `make state` (scripts/state.sh: kubectl + docker + MinIO). Holds no kube client itself.
- vote / worker / result: annotated jit.infra/<module>. vote declares redis + pgadmin; worker consumes redis, declares postgres; result consumes postgres. Overlays voting-a / voting-b.
- InfraClaim: CRD infraclaims.jit.io v1alpha1 (short name ic). ownerRef = Namespace, finalizer jit.infra/teardown. status: phase, allocatedIP, appliedParams, referencedBy, declaredBy, expiresAt, conditions.
- Secret + Svc + EPS: written by the controller from runner outputs. Secret holds service_url, service_host, port, POSTGRES_*; headless Service with no selector + EndpointSlice to the container IP.
- jit-controller: watches Deployments cluster-wide (WATCH_NAMESPACES=""). Code arrives as ConfigMap jit-controller-code (main.py, ipam.py). ClusterRole */*/*. 30s resync timer per claim.
- jit-ipam: one 10-address block per namespace out of 172.19.0.100-199, ref-counted per claim.
- jit-runner: FastAPI + OpenTofu 1.8.1. A plain docker container from deploy/runner.sh, not a k8s pod. Holds docker.sock and MinIO creds; bearer-token auth.
- MinIO: S3 state backend, key ns/<ns>/<module>/terraform.tfstate.
- Containers: named <ns>-<module>-<module> at allocated IPs. postgres keeps a named volume; pgadmin publishes host port 5050/5051.
- jit-modules: local dir bind-mounted read-only at /opt/jit-modules. moduleVersion is sent but ignored (no git-ref pinning).

Left out: jit-runner-token Secret, ServiceAccount/ClusterRole, Traefik Ingress + app Services, pgAdmin servers.json share dir, scripts/ behind make, fake runner mode (empty RUNNER_URL)."""


# ---------------------------------------------------------------- diagram 2
def provisioning():
    s = Scene()
    s.note("title", "Provisioning walkthrough", 0, -70, size=28, color="#1e1e1e")
    s.note("sub", "From annotation to a pod using the claim. Circled numbers = steps.", 0, -30)

    s.group("g-k8s", "Kubernetes (tenant ns + default)", 0, 20, 1500, 520, "k8s")
    s.node("deploy", "① Annotated\nDeployment", 30, 90,
           file="app/kustomize/base/vote-deployment.yaml")
    s.node("handler", "① kopf on.create\n/ on.update", 330, 90,
           file="jit-controller/main.py")
    s.node("claim", "② InfraClaim\nphase \"\"", 630, 90, file="deploy/crd/infraclaim.yaml")
    s.node("ipam", "③ IPAM →\nstatus.allocatedIP", 930, 90, file="jit-controller/ipam.py")
    s.node("reconcile", "④ Resolve declarers\n+ validate params", 1240, 90, kind="accent")
    s.node("pods", "⑦ Pods consume\n(secretKeyRef)", 30, 400)
    s.node("ready", "⑥ phase Ready", 330, 400, kind="accent")
    s.node("write", "⑥ Secret + Svc + EPS\njit-<module>", 630, 400)
    s.node("failed", "⑥ phase Failed", 980, 250, kind="muted")

    s.group("g-out", "Outside k3d", 1540, 20, 300, 520, "out")
    s.node("runner", "⑤ jit-runner\nPOST /v1/runs", 1580, 90, file="jit-runner/main.py")
    s.node("tofu", "⑤ tofu init + apply\n(state in MinIO)", 1580, 250,
           file="jit-modules/modules/redis/main.tf")
    s.node("container", "⑤ <ns>-<module>-<module>\ncontainer", 1580, 410, w=240)

    s.arrow("deploy", "handler", "watch event")
    s.arrow("handler", "claim", "ensure_claim")
    s.arrow("claim", "ipam", "allocate")
    s.arrow("ipam", "reconcile")
    s.arrow("reconcile", "runner", "HTTP + bearer")
    s.arrow("runner", "tofu")
    s.arrow("tofu", "container", "docker.sock")
    s.arrow("runner", "failed", "error")
    s.arrow("runner", "write", "outputs")
    s.arrow("write", "ready")
    s.arrow("ready", "pods")
    s.arrow("pods", "container", "via Service + EndpointSlice", dashed=True,
            start=(140, 486), end=(1700, 496), via=[(140, 600), (1700, 600)])

    s.note("steps", STEPS_2, 0, 650, color="#1e1e1e")
    s.note("notes", NOTES_2, 860, 650)
    s.save("02-provisioning", "provisioning")


STEPS_2 = """Steps
① Annotate: tenant applies a Deployment with jit.infra/<module>;
   kopf fires on.create and on.update (handle_deployment).
② Claim: ensure_claim creates InfraClaim <ns>-<module>
   (owner Namespace, finalizer jit.infra/teardown). Phase is "".
③ Address: IPAM gives the namespace a 10-IP block and the
   claim its own status.allocatedIP.
④ Resolve: declarers resolved, params validated.
   Consumers only → phase Pending + AwaitingDeclarer.
⑤ Provision: POST /v1/runs; runner runs tofu against MinIO
   state, Docker creates the container.
⑥ Ready: outputs → Secret + headless Service + EndpointSlice,
   phase Ready. Runner error on create → phase Failed.
⑦ Consume: pods read the Secret and reach the container
   through the Service."""

NOTES_2 = """Notes
- Annotation: jit.infra/redis: {"module":"redis","params":{},"softDeleteTTL":"10m"}.
  A `params` key (even {}) makes the Deployment a declarer; no key = consumer.
- IPAM: allocate_block(ns) in ConfigMap default/jit-ipam, then first_free_address
  under a per-namespace lock.
- Resolve: referencedBy/declaredBy; softDeleteTTL = max over refs.
  Declarers disagree → ParamsConflict. Bad key → UpdateRefused. Else Updating=True.
- Runner request: {module, version, workspace=ns, params + name/ip/network}.
  Controller generates the postgres password (reused from the Secret). Runner caches
  by params hash; retries apply once after `docker rm -f` on a name conflict.
- Failed is terminal until a Deployment event. On an update the claim stays
  Ready + UpdateFailed instead.
- Ready sets outputsSecret, endpoint, appliedParams; Updating=False, OutputsChanged.

Left out: update path (apply_update, UpdateFailed, attemptedParamsHash gate),
stale-Ready re-provision, pgadmin waiting on jit-postgres, appliedParams backfill,
claim/namespace locks, runner per-run lock, extra postgresql_database resources."""


# ---------------------------------------------------------------- diagram 3
def teardown():
    s = Scene()
    s.note("title", "Teardown walkthrough", 0, -110, size=28, color="#1e1e1e")
    s.note("sub", "Two paths: retention clock (A) vs immediate namespace delete (B). "
           "Circled numbers = steps.", 0, -70)

    s.group("g-soft", "Path A: delete the app (soft)", 0, -20, 1200, 420, "k8s")
    s.node("deldep", "① Delete\nDeployments", 30, 90, file="Makefile")
    s.node("resync", "① Resync timer\n(every 30s)", 330, 90, file="jit-controller/main.py")
    s.node("orphaned", "② phase Orphaned\nexpiresAt = now+TTL", 630, 90, kind="accent")
    s.node("deleting", "③ phase Deleting", 930, 90)
    s.node("ready", "③ back to Ready\n(no runner call)", 330, 290)

    s.group("g-hard", "Path B: delete the namespace (hard)", 0, 440, 600, 200, "host")
    s.node("delns", "⑥ kubectl delete ns", 30, 520)
    s.node("ondelete", "⑥ GC → kopf on.delete\nhandle_claim_delete", 330, 520, w=230)

    s.group("g-shared", "Shared teardown", 1240, -20, 300, 760, "shared")
    s.node("destroy", "④ DELETE /v1/runs/<ns>\n(tofu destroy)", 1275, 90, w=230,
           kind="accent", file="jit-runner/main.py")
    s.node("cleanup", "⑤ Delete Secret /\nSvc / EPS", 1275, 260, w=230)
    s.node("remove", "⑤ Drop finalizer,\ndelete claim", 1275, 430, w=230)
    s.node("release", "⑤ Release IP block", 1275, 600, w=230, file="jit-controller/ipam.py")

    s.arrow("deldep", "resync", "no refs left")
    s.arrow("resync", "orphaned", "set expiresAt")
    s.arrow("orphaned", "ready", "ref returns in window", dashed=True)
    s.arrow("orphaned", "deleting", "TTL expired")
    s.arrow("deleting", "destroy")
    s.arrow("destroy", "deleting", "fails: retry next tick", kind="muted", dashed=True,
            start=(1390, 84), end=(1040, 84), via=[(1390, 30), (1040, 30)])
    s.arrow("destroy", "cleanup", "success")
    s.arrow("cleanup", "remove")
    s.arrow("remove", "release")
    s.arrow("delns", "ondelete", "ownerRef GC")
    s.arrow("ondelete", "destroy", "immediately, any phase")
    s.arrow("ondelete", "release", "unless phase Deleting", dashed=True)

    s.note("steps", STEPS_3, 0, 790, color="#1e1e1e")
    s.note("notes", NOTES_3, 760, 790)
    s.save("03-teardown", "teardown")


STEPS_3 = """Steps
① Unreference: the last referencing Deployment goes; the 30s
   resync (resync_referenced_by) finds no references.
② Orphan: phase Orphaned, expiresAt = now + softDeleteTTL.
   The container and its data stay.
③ Branch: redeploy before expiry → Ready, no runner call.
   Expiry → phase Deleting.
④ Destroy: runner DELETE removes container + tofu state.
   On failure the claim stays Deleting and retries each tick.
⑤ Finish A: delete Secret/Svc/EPS, drop finalizer + claim,
   release the IP block.
⑥ Path B: namespace delete → GC deletes the claim; on.delete
   destroys at once, cleans up and releases the block.
   A failed destroy here is only logged: the claim still goes."""

NOTES_3 = """Notes
- Rollouts, or deleting only some referencing Deployments, change nothing:
  the claim stays Ready while any reference remains.
- softDeleteTTL = max over references; default 30d, 10m in the demo.
- Destroy body: {module, params = appliedParams + name/ip/network}. Runner does
  docker rm -f -v, tofu init (MinIO), state rm postgresql_*, tofu destroy.
  'destroyed' and 'not_found' count as success.
- Path A: dropping the finalizer fires on.delete again; that pass sees phase
  Deleting, re-runs a no-op destroy and skips the IP release.
- release_block decrements the jit-ipam count; the block is freed at 0.

Left out: runner cold-destroy path (no cached run), placeholder postgres
password/URL at destroy, referencedBy updates while Orphaned, pods and Ingress
removed with the namespace."""


static()
provisioning()
teardown()
print("ok")
