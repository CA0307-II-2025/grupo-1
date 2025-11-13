# -*- coding: utf-8 -*-
"""
Dashboard (Dash) que usa **el mismo método del script `modelo_jerarquico.py`** para:
- Ejecutar/leer el modelo jerárquico (obesidad y sobrepeso) por **provincia**.
- Generar **mosaicos** (una sola imagen por condición con todas las provincias + país).
- Construir un **mapa interactivo** (hover muestra media e IC95% de obesidad y sobrepeso).
- Añadir un **forest plot** comparando provincias.

Rutas esperadas (como en `modelo_provincias.py`):
- Datos: `data/clean/datos_limpios.csv`
- Gráficos simulados de salida:
  - `res/graficos/graficos_simulados/obesidad/`
  - `res/graficos/graficos_simulados/sobrepeso/`

Comportamiento:
- Si no existen los mosaicos, el app **corre el modelo** (idénticos hyperparámetros y priors) y genera:
  - figuras país + por provincia (función original) y
  - **mosaicos** `posterior_prevalencia_<condicion>_grid.png`.
- Si ya existen, **no re-corre** el muestreo.

Notas:
- Para el mapa, se agregan **coordenadas de cabeceras** provinciales.
- El TOTAL país en el mapa y resúmenes se calcula con **promedio ponderado por `total`** usando los draws (igual que en el script).
"""

import os
import numpy as np
import pandas as pd
from typing import Dict, Tuple, List

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

# Para componer mosaicos y utilidades
from PIL import Image

# Importar utilidades y función de muestreo del script original
import base64


def img_to_data_uri(path: str) -> str:
    if not os.path.isfile(path):
        return ""
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode("ascii")




SUMMARY_CSV = "../res/csv/summary_prevalence_by_province.csv"

# ==========================
# Parámetros y constantes
# ==========================
CR_LATITUDE = 9.76810
CR_LONGITUDE = -84.29070
CR_ZOOM = 7
MAPBOX_STYLE = "carto-positron"

PROVINCE_ORDER = [
    "SAN JOSE",
    "ALAJUELA",
    "CARTAGO",
    "HEREDIA",
    "GUANACASTE",
    "PUNTARENAS",
    "LIMON",
]

# Cabeceras provinciales (aprox.)
PROV_POINTS = {
    "SAN JOSE": (9.92810, -84.09070),  # San José
    "ALAJUELA": (10.01630, -84.21160),  # Alajuela
    "CARTAGO": (9.86440, -83.91940),  # Cartago
    "HEREDIA": (9.99700, -84.11700),  # Heredia
    "GUANACASTE": (10.63470, -85.44360),  # Liberia (cabecera provincia)
    "PUNTARENAS": (9.97630, -84.83840),  # Puntarenas
    "LIMON": (9.99070, -83.03600),  # Limón
}

DATA_CSV = "../data/clean/datos_limpios.csv"
OUTDIR_OB = "../res/graficos/graficos_simulados_no_jer/obesidad"
OUTDIR_SOB = "../res/graficos/graficos_simulados_no_jer/sobrepeso"
MOSAIC_OB_PROV = os.path.join(
    OUTDIR_OB, "mosaico_posterior_prevalencia_obesidad_provincias.png"
)
MOSAIC_SOB_PROV = os.path.join(
    OUTDIR_SOB, "mosaico_posterior_prevalencia_sobrepeso_provincias.png"
)
MOSAIC_OB_PAIS = os.path.join(OUTDIR_OB, "posterior_prevalencia_obesidad_pais.png")
MOSAIC_SOB_PAIS = os.path.join(OUTDIR_SOB, "posterior_prevalencia_sobrepeso_pais.png")
GEOJSON_PROVINCES = "../data/geo/geoBoundaries-CRI-ADM1_simplified.geojson"

# ==========================
# Utilidades
# ==========================

