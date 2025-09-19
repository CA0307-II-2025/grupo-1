# app.py
import dash
from dash import dcc, html
import plotly.graph_objs as go


CR_LATITUDE = 9.7489
CR_LONGITUDE = -83.7534
CR_ZOOM = 7
mapbox_style = ["open-street-map", "carto-positron", "carto-darkmatter"]


def create_map_cr_basico():
    fig = go.Figure()

    # (Opcional) un marcador en San José
    fig.add_trace(
        go.Scattermapbox(
            lat=[9.9281],
            lon=[-84.0907],
            mode="markers",
            marker=dict(size=10),
            name="San José",
        )
    )

    fig.update_layout(
        mapbox_style=mapbox_style[1],  # "carto-positron"
        mapbox_zoom=CR_ZOOM,
        mapbox_center={"lat": CR_LATITUDE, "lon": CR_LONGITUDE},
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=600,
    )
    return fig


# Inicializar Dash
app = dash.Dash(__name__)
app.title = "Mapa Costa Rica"

# Layout con Tabs
app.layout = html.Div(
    [
        html.H1("Dashboard - Costa Rica"),
        dcc.Tabs(
            id="tabs",
            value="tab-1",
            children=[
                dcc.Tab(label="Mapa de Costa Rica", value="tab-1"),
                dcc.Tab(label="Resultados", value="tab-2"),
                dcc.Tab(label="Otra sección", value="tab-3"),
            ],
        ),
        html.Div(id="tabs-content"),
    ]
)


# Callback para manejar contenido de Tabs
@app.callback(dash.Output("tabs-content", "children"), [dash.Input("tabs", "value")])
def render_content(tab):
    if tab == "tab-1":
        return dcc.Graph(id="geomap-cr", figure=create_map_cr_basico())
    elif tab == "tab-2":
        return html.Div([html.H3("Aquí van los resultados")])
    elif tab == "tab-3":
        return html.Div([html.H3("Otra sección del dashboard")])


# Ejecutar servidor
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)
