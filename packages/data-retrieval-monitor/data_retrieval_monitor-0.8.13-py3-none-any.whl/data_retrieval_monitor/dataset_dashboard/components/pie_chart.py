from typing import Dict
from ..constants import JOB_STATUS_ORDER, JOB_RGB

class PieChartComponent:
    def figure(self, title_text: str, counts: Dict[str,int]):
        labels = [s.title() for s in JOB_STATUS_ORDER]
        raw_values = [int(counts.get(s, 0) or 0) for s in JOB_STATUS_ORDER]
        total = sum(raw_values)

        colors, values, texttempl = [], [], []
        if total == 0:
            for s in JOB_STATUS_ORDER:
                r, g, b = JOB_RGB[s]
                colors.append(f"rgba({r},{g},{b},0.12)")
                values.append(1)
                texttempl.append("%{label}")
            hover = "%{label}: 0<extra></extra>"
        else:
            for s, v in zip(JOB_STATUS_ORDER, raw_values):
                r, g, b = JOB_RGB[s]
                colors.append(f"rgba({r},{g},{b},{0.9 if v>0 else 0.0})")
                values.append(v)
                texttempl.append("" if v == 0 else "%{label} %{percent}")
            hover = "%{label}: %{value}<extra></extra>"

        trace = {
            "type": "pie",
            "labels": labels,
            "values": values,
            "hole": 0.45,
            "marker": {"colors": colors, "line": {"width": 0}},
            "texttemplate": texttempl,
            "textposition": "outside",
            "hovertemplate": hover,
            "showlegend": True,
        }
        return {
            "data": [trace],
            "layout": {
                "annotations": [{
                    "text": title_text, "xref": "paper", "yref": "paper",
                    "x": 0.5, "y": 1.12, "xanchor": "center", "yanchor": "top",
                    "showarrow": False, "font": {"size": 13}
                }],
                "margin": {"l": 10, "r": 10, "t": 26, "b": 10},
                "legend": {"orientation": "h"},
                "title": {"text": ""}
            }
        }