def density_image_path(condicion: str, ambito: str) -> str:
    """
    Devuelve la ruta al PNG de la densidad para una condición
    ('obesidad' o 'sobrepeso') y un ámbito (provincia en MAYÚSCULAS
    como en PROVINCE_ORDER, o 'PAIS').
    """
    if condicion == "obesidad":
        base_dir = OUTDIR_OB
        prefix = "posterior_prevalencia_obesidad_"
    else:
        base_dir = OUTDIR_SOB
        prefix = "posterior_prevalencia_sobrepeso_"

    if ambito == "PAIS":
        filename = prefix + "pais.png"
    else:
        # ej: 'SAN JOSE' -> 'posterior_prevalencia_obesidad_SAN JOSE.png'
        filename = prefix + ambito + ".png"

    return os.path.join(base_dir, filename)


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def _sanitize_prov(s: str) -> str:
    # Uppercase sin tildes principales para empatar con nombres de archivos
    rep = (
        ("á", "A"),
        ("é", "E"),
        ("í", "I"),
        ("ó", "O"),
        ("ú", "U"),
        ("Á", "A"),
        ("É", "E"),
        ("Í", "I"),
        ("Ó", "O"),
        ("Ú", "U"),
        ("ï", "I"),
        ("ö", "O"),
        ("ñ", "N"),
        ("Ñ", "N"),
    )
    t = s.upper()
    for a, b in rep:
        t = t.replace(a, b)
    return t


def _load_province_geojson(path: str):
    """Carga un GeoJSON de provincias y añade 'id' normalizado por feature
    para poder unir contra df['_prov_clean']."""
    import json
    import re

    if not os.path.isfile(path):
        return None, None
    with open(path, "r", encoding="utf-8") as f:
        gj = json.load(f)

    # claves candidatas para el nombre; geoBoundaries usa 'shapeName'
    candidates = [
        "shapeName",
        "name",
        "provincia",
        "province",
        "PROVINCIA",
        "NOMBRE",
        "nom",
        "Nombre",
    ]
    prop_key = None
    try:
        props = gj["features"][0]["properties"]
        for k in candidates:
            if k in props:
                prop_key = k
                break
        if prop_key is None:
            for k, v in props.items():
                if isinstance(v, str):
                    prop_key = k
                    break
    except Exception:
        return None, None

    # normaliza y fija 'id' por feature para el join
    for feat in gj.get("features", []):
        name_raw = str(feat.get("properties", {}).get(prop_key, "")).strip()
        # muchos geoBoundaries traen "Provincia Heredia": quitamos prefijo
        name_raw = re.sub(r"^\s*Provincia\s+", "", name_raw, flags=re.I)
        name_clean = _sanitize_prov(name_raw)  # SAN JOSE, LIMON, etc.
        feat["id"] = name_clean

    return gj, "id"



def _summarize(draws: np.ndarray) -> Tuple[float, float, float, float]:
    mean = float(draws.mean())
    q2, q50, q97 = [float(x) for x in np.quantile(draws, [0.025, 0.5, 0.975])]
    return mean, q2, q50, q97


def _compose_mosaic(
    image_paths: List[str],
    outpath: str,
    cols: int = 4,
    pad: int = 10,
    bg=(255, 255, 255),
):
    imgs = [Image.open(p) for p in image_paths if os.path.isfile(p)]
    if not imgs:
        return
    # Normalizar tamaños: escalar alturas a la menor altura
    h = min(im.height for im in imgs)
    resized = []
    for im in imgs:
        w = int(im.width * (h / im.height))
        resized.append(im.resize((w, h)))
    rows = (len(resized) + cols - 1) // cols
    max_w = max(im.width for im in resized)
    grid_w = cols * max_w + (cols + 1) * pad
    grid_h = rows * h + (rows + 1) * pad
    canvas = Image.new("RGB", (grid_w, grid_h), bg)
    x = pad
    y = pad
    for i, im in enumerate(resized):
        canvas.paste(im, (x, y))
        x += max_w + pad
        if (i + 1) % cols == 0:
            x = pad
            y += h + pad
    _ensure_dir(os.path.dirname(outpath))
    canvas.save(outpath)

