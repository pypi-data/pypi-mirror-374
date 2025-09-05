from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
from typing import Any, Dict, List
import html


@dataclass
class Figure:
    title: str
    data_uri: str  # base64 png


@dataclass
class Section:
    title: str
    content_html: str = ""
    figures: List[Figure] = field(default_factory=list)


@dataclass
class Report:
    profile: Dict[str, Any]
    sections: List[Section]
    summary: Dict[str, Any]

    def to_html(self, path: str, inline: bool = True) -> None:
        html_str = self._render_html()
        with open(path, "w", encoding="utf-8") as f:
            f.write(html_str)

    def _render_html(self) -> str:
        head = (
            "<meta charset='utf-8'>"
            "<style>body{font-family:Inter,system-ui,Arial;margin:24px;}"
            ".sec{margin-bottom:28px;} h1{font-size:22px;} h2{font-size:18px;}"
            ".grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:12px;}"
            ".card{border:1px solid #eee;border-radius:8px;padding:12px;}"
            "img{max-width:100%;height:auto;border-radius:6px;border:1px solid #f1f1f1;}"
            "table{border-collapse:collapse;} td,th{border:1px solid #eee;padding:6px 8px;}"
            "</style>"
        )
        prof = self.profile
        info = (
            f"<div class='card'><b>Rows:</b> {prof['n_rows']} &nbsp; "
            f"<b>Cols:</b> {prof['n_cols']} &nbsp; "
            f"<b>Memory:</b> {prof['memory_mb']:.2f} MB &nbsp; "
            f"<b>Generated:</b> {_dt.datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC" 
            "</div>"
        )

        sec_html = []
        for sec in self.sections:
            h = [f"<div class='sec'><h2>{html.escape(sec.title)}</h2>"]
            if sec.content_html:
                h.append(sec.content_html)
            if sec.figures:
                h.append("<div class='grid'>")
                for fig in sec.figures:
                    h.append(
                        f"<div class='card'><div><b>{html.escape(fig.title)}</b></div>"
                        f"<img src='data:image/png;base64,{fig.data_uri}'/></div>"
                    )
                h.append("</div>")
            h.append("</div>")
            sec_html.append("".join(h))

        # Simple summary highlights
        top_feats = self.summary.get("top_features", [])
        tf_html = "".join(f"<li>{html.escape(n)} — {m:.3f}</li>" for n, m in top_feats)
        summary_block = f"<div class='card'><b>Top Features</b><ul>{tf_html}</ul></div>"

        return (
            "<!doctype html><html><head>" + head + "</head><body>"
            + "<h1>Visea Report</h1>" + info + summary_block + "".join(sec_html)
            + "</body></html>"
        )
