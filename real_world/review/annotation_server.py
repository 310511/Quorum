"""Phase 8: lightweight annotation web interface."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from real_world.common import read_jsonl
from real_world.config import ANNOTATIONS_JSONL, CANDIDATES_DIR, REAL_WORLD_ROOT

logger = logging.getLogger(__name__)

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Quorum Real-World Review</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 1.5rem; max-width: 1200px; }
    header { margin-bottom: 1rem; }
    pre { background: #f6f8fa; padding: 1rem; overflow: auto; border-radius: 6px; }
    .meta { color: #444; }
    .actions { margin: 1rem 0; display: flex; gap: 0.5rem; flex-wrap: wrap; }
    button { padding: 0.5rem 1rem; cursor: pointer; }
    textarea { width: 100%; min-height: 80px; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
    @media (max-width: 900px) { .grid { grid-template-columns: 1fr; } }
    .badge { display: inline-block; padding: 0.15rem 0.5rem; border-radius: 999px; background: #eee; }
  </style>
</head>
<body>
  <header>
    <h1>Real-World Semantic Merge Review</h1>
    <p class="meta">Reviewer: <strong id="reviewer">default</strong> · Example <span id="pos">0</span>/<span id="total">0</span></p>
    <p><span class="badge" id="repo"></span> <span class="badge" id="category"></span> <span class="badge" id="estimate"></span></p>
  </header>
  <section>
    <h2 id="example-id"></h2>
    <p id="reason"></p>
    <h3>Changed symbols</h3>
    <pre id="symbols"></pre>
    <div class="grid">
      <div><h3>Branch A diff</h3><pre id="left"></pre></div>
      <div><h3>Branch B diff</h3><pre id="right"></pre></div>
    </div>
    <h3>Your rationale</h3>
    <textarea id="notes" placeholder="Why conflict or compatible?"></textarea>
    <div class="actions">
      <button onclick="submitLabel('conflict')">Conflict</button>
      <button onclick="submitLabel('compatible')">Compatible</button>
      <button onclick="submitLabel('skip')">Skip</button>
      <button onclick="nextExample()">Next →</button>
    </div>
    <p id="status"></p>
  </section>
  <script>
    let examples = [];
    let index = 0;
    const params = new URLSearchParams(window.location.search);
    const reviewer = params.get('reviewer') || 'default';
    document.getElementById('reviewer').textContent = reviewer;

    async function loadExamples() {
      const res = await fetch('/api/examples');
      examples = await res.json();
      document.getElementById('total').textContent = examples.length;
      index = 0;
      render();
    }

    function render() {
      if (!examples.length) return;
      const ex = examples[index];
      document.getElementById('pos').textContent = index + 1;
      document.getElementById('example-id').textContent = ex.id;
      document.getElementById('repo').textContent = ex.repository;
      document.getElementById('category').textContent = ex.category;
      document.getElementById('estimate').textContent = 'estimate: ' + ex.estimated_label + ' (' + ex.confidence + ')';
      document.getElementById('reason').textContent = ex.reason || '';
      document.getElementById('symbols').textContent = (ex.symbols || []).join('\\n');
      document.getElementById('left').textContent = ex.left_diff || '';
      document.getElementById('right').textContent = ex.right_diff || '';
      document.getElementById('notes').value = '';
      document.getElementById('status').textContent = '';
    }

    async function submitLabel(label) {
      const ex = examples[index];
      const payload = {
        id: ex.id,
        label,
        reason: document.getElementById('notes').value,
        reviewer,
        annotated_at: new Date().toISOString()
      };
      const res = await fetch('/api/annotate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });
      document.getElementById('status').textContent = res.ok ? 'Saved ' + label : 'Error saving';
      if (res.ok) nextExample();
    }

    function nextExample() {
      if (index < examples.length - 1) {
        index += 1;
        render();
      }
    }

    loadExamples();
  </script>
</body>
</html>
"""


def _load_examples(limit: int | None = None) -> list[dict]:
    examples = []
    if not CANDIDATES_DIR.exists():
        return examples
    for candidate_dir in sorted(CANDIDATES_DIR.iterdir()):
        if not candidate_dir.is_dir():
            continue
        meta_path = candidate_dir / "metadata.json"
        if not meta_path.exists():
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        left = (candidate_dir / "left.diff").read_text(encoding="utf-8") if (candidate_dir / "left.diff").exists() else ""
        right = (candidate_dir / "right.diff").read_text(encoding="utf-8") if (candidate_dir / "right.diff").exists() else ""
        changed = {}
        cs_path = candidate_dir / "changed_symbols.json"
        if cs_path.exists():
            changed = json.loads(cs_path.read_text(encoding="utf-8"))
        heuristic = meta.get("heuristic", {})
        examples.append(
            {
                "id": meta["id"],
                "repository": meta["repository"],
                "category": meta.get("semantic_category", "Other"),
                "estimated_label": heuristic.get("estimated_label", "uncertain"),
                "confidence": heuristic.get("confidence", 0),
                "reason": heuristic.get("reason", ""),
                "symbols": changed.get("affected_symbols", meta.get("affected_symbols", [])),
                "left_diff": left,
                "right_diff": right,
            }
        )
    if limit:
        examples = examples[:limit]
    return examples


def _annotation_path(reviewer: str) -> Path:
    if reviewer in {"A", "a", "reviewer_A"}:
        return REAL_WORLD_ROOT / "reviewer_A.jsonl"
    if reviewer in {"B", "b", "reviewer_B"}:
        return REAL_WORLD_ROOT / "reviewer_B.jsonl"
    if reviewer != "default":
        return REAL_WORLD_ROOT / f"reviewer_{reviewer}.jsonl"
    return ANNOTATIONS_JSONL


class AnnotationHandler(BaseHTTPRequestHandler):
    server_version = "QuorumReview/0.1"

    def log_message(self, fmt: str, *args) -> None:  # noqa: D401
        logger.info("%s - %s", self.address_string(), fmt % args)

    def _send_json(self, payload: object, status: int = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html: str) -> None:
        body = html.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path in {"/", "/index.html"}:
            self._send_html(HTML_PAGE)
            return
        if parsed.path == "/api/examples":
            qs = parse_qs(parsed.query)
            limit = int(qs["limit"][0]) if "limit" in qs else None
            self._send_json(_load_examples(limit=limit))
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/annotate":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self.send_error(HTTPStatus.BAD_REQUEST)
            return

        example_id = payload.get("id")
        label = payload.get("label")
        if not example_id or label not in {"conflict", "compatible", "skip"}:
            self.send_error(HTTPStatus.BAD_REQUEST)
            return

        reviewer = payload.get("reviewer") or "default"
        out_path = _annotation_path(reviewer)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "id": example_id,
            "label": label,
            "reason": payload.get("reason", ""),
            "reviewer": reviewer,
            "annotated_at": payload.get("annotated_at")
            or datetime.now(timezone.utc).isoformat(),
        }
        with out_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")
        self._send_json({"ok": True, "path": str(out_path)})


def serve(host: str = "127.0.0.1", port: int = 8765) -> None:
    REAL_WORLD_ROOT.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((host, port), AnnotationHandler)
    logger.info("Annotation UI at http://%s:%d/?reviewer=A", host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down annotation server")
    finally:
        server.server_close()