# ==========================
# Construcción de resúmenes para el mapa y forest plot
# ==========================
    ob_by_prov = _posterior_draws_by_province(trace_ob, meta_ob)
    sob_by_prov = _posterior_draws_by_province(trace_sob, meta_sob)

    rows = []
    for prov in PROVINCE_ORDER:
        if prov not in ob_by_prov or prov not in sob_by_prov:
            continue
        obm, ob2, ob50, ob97 = _summarize(ob_by_prov[prov])
        sbm, sb2, sb50, sb97 = _summarize(sob_by_prov[prov])
        lat, lon = PROV_POINTS[prov]
        rows.append(
            {
                "Province": prov,
                "lat": lat,
                "lon": lon,
                "ob_mean": obm,
                "ob_q2.5": ob2,
                "ob_q50": ob50,
                "ob_q97.5": ob97,
                "sb_mean": sbm,
                "sb_q2.5": sb2,
                "sb_q50": sb50,
                "sb_q97.5": sb97,
            }
        )

    # Agregar país (para leyenda / forest opcional)
    ob_country = _posterior_country_draws(trace_ob, meta_ob)
    sb_country = _posterior_country_draws(trace_sob, meta_sob)
    cobm, cob2, cob50, cob97 = _summarize(ob_country)
    csbm, csb2, csb50, csb97 = _summarize(sb_country)

    df = pd.DataFrame(rows)
    total_row = {
        "Province": "PAIS",
        "lat": (9.92810, -84.09070),
        "lon": CR_LONGITUDE,
        "ob_mean": cobm,
        "ob_q2.5": cob2,
        "ob_q50": cob50,
        "ob_q97.5": cob97,
        "sb_mean": csbm,
        "sb_q2.5": csb2,
        "sb_q50": csb50,
        "sb_q97.5": csb97,
    }
    df_total = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)
    return df_total


# ==========================
# Figuras Plotly
# ==========================


