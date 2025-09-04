# Copyright (c) 2025 LIN XIAO DAO
# Licensed under the MIT License. See LICENSE file in the project root for full license text.

from __future__ import annotations

from typing import Mapping, Any
import numpy as np
from numpy.typing import NDArray

import dash
from dash import dcc, html, Output, Input, State
import plotly.graph_objects as go

from .utils import vector_MAE


class OverallPlot:
    """
    Interactive comparison dashboard for three probability vectors.

    The component overlays three bar traces:
    - ``Statevector`` (reference/ground truth)
    - backend (e.g., simulator or hardware), provided via ``y["backend"]``
    - ``Autoencoder`` (mitigated result)

    Attributes
    ----------
    y : Mapping[str, Any]
        A mapping containing:
        - ``"backend"`` : str
            The backend name for labeling.
        - ``"Statevector"`` : array-like of shape (n_bins,)
        - ``"noisy_input"`` : array-like of shape (n_bins,)
        - ``"Autoencoder"`` : array-like of shape (n_bins,)

    backend : str
        The noisy backend name uses in this job.
    """

    def __init__(self, y: Mapping[str, Any]) -> None:
        # Extract and normalize inputs
        self.backend: str = str(y["backend"])
        self.y0: NDArray[np.floating] = np.asarray(y["Statevector"], dtype=float)
        self.y1: NDArray[np.floating] = np.asarray(y["noisy_input"], dtype=float)
        self.y2: NDArray[np.floating] = np.asarray(y["Autoencoder"], dtype=float)

        # Basic shape validation（保持你原本的，不新增任何檢查）
        n = self.y0.shape[0]
        if self.y1.shape[0] != n or self.y2.shape[0] != n:
            raise ValueError(
                "Input arrays must have the same length: "
                f"len(Statevector)={n}, len(noisy_input)={self.y1.shape[0]}, "
                f"len(Autoencoder)={self.y2.shape[0]}"
            )
        if not np.isfinite(self.y0).all() or not np.isfinite(self.y1).all() or not np.isfinite(self.y2).all():
            raise ValueError("Input arrays contain NaN or Inf.")

        self.x: NDArray[np.int_] = np.arange(n)

        # Prebuild traces for quick toggling
        self.trace_a = go.Bar(
            name="Statevector", x=self.x, y=self.y0, marker_color="rgba(214, 39, 40, 1)"
        )
        self.trace_b = go.Bar(
            name=self.backend, x=self.x, y=self.y1, marker_color="rgba(31, 119, 180, 0.8)"
        )
        self.trace_c = go.Bar(
            name="Autoencoder", x=self.x, y=self.y2, marker_color="rgba(44, 160, 44, 0.5)"
        )

    def plot_result(self, *, debug: bool = False) -> None:
        """
        Launch the interactive dashboard.
        """
        TITLE_SIZE_MAIN = 26
        TITLE_SIZE_SIDE = 24
        AXIS_TITLE_SIZE = 20
        TICK_SIZE = 16
        BUTTON_FONT_SIZE = 20

        def create_bar_chart(show_a: bool = True, show_b: bool = False, show_c: bool = False) -> go.Figure:
            fig = go.Figure()
            if show_a:
                fig.add_trace(self.trace_a)
            if show_b:
                fig.add_trace(self.trace_b)
            if show_c:
                fig.add_trace(self.trace_c)

            # Transparent baseline to stabilize hover and axis
            fig.add_trace(
                go.Bar(
                    x=self.x,
                    y=[0] * len(self.x),
                    marker_color="rgba(0,0,0,0)",
                    showlegend=False,
                    hoverinfo="skip",
                )
            )

            fig.update_layout(
                title="Probability for Each Basis Vector",
                title_x=0.5,
                title_font=dict(size=TITLE_SIZE_MAIN),
                barmode="overlay",
                xaxis=dict(
                    title="Basis vector (decimal)",
                    title_font=dict(size=AXIS_TITLE_SIZE),
                    tickfont=dict(size=TICK_SIZE),
                ),
                yaxis=dict(
                    title="Probability",
                    title_font=dict(size=AXIS_TITLE_SIZE),
                    tickfont=dict(size=TICK_SIZE),
                    range=[0, 1],
                ),
                transition=dict(duration=500, easing="cubic-in-out"),
                showlegend=False,
                hovermode="x unified",
                margin=dict(l=70, r=30, t=80, b=110)
            )
            return fig

        def create_noise_fig() -> go.Figure:
            mae_noisy = float(vector_MAE(self.y0, self.y1))
            mae_denoised = float(vector_MAE(self.y0, self.y2))
            ymax = max(mae_noisy, mae_denoised, 0.0) * 1.2
            if ymax == 0.0:
                ymax = 1e-6  # avoid [0, 0] range
            fig = go.Figure()
            fig.add_trace(
                go.Bar(
                    x=["Unmitigated", "Mitigated"],
                    y=[mae_noisy, mae_denoised],
                    marker_color="rgba(255, 206, 86, 0.8)",
                )
            )
            fig.update_layout(
                title="Average Noise Level (MAE)",
                title_x=0.5,
                title_font=dict(size=TITLE_SIZE_SIDE),
                yaxis=dict(
                    title="MAE",
                    title_font=dict(size=AXIS_TITLE_SIZE),
                    tickfont=dict(size=TICK_SIZE),
                    range=[0, ymax],
                ),
                xaxis=dict(
                    title="",
                    title_font=dict(size=AXIS_TITLE_SIZE),
                    tickfont=dict(size=TICK_SIZE),
                ),
                showlegend=False,
                hovermode="x unified",
                margin=dict(l=70, r=30, t=80, b=110)
            )
            return fig

        def button_style() -> dict[str, str]:
            return {
                "background": "none",
                "border": "none",
                "color": "black",
                "fontSize": f"{BUTTON_FONT_SIZE}px",
                "margin": "0 10px",
                "cursor": "pointer",
            }

        app = dash.Dash(__name__)
        app.layout = html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        dcc.Graph(
                                            id="bar-chart",
                                            figure=create_bar_chart(),
                                            style={"height": "520px"}
                                        ),
                                        html.Div(
                                            [
                                                html.Button("🟥 Theorem", id="btn-a", n_clicks=0, style=button_style()),
                                                html.Button(f"🟦 {self.backend}", id="btn-b", n_clicks=0, style=button_style()),
                                                html.Button("🟩 Autoencoder", id="btn-c", n_clicks=0, style=button_style()),
                                            ],
                                            style={
                                                "position": "absolute",
                                                "left": 0,
                                                "right": 0,
                                                "bottom": "12px",
                                                "textAlign": "center",
                                                "zIndex": 10,
                                            },
                                        ),
                                    ],
                                    style={"position": "relative"}
                                ),
                            ],
                            style={
                                "display": "inline-block",
                                "width": "60%",
                                "verticalAlign": "top"
                            },
                        ),

                        html.Div(
                            [dcc.Graph(id="noise-graph", figure=create_noise_fig())],
                            style={
                                "display": "inline-block",
                                "width": "40%",
                                "verticalAlign": "top",
                                "height": "520px"
                            },
                        ),
                        dcc.Store(id="visible-traces", data={"A": True, "B": False, "C": False}),
                    ]
                )
            ]
        )

        @app.callback(
            Output("bar-chart", "figure"),
            Output("visible-traces", "data"),
            Input("btn-a", "n_clicks"),
            Input("btn-b", "n_clicks"),
            Input("btn-c", "n_clicks"),
            State("visible-traces", "data"),
            prevent_initial_call=True,
        )
        def toggle_traces(n_a, n_b, n_c, visibility):
            ctx = dash.callback_context  # for Dash >=2.9 you can also use: from dash import ctx
            btn_id = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else ""
            if btn_id == "btn-a":
                visibility["A"] = not visibility["A"]
            elif btn_id == "btn-b":
                visibility["B"] = not visibility["B"]
            elif btn_id == "btn-c":
                visibility["C"] = not visibility["C"]

            fig = create_bar_chart(
                show_a=visibility["A"], show_b=visibility["B"], show_c=visibility["C"]
            )
            return fig, visibility

        app.run(debug=debug)
