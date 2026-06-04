from dash import html, dcc
from config import REFRESH_INTERVAL


def create_layout(
    fig_past,
    fig_future_temp,
    fig_future_rain,
    fig_today,
    rain_5days,
    temp_max_12h,
    temp_min_12h,
    rain_start_time,
):
    return html.Div(
        [
            dcc.Interval(
                id="interval-component",
                interval=REFRESH_INTERVAL,
                n_intervals=0,
            ),
            # Most-Top
            html.Div(
                [
                    # Title and insight card
                    html.Div(
                        [
                            # Title Top-left
                            html.Div(
                                [
                                    html.Img(
                                        src="assets/Plantly_icon.png",
                                        id="logo",
                                        style={
                                            "width": "34px",
                                            "height": "34px",
                                            "marginLeft": "8px",
                                            "marginBottom": "-10px",
                                        },
                                    ),
                                    html.H1(
                                        "PLANTly",
                                        id="title",
                                        style={
                                            "marginTop": "0",
                                            "marginBottom": "-8px",
                                            "marginLeft": "6px",
                                            "fontSize": "38px",
                                            "fontWeight": "500",
                                            "color": "#5f6f65",
                                        },
                                    ),
                                ],
                                className="titles",
                                style={
                                    "display": "flex",
                                    "alignItems": "center",
                                    "width": "fit-content",
                                    "gap": "0px",
                                    "borderBottom": "4px solid rgba(120, 92, 62, 0.65)",
                                    "paddingBottom": "0",
                                    "paddingRight": "8px",
                                },
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        id="insight-water",
                                        style={
                                            "fontSize": "16px",
                                            "fontWeight": "500",
                                            "color": "#5f6f65",
                                        },
                                    ),
                                    html.Div(
                                        id="insight-solar",
                                        style={
                                            "fontSize": "16px",
                                            "fontWeight": "500",
                                            "color": "#5f6f65",
                                        },
                                    ),
                                ],
                                className="cards",
                                id="insight-card",
                                style={
                                    "backgroundColor": "#ece7dc",
                                    "padding": "14px 18px",
                                    "borderRadius": "20px",
                                    "marginTop": "10px",
                                    "boxShadow": "0 2px 8px rgba(0,0,0,0.05)",
                                },
                            ),
                        ]
                    ),
                    # Info card Top-right
                    html.Div(
                        [
                            html.Div("💧Past 5days"),
                            html.Div(f"{rain_5days:.0f} mm", id="rain-5days-value"),
                            html.Div("🕰️Next"),
                            html.Div(
                                "------",
                                style={"color": "rgba(0,0,0,0.6)"},
                            ),
                            html.Div("🌡️12h Max"),
                            html.Div(
                                f"{temp_max_12h:.1f} ℃",
                                id="temp-max-value",
                                style={"color": "#e74c3c"},
                            ),
                            html.Div("🌡️12h min"),
                            html.Div(
                                f"{temp_min_12h:.1f} ℃",
                                id="temp-min-value",
                                style={"color": "#4dabf7"},
                            ),
                            html.Div("🌂Rain start"),
                            html.Div(f"{rain_start_time}", id="rain-start-value"),
                        ],
                        className="cards",
                        id="info-card",
                        style={
                            "display": "grid",
                            "gridTemplateColumns": "auto 1fr",
                            "rowGap": "1",
                            "columnGap": "8px",
                            "padding": "12px",
                            "backgroundColor": "#f3f1eb",
                            "borderRadius": "20px",
                            "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.1)",
                            "width": "220px",
                            "height": "auto",
                            "fontSize": "16px",
                            "lineHeight": "1.4",
                            "marginLeft": "auto",
                            "position": "relative",
                            "zIndex": 10,
                        },
                    ),
                ],
                className="top-section",
                style={"display": "flex", "gap": "10px", "alignItems": "flex-start"},
            ),
            # Top graphs
            html.Div(
                [
                    # Left
                    html.Div(
                        [
                            dcc.Graph(
                                figure=fig_past,
                                responsive=True,
                                style={
                                    "height": "100%",
                                    "width": "100%",
                                },
                                config={"displayModeBar": False},
                            )
                        ],
                        id="past-graph",
                        style={
                            "width": "40%",
                            "height": "300px",
                            "backgroundColor": "#ece7dc",
                            "borderRadius": "20px",
                            "padding": "6px",
                            "boxShadow": "0 4px 12px rgba(0,0,0,0.05)",
                        },
                    ),
                    # Right
                    html.Div(
                        [
                            dcc.Graph(
                                id="future-temp-graph",
                                figure=fig_future_temp,
                                clear_on_unhover=True,
                                style={
                                    "flex": 7,
                                    "minHeight": 0,
                                    "marginBottom": "0px",
                                },
                                config={"displayModeBar": False},
                                responsive=True,
                            ),
                            dcc.Graph(
                                id="future-rain-graph",
                                figure=fig_future_rain,
                                clear_on_unhover=True,
                                style={
                                    "flex": 3,
                                    "minHeight": 0,
                                    "marginTop": "-10px",
                                },
                                config={"displayModeBar": False},
                                responsive=True,
                            ),
                            dcc.Tooltip(
                                id="future-tooltip",
                                targetable=False,
                                style={
                                    "pointerEvents": "none",
                                    "zIndex": 9999,
                                    "backgroundColor": "rgba(255,255,255,0.95)",
                                    "borderRadius": "19px",
                                    "padding": "8px",
                                    "boxShadow": "0 4px 12px rgba(0,0,0,0.12)",
                                },
                            ),
                        ],
                        id="future-graph",
                        style={
                            "width": "60%",
                            "height": "300px",
                            "display": "flex",
                            "flexDirection": "column",
                            "backgroundColor": "#ece7dc",
                            "borderRadius": "20px",
                            "padding": "6px",
                            "boxShadow": "0 4px 12px rgba(0,0,0,0.05)",
                            "position": "relative",
                        },
                    ),
                ],
                className="Upper-graphs",
                style={
                    "display": "flex",
                    "gap": "15px",
                },
            ),
            # Bottom Graph
            html.Div(
                [
                    # left
                    # html.Div(""),
                    # center
                    html.Div(
                        [
                            dcc.Graph(
                                figure=fig_today,
                                clear_on_unhover=True,
                                style={
                                    "height": "400px",
                                    "width": "100%",
                                    "padding": "0px",
                                    "margin": "0",
                                },
                                config={"displayModeBar": False, "displaylogo": False},
                                responsive=True,
                            ),
                            dcc.Tooltip(
                                id="today-tooltip",
                                # direction="top",
                                style={
                                    "zIndex": 9999,
                                    "backgroundColor": "rgba(255,255,255,0.95)",
                                    "borderRadius": "12px",
                                    "padding": "8px",
                                    "boxShadow": "0 4px 12px rgba(0,0,0,0.12)",
                                },
                            ),
                        ],
                        id="today-graph",
                        style={
                            "display": "flex",
                            "flexDirection": "column",
                            "position": "relative",
                            "overflow": "visible",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "padding": "0",
                            "margin": "0",
                            "width": "100%",
                            "height": "100%",
                        },
                    ),
                    # right
                    # html.Div(""),
                ],
                className="Lower-graph",
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "stretch",
                    "backgroundColor": "#ece7dc",
                    "borderRadius": "20px",
                    "padding": "4px",
                    "marginTop": "15px",
                    "boxShadow": "0 4px 12px rgba(0,0,0,0.05)",
                },
            ),
        ],
        className="app-container",
        style={
            "backgroundColor": "#c7e3c7",
            "minHeight": "60vh",
            "borderRadius": "20px",
            "padding": "20px",
            "margin": "0",
            "fontFamily": "Zen Maru Gothic",
            "position": "relative",
        },
    )