def make_map(df_summary: pd.DataFrame, metric: str = "ob_mean") -> go.Figure:
    import plotly.express as px
    import plotly.graph_objects as go
    import numpy as np

    assert metric in {"ob_mean", "sb_mean"}

    # columnas del intervalo según la métrica elegida
    lo_col = "ob_q2.5" if metric == "ob_mean" else "sb_q2.5"
    hi_col = "ob_q97.5" if metric == "ob_mean" else "sb_q97.5"

    # DataFrame por provincia (sin PAIS) y nombre limpio para el join
    dfp = df_summary[df_summary["Province"].astype(str) != "PAIS"].copy()
    dfp["_prov_clean"] = dfp["Province"].astype(str).apply(_sanitize_prov)

    # columnas auxiliares para hover (media + IC) de la métrica elegida
    dfp["__mean"] = dfp[metric].astype(float)
    dfp["__lo"] = dfp[lo_col].astype(float)
    dfp["__hi"] = dfp[hi_col].astype(float)

    # intenta cargar GeoJSON
    gj, fid_key = _load_province_geojson(GEOJSON_PROVINCES)

    if gj is not None and fid_key is not None:
        fig = px.choropleth_mapbox(
            dfp,
            geojson=gj,
            locations="_prov_clean",  # coincide con feature['id']
            featureidkey="id",
            color="__mean",
            custom_data=["__mean", "__lo", "__hi"],
            center={"lat": CR_LATITUDE, "lon": CR_LONGITUDE},
            mapbox_style=MAPBOX_STYLE,
            zoom=7.2,  # zoom más cercano a CR
            opacity=0.78,
            color_continuous_scale="Viridis",
        )

        # usa hovertext para el título (provincia) y define el contenido del hover
        fig.update_traces(
            hovertext=dfp["Province"],
            hovertemplate=(
                "<b>%{hovertext}</b><br>"
                "Media: %{customdata[0]:.4f}<br>"
                "IC95%: [%{customdata[1]:.4f}, %{customdata[2]:.4f}]"
                "<extra></extra>"
            ),
        )

        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            coloraxis_colorbar=dict(title="media"),
            height=600,
        )

        # marcador opcional para PAIS (con mismo esquema: título en negrita + media e IC)
        if "PAIS" in df_summary["Province"].values:
            pais_row = df_summary[df_summary["Province"] == "PAIS"].iloc[0]
            mean_p = float(pais_row[metric])
            lo_p = float(pais_row[lo_col])
            hi_p = float(pais_row[hi_col])
            fig.add_trace(
                go.Scattermapbox(
                    lat=[pais_row.get("lat", CR_LATITUDE)],
                    lon=[pais_row.get("lon", CR_LONGITUDE)],
                    mode="markers",
                    marker=dict(size=12, opacity=0.9),
                    name="País",
                    customdata=np.array([[mean_p, lo_p, hi_p]]),
                    hovertemplate=(
                        "<b>País</b><br>"
                        "Media: %{customdata[0]:.4f}<br>"
                        "IC95%: [%{customdata[1]:.4f}, %{customdata[2]:.4f}]"
                        "<extra></extra>"
                    ),
                )
            )

        return fig

    # ------- Fallback a puntos si no hay GeoJSON -------
    vals = dfp["__mean"].values
    vmin, vmax = float(np.nanmin(vals)), float(np.nanmax(vals))

    fig = go.Figure(
        go.Scattermapbox(
            lat=dfp["lat"],
            lon=dfp["lon"],
            text=dfp["Province"],  # título en la cajita
            mode="markers",
            marker=dict(
                size=18,
                color=dfp["__mean"],
                colorscale="Viridis",
                cmin=vmin,
                cmax=vmax,
                showscale=True,
                colorbar=dict(title="media"),
                opacity=0.9,
            ),
            customdata=np.column_stack([dfp["__mean"], dfp["__lo"], dfp["__hi"]]),
            hovertemplate=(
                "<b>%{text}</b><br>"
                "media: %{customdata[0]:.4f}<br>"
                "IC95%: [%{customdata[1]:.4f}, %{customdata[2]:.4f}]"
                "<extra></extra>"
            ),
            name="Provincia",
        )
    )
    fig.update_layout(
        mapbox=dict(
            style=MAPBOX_STYLE,
            center=dict(lat=CR_LATITUDE, lon=CR_LONGITUDE),
            zoom=7.2,
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=600,
    )
    return fig


def make_forest(df_summary: pd.DataFrame, metric: str = "ob"):
    import plotly.graph_objects as go
    import numpy as np
    import pandas as pd

    # columnas según métrica
    if metric == "ob":
        mean_col, lo_col, hi_col, title = "ob_mean", "ob_q2.5", "ob_q97.5", "Obesidad"
    else:
        mean_col, lo_col, hi_col, title = "sb_mean", "sb_q2.5", "sb_q97.5", "Sobrepeso"

    # solo provincias (sin PAIS) y orden DESC por media (mayor → menor)
    dfp = df_summary[df_summary["Province"].astype(str) != "PAIS"].copy()
    dfp = dfp.sort_values(mean_col, ascending=False)

    # orden explícito para el eje Y
    y_order = dfp["Province"].tolist()
    y_vals = pd.Categorical(dfp["Province"], categories=y_order, ordered=True)

    mean = dfp[mean_col].to_numpy()
    lo = dfp[lo_col].to_numpy()
    hi = dfp[hi_col].to_numpy()

    # barras de error asimétricas
    err_plus = hi - mean
    err_minus = mean - lo

    custom = np.column_stack([lo, hi])

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=mean,
            y=y_vals,
            mode="markers",
            marker=dict(size=8),
            error_x=dict(
                type="data",
                symmetric=False,
                array=err_plus,
                arrayminus=err_minus,
                thickness=1.2,
                width=0,
            ),
            customdata=custom,
            hovertemplate=(
                "Media: %{x:.4f}<br>"
                "IC95%: %{customdata[0]:.4f} – %{customdata[1]:.4f}"
                "<extra></extra>"
            ),
            name=title,
            showlegend=False
        )
    )

    # línea vertical *interactiva* con media país + etiqueta
    if "PAIS" in df_summary["Province"].values:
        pais_row = df_summary.loc[df_summary["Province"] == "PAIS"].iloc[0]
        pais_val = float(pais_row[mean_col])
        pais_lo = float(pais_row[lo_col])
        pais_hi = float(pais_row[hi_col])

        line_opacity = 0.6
        line_color = "#111827"  # gris oscuro (elige el que quieras)

        # 1) línea de fondo que SIEMPRE va de arriba a abajo del panel (tamaño paper)
        fig.add_vline(
            x=pais_val,
            line_dash="dot",
            line_width=1.5,
            opacity=line_opacity,
            line_color=line_color,
        )

        # desplazamiento en unidades de datos (~3.5 % del rango)
        x_min = float(np.min(lo))
        x_max = float(np.max(hi))
        dx = 0.035 * (x_max - x_min)

        fig.add_annotation(
            x=pais_val + dx,
            y=1.02,
            xref="x",
            yref="paper",
            text="",
            showarrow=True,
            align="left",
            opacity=line_opacity,
        )
        pais_row = df_summary.loc[df_summary["Province"] == "PAIS"].iloc[0]
        pais_val = float(pais_row[mean_col])
        pais_lo = float(pais_row[lo_col])
        pais_hi = float(pais_row[hi_col])

        # muchos puntos a lo largo de Y (una por provincia)
        y_line = pd.Categorical(y_order, categories=y_order, ordered=True)
        custom_line = np.column_stack(
            [[pais_lo] * len(y_order), [pais_hi] * len(y_order)]
        )

        fig.add_trace(
            go.Scatter(
                x=[pais_val] * len(y_order),
                y=y_line,
                mode="lines",
                line=dict(dash="dot", width=1.5),
                name="Media país",
                opacity=0,
                customdata=custom_line,
                hovertemplate=(
                    "Media país: %{x:.4f}<br>"
                    "IC95% país: %{customdata[0]:.4f} – %{customdata[1]:.4f}"
                    "<extra></extra>"
                ),
                showlegend=False,
            )
        )



    # altura dinámica para que quepan todas las provincias
    base_h = 140
    row_h = 40
    fig_h = base_h + row_h * max(1, len(y_order))

    fig.update_layout(
        title=dict(
            text=f"Intervalos de confianza 95% – {title}",
            x=0.5,          
            xanchor="center",
        ),
        xaxis_title="",
        yaxis_title="",
        margin=dict(l=10, r=10, t=55, b=10),
        hoverlabel=dict(bgcolor="#4f46e5", font_color="white"),
        height=fig_h,
        showlegend=False,      # si ya quitaste la leyenda
    )



    # asegura orden y evita “zoom inicial”
    fig.update_yaxes(categoryorder="array", categoryarray=y_order, automargin=True)
    fig.update_xaxes(autorange=True)

    return fig


