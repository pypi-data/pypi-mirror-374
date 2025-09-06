import pathlib, threading, hashlib
from typing import Any
from urllib.parse import quote
from flask import Response, abort

class LogLinker:
    """
    Maps input log paths/URLs to safe, *relative* hrefs:
      - http(s) URLs → returned as-is
      - inside LOG_ROOT → logview/root/<rel>
      - absolute outside LOG_ROOT → cached once → logview/mem/<key>
    """
    def __init__(self, log_root: pathlib.Path | str):
        self.root = pathlib.Path(log_root).resolve()
        self._mem = {}            # key -> text
        self._lock = threading.RLock()

    def _key_for_abs(self, abs_path: pathlib.Path) -> str:
        h = hashlib.sha1(str(abs_path).encode("utf-8")).hexdigest()[:16]
        return f"abs/{h}/{abs_path.name}"

    def _read_text(self, p: pathlib.Path) -> str | None:
        try:
            return p.read_text("utf-8", errors="replace")
        except Exception:
            try:
                return p.read_bytes().decode("utf-8", errors="replace")
            except Exception:
                return None

    def href_for(self, value: str | None) -> str | None:
        if not value:
            return None
        v = str(value).strip()
        if v.startswith("http://") or v.startswith("https://"):
            return v

        p = pathlib.Path(v)
        try:
            if p.is_absolute():
                abs_p = p.resolve()
                try:
                    rel = abs_p.relative_to(self.root).as_posix()
                    # relative URL (no leading slash) so proxy prefixes work
                    return f"logview/root/{quote(rel)}"
                except Exception:
                    # outside LOG_ROOT → cache and serve from memory
                    txt = self._read_text(abs_p)
                    if txt is None:
                        return None
                    key = self._key_for_abs(abs_p)
                    with self._lock:
                        self._mem.setdefault(key, txt)
                    return f"logview/mem/{quote(key)}"
            else:
                # relative path within LOG_ROOT
                rel = p.as_posix().lstrip("./")
                if ".." in rel:
                    return None
                return f"logview/root/{quote(rel)}"
        except Exception:
            return None


def _html_page(title: str, body_text: str) -> str:
    from html import escape
    return f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8"/>
    <title>{escape(title)}</title>
    <style>
      body {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
              margin:16px; }}
      pre {{ white-space: pre-wrap; word-break: break-word; }}
      .meta {{ color:#666; margin-bottom:8px; }}
    </style>
  </head>
  <body>
    <div class="meta">{escape(title)}</div>
    <pre>{escape(body_text)}</pre>
  </body>
</html>"""


def _ensure_linker(linker_or_root: Any) -> LogLinker:
    if isinstance(linker_or_root, LogLinker):
        return linker_or_root
    return LogLinker(linker_or_root)


def register_log_routes(server, linker_or_root: LogLinker | str | pathlib.Path):
    """
    Register:
      - GET logview/root/<rel>  → HTML viewer for files in LOG_ROOT
      - GET logview/mem/<key>   → HTML viewer for cached absolute files
      - (Also keep text endpoints /logs and /logmem for debugging)
    """
    linker = _ensure_linker(linker_or_root)
    root = linker.root

    # HTML viewer for files inside LOG_ROOT
    @server.get("/logview/root/<path:rel>")
    def logview_root(rel: str):
        clean = rel.lstrip("/").replace("\\", "/")
        if ".." in clean:
            return abort(400)
        path = (root / clean).resolve()
        try:
            path.relative_to(root)
        except Exception:
            return Response(_html_page("Log outside root", f"(outside root) {clean}"), mimetype="text/html")
        if not path.exists():
            return Response(_html_page("Log not found", clean), mimetype="text/html", status=404)
        txt = linker._read_text(path) or ""
        return Response(_html_page(f"Log: {clean}", txt), mimetype="text/html")

    # HTML viewer for cached absolute files
    @server.get("/logview/mem/<path:key>")
    def logview_mem(key: str):
        clean = key.lstrip("/").replace("\\", "/")
        with linker._lock:
            txt = linker._mem.get(clean)
        if txt is None:
            return Response(_html_page("Log not cached", clean), mimetype="text/html", status=404)
        return Response(_html_page(f"Log (cached): {clean}", txt), mimetype="text/html")

    # Optional plain-text endpoints (debug)
    @server.get("/logs/<path:rel>")
    def logs_plain(rel: str):
        clean = rel.lstrip("/").replace("\\", "/")
        if ".." in clean:
            return abort(400)
        p = (root / clean).resolve()
        try:
            p.relative_to(root)
        except Exception:
            return Response(f"(outside root) {clean}", mimetype="text/plain")
        if not p.exists():
            return Response(f"(log not found: {clean})", mimetype="text/plain", status=404)
        txt = linker._read_text(p) or ""
        return Response(txt, mimetype="text/plain")

    @server.get("/logmem/<path:key>")
    def logmem_plain(key: str):
        clean = key.lstrip("/").replace("\\", "/")
        with linker._lock:
            txt = linker._mem.get(clean)
        if txt is None:
            return Response(f"(log not cached: {clean})", mimetype="text/plain", status=404)
        return Response(txt, mimetype="text/plain")