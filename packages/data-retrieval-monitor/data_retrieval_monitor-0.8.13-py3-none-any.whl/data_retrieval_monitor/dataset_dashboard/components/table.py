from typing import List, Optional, Tuple
from dash import html, dcc
import dash_bootstrap_components as dbc
from .compute import best_status
from ..constants import JOB_STATUS_ORDER, JOB_RGB, STAGES

class TableComponent:
    """Intrinsic-width table; no inner scrollbar; compact chunk badges with proc/log + clipboard."""
    def __init__(self, log_linker, clipboard_fallback_open: bool):
        self.linker = log_linker
        self.fallback_open = bool(clipboard_fallback_open)

    @staticmethod
    def _shade(status: Optional[str], alpha=0.18):
        if not status: return {"backgroundColor":"#FFFFFF"}
        r,g,b = JOB_RGB[status]
        return {"backgroundColor": f"rgba({r},{g},{b},{alpha})"}

    def _clipboard_button(self, text: str):
        """
        Small 📋 with invisible Clipboard overlay — compact and spaced so the
        next chunk doesn't crowd it.
        """
        icon = html.Span("🗂️", title=f"Copy: {text}",
                         style={"display":"inline-block","fontSize":"12px","opacity":0.9,
                                "marginLeft":"4px","cursor":"pointer"})
        overlay = dcc.Clipboard(
            content=text, title="Copy",
            style={"position":"absolute","left":0,"top":0,"width":"1.4em","height":"1.4em",
                   "opacity":0.01,"zIndex":5,"cursor":"pointer","border":0,"background":"transparent"}
        )
        # marginRight adds a little breathing room before the next chunk
        return html.Span([icon, overlay],
                         style={"position":"relative","display":"inline-block","marginRight":"8px"})

    def _chunk_badge_and_links(self, ch: dict, idx: int):
        # label is c0, c1, c2...; original id goes to title
        label = f"c{idx}"
        st  = (ch.get("status") or "waiting").lower()
        proc = ch.get("proc")
        raw  = ch.get("log")
        href = self.linker.href_for(raw)

        badge = html.Span(
            label,
            title=str(ch.get("id") or label),
            style={"display":"inline-block","padding":"2px 6px","borderRadius":"8px",
                   "fontSize":"12px","marginRight":"6px", **self._shade(st, 0.35)}
        )
        bits = [badge]

        if proc:
            bits.append(html.A("p", href=proc, target="_blank", title="proc",
                               style={"marginRight":"6px","textDecoration":"underline"}))

        # Show an 'l' link AND a clipboard right next to it (copies the link).
        # If we don't have a linkable URL, show clipboard that copies the raw path.
        if href:
            link = html.A("l", href=href, target="_blank", title="open log",
                          style={"marginRight":"0","textDecoration":"underline","fontSize":"12px"})
            bits.append(link)
            bits.append(self._clipboard_button(href))      # copy the viewer URL
        elif raw:
            bits.append(self._clipboard_button(str(raw)))   # copy raw path if no link

        return bits

    def _chunk_block(self, chunks: List[dict], chunks_per_line: int):
        """Render chunk badges grouped by N per line."""
        if not chunks:
            return html.I("—", className="text-muted")
        cpl = max(1, int(chunks_per_line or 999_999))
        lines = []
        for i in range(0, len(chunks), cpl):
            seg = chunks[i:i+cpl]
            seg_nodes = []
            for j, ch in enumerate(seg):
                seg_nodes.extend(self._chunk_badge_and_links(ch, idx=i + j))
            lines.append(html.Div(seg_nodes, style={"whiteSpace":"nowrap"}))
        return html.Div(lines, style={"display":"grid","rowGap":"2px"})

    def build(self, store_dict: dict, labels: dict,
              owner: Optional[str], mode: Optional[str],
              groups_per_row: int, entries_sorted: List[Tuple],
              chunks_per_line: int) -> html.Div:
        gpr = max(1, min(int(groups_per_row or 1), 6))

        # header in exact order: Archive, Stage, Enrich, Consolidate
        head_cells = []
        for _ in range(gpr):
            head_cells.extend([html.Th("Dataset", style={"whiteSpace":"nowrap"})] +
                              [html.Th(s.title(), style={"whiteSpace":"nowrap"}) for s in STAGES])
        head = html.Thead(html.Tr(head_cells))

        def _chunked(lst: List, n: int) -> List[List]:
            return [lst[i:i+n] for i in range(0, len(lst), n)]

        # Always show only dataset name (no owner prefix)
        body_rows = []
        for row_groups in _chunked(entries_sorted, gpr):
            tds: List[html.Td] = []
            for _, _own, _md, dn, d_map in row_groups:
                stage_status = {stg: best_status((d_map.get(stg) or {"counts":{}})["counts"]) for stg in STAGES}
                title = dn
                cells = [html.Td(title, style={"fontWeight":"600","whiteSpace":"nowrap"})]
                for stg in STAGES:
                    leaf = d_map.get(stg, {"counts":{s:0 for s in JOB_STATUS_ORDER}, "chunks":[]})
                    cells.append(html.Td(self._chunk_block(leaf.get("chunks", []), chunks_per_line),
                                         style={"verticalAlign":"top","padding":"6px 10px","whiteSpace":"nowrap",
                                                **self._shade(stage_status[stg], 0.18)}))
                tds.extend(cells)
            if len(row_groups) < gpr:
                for _ in range(gpr - len(row_groups)):
                    tds.extend([html.Td(""), html.Td(""), html.Td(""), html.Td(""), html.Td("")])
            body_rows.append(html.Tr(tds))

        if not body_rows:
            body_rows = [html.Tr(html.Td("No data", colSpan=5*gpr, className="text-muted"))]

        # Add ~10 characters of space on the right edge
        return dbc.Table(
            [head, html.Tbody(body_rows)],
            bordered=True, hover=False, size="sm", className="mb-1",
            style={
                "tableLayout": "auto",
                "width": "auto",
                "display": "inline-table",
                "marginRight":"10ch"
                # removed marginLeft/marginRight — gutters now live at the page level
            },
        )
    
def chunkline(chunks: List[dict], linker, chunks_per_line: Optional[int] = None):
    """
    Backward-compatible helper.

    Args:
        chunks: list of chunk dicts (with optional 'id', 'status', 'proc', 'log')
        linker: an instance of LogLinker (must have .href_for)
        chunks_per_line: if provided, wrap every N chunks to a new line;
                         default is a very large number (single line)

    Returns:
        dash.html.Div containing the rendered badges/links.
    """
    comp = TableComponent(linker, clipboard_fallback_open=False)
    return comp._chunk_block(chunks or [], chunks_per_line or 999_999)