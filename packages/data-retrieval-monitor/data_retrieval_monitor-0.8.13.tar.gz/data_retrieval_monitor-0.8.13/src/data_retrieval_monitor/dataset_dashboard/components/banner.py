from dash import html

class BannerComponent:
    def __init__(self, gutter_ch: int = 10):
        # keep banner aligned with the page gutters (10ch by default)
        self.gutter_ch = gutter_ch

    def render(self, title: str):
        pad = f"{self.gutter_ch}ch"
        return html.Div(
            [
                html.Div(title, className="h2 fw-bold"),
                html.Div(id="now-indicator", className="text-muted"),
            ],
            style={
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "space-between",
                "width": "100%",
                "paddingLeft": pad,   # ← shift right
                "paddingRight": pad,  # ← keep symmetry
            },
        )