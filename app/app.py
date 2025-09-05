# app.py
import json
import dash
from dash import dcc, html
import plotly.graph_objs as go

# Configuración inicial Costa Rica
CR_LATITUDE = 9.7489
CR_LONGITUDE = -83.7534
CR_ZOOM = 7
mapbox_style = ["open-street-map", "carto-positron", "carto-darkmatter"]

# Cargar GeoJSON local de Costa Rica
with open("CRI.geo.json", "r", encoding="utf-8") as f:
    cr_geojson = json.load(f)

# Crear mapa de Costa Rica
def create_map_geomap_cr():
    fig = go.Figure(
        go.Choroplethmapbox(
            geojson=cr_geojson,
            locations=["CRI"],  # Código de país
            z=[1],
            colorscale="Blues",
            showscale=False,
        )
    )
    fig.update_layout(
        mapbox_style=mapbox_style[1],
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
@app.callback(
    dash.Output("tabs-content", "children"),
    [dash.Input("tabs", "value")]
)
def render_content(tab):
    if tab == "tab-1":
        return dcc.Graph(id="geomap-cr", figure=create_map_geomap_cr())
    elif tab == "tab-2":
        return html.Div([html.H3("Aquí van los resultados")])
    elif tab == "tab-3":
        return html.Div([html.H3("Otra sección del dashboard")])

# Ejecutar servidor
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)