# ==========================
# Preparación (correr/leer) y DataFrame resumen
# ==========================
def get_summary_df() -> pd.DataFrame:
    """
    Lee SUMMARY_CSV y lo valida. No crea nada si falta.
    """
    if not os.path.isfile(SUMMARY_CSV):
        raise FileNotFoundError(
            f"No se encontró el CSV requerido: {SUMMARY_CSV}. "
            "Genera el archivo antes de lanzar el dashboard."
        )

    df = pd.read_csv(SUMMARY_CSV)

    required_cols = {
        "Province",
        "ob_mean",
        "ob_q2.5",
        "ob_q50",
        "ob_q97.5",
        "sb_mean",
        "sb_q2.5",
        "sb_q50",
        "sb_q97.5",
    }
    missing = required_cols.difference(df.columns)
    if missing:
        raise ValueError(
            "El CSV no tiene las columnas necesarias: " + ", ".join(sorted(missing))
        )
    # --- Añadir lat/lon desde constantes si el CSV no las trae ---
    if ("lat" not in df.columns) or ("lon" not in df.columns):
        # normaliza nombres para hacer match con PROV_POINTS
        df["_prov_clean"] = df["Province"].astype(str).apply(_sanitize_prov)

        # mapea coords de provincias (PAIS se pone con el centro CR)
        df["lat"] = df["_prov_clean"].map(
            lambda k: PROV_POINTS.get(k, (np.nan, np.nan))[0]
        )
        df["lon"] = df["_prov_clean"].map(
            lambda k: PROV_POINTS.get(k, (np.nan, np.nan))[1]
        )

        # override para PAIS
        mask_pais = df["_prov_clean"] == "PAIS"
        if mask_pais.any():
            df.loc[mask_pais, "lat"] = CR_LATITUDE
            df.loc[mask_pais, "lon"] = CR_LONGITUDE

        df.drop(columns=["_prov_clean"], inplace=True)

        # (opcional) avisa si quedó alguna provincia sin coordenadas
        if df["lat"].isna().any() or df["lon"].isna().any():
            faltantes = df.loc[df["lat"].isna() | df["lon"].isna(), "Province"].tolist()
            raise ValueError(
                "Faltan coordenadas para: "
                + ", ".join(faltantes)
                + ". Revisa PROV_POINTS o los nombres en el CSV."
            )

    # Ordena provincias si están todas (opcional)
    try:
        order = [p for p in PROVINCE_ORDER if p in set(df["Province"])]
        # deja PAIS al final si existe
        if "PAIS" in set(df["Province"]):
            order += ["PAIS"]
        df = df.set_index("Province").loc[order].reset_index()
    except Exception:
        pass

    return df


SUMMARY_DF = get_summary_df()

# ==========================
# App Dash
# ==========================
app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.title = "Obesidad y Sobrepeso – Costa Rica"

