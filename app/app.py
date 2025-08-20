# app.py
import dash
from dash import dcc, html
import plotly.graph_objs as go

# Configuración inicial
INIT_LATITUDE = 3.4455217746834705
INIT_LONGITUDE = 27.607108241243623
INIT_ZOOM = 1.6637151294876884
mapbox_style = ["open-street-map", "carto-positron", "carto-darkmatter"]

# Crear mapa vacío
def create_map_geomap_empty():
    fig = go.Figure(go.Choroplethmapbox())  # vacío
    fig.update_layout(
        mapbox_style=mapbox_style[1],  # carto-positron
        mapbox_zoom=INIT_ZOOM,
        mapbox_center={"lat": INIT_LATITUDE, "lon": INIT_LONGITUDE},
        margin={"r":0,"t":0,"l":0,"b":0},
        height=600
    )
    return fig

# Inicializar Dash
app = dash.Dash(__name__)
app.title = "Mapa vacío"

# Layout
app.layout = html.Div([
    html.H1("Mapa vacío estilo World Atlas"),
    dcc.Graph(id="geomap-empty", figure=create_map_geomap_empty())
])

# Ejecutar servidor
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)