app.layout = html.Div(
    [
        html.H1(
            "Dashboard – Costa Rica: Obesidad y Sobrepeso", style={"marginBottom": 6}
        ),
        dcc.Tabs(
            id="tabs",
            value="tab-map",
            children=[
                # TAB MAPA
                dcc.Tab(
                    label="Mapa interactivo",
                    value="tab-map",
                    children=html.Div(
                        [
                            html.Div(
                                [
                                    html.Label("Condición:"),
                                    dcc.RadioItems(
                                        id="metric-radio",
                                        options=[
                                            {"label": "Obesidad", "value": "ob_mean"},
                                            {"label": "Sobrepeso", "value": "sb_mean"},
                                        ],
                                        value="ob_mean",
                                        inline=True,
                                    ),
                                ]
                            ),
                            dcc.Graph(
                                id="map-graph",
                                figure=make_map(SUMMARY_DF, metric="ob_mean"),
                            ),
                        ]
                    ),
                ),
                # TAB DENSIDADES
                dcc.Tab(
                    label="Densidades",
                    value="tab-mosaic",  # puedes dejar este value igual
                    children=html.Div(
                        [
                            html.Div(
                                [
                                    html.Label("Condición:"),
                                    dcc.RadioItems(
                                        id="dens-cond-radio",
                                        options=[
                                            {"label": "Obesidad", "value": "obesidad"},
                                            {
                                                "label": "Sobrepeso",
                                                "value": "sobrepeso",
                                            },
                                        ],
                                        value="obesidad",
                                        inline=True,
                                    ),
                                ],
                                style={"marginBottom": 8},
                            ),

                            # Pestañas por ámbito: país + provincias
                            dcc.Tabs(
                                id="dens-scope-tabs",
                                value="PAIS",
                                children=[
                                    dcc.Tab(label="País", value="PAIS"),
                                    dcc.Tab(label="San José", value="SAN JOSE"),
                                    dcc.Tab(label="Alajuela", value="ALAJUELA"),
                                    dcc.Tab(label="Cartago", value="CARTAGO"),
                                    dcc.Tab(label="Heredia", value="HEREDIA"),
                                    dcc.Tab(label="Guanacaste", value="GUANACASTE"),
                                    dcc.Tab(label="Puntarenas", value="PUNTARENAS"),
                                    dcc.Tab(label="Limón", value="LIMON"),
                                ],
                                style={"marginBottom": 8},
                            ),

                            html.Img(
                                id="dens-img",
                                src="",
                                style={"display": "none"},
                            ),
                        ]
                    ),
                ),
                # TAB FOREST
                dcc.Tab(
                    label="Intervalos de Confianza 95%",
                    value="tab-forest",
                    children=html.Div(
                        [
                            html.Label("Condición:"),
                            dcc.RadioItems(
                                id="forest-radio",
                                options=[
                                    {"label": "Obesidad", "value": "ob"},
                                    {"label": "Sobrepeso", "value": "sb"},
                                ],
                                value="ob",
                                inline=True,
                            ),
                            dcc.Graph(
                                id="forest-graph",
                                figure=make_forest(SUMMARY_DF, metric="ob"),
                            ),
                        ]
                    ),
                ),
            ],
        ),
    ],
    style={"maxWidth": 1280, "margin": "0 auto", "padding": "12px"},
)


# === Callbacks dinámicos ===
@app.callback(Output("map-graph", "figure"), Input("metric-radio", "value"))
def update_map(metric_value):
    return make_map(SUMMARY_DF, metric=metric_value)


# --- NUEVO: mosaico como imagen "plana" con dos radios (condición y ámbito) ---


@app.callback(
    Output("dens-img", "src"),
    Output("dens-img", "style"),
    Input("dens-cond-radio", "value"),
    Input("dens-scope-tabs", "value"),
)
def update_density_image(condicion, ambito):
    # arma la ruta del PNG según condición y ámbito
    path = density_image_path(condicion, ambito)

    if not os.path.isfile(path):
        # si no existe, ocultamos la imagen
        return "", {"display": "none"}

    # si existe, la convertimos a data URI para mostrarla en el <img>
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("ascii")

    src = f"data:image/png;base64,{encoded}"
    style = {
        "maxWidth": "100%",
        "height": "auto",
        "display": "block",
        "border": "1px solid #e5e7eb",
        "borderRadius": "8px",
    }
    return src, style



@app.callback(Output("forest-graph", "figure"), Input("forest-radio", "value"))
def update_forest(metric_value):
    return make_forest(SUMMARY_DF, metric=metric_value)


# Servidor
if __name__ == "__main__":
    # Dash
    app.run(host="127.0.0.1", port=8050, debug=True)
