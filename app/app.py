# -*- coding: utf-8 -*-
"""
Dashboard utiliza los resultados generados para:
- Construir un **mapa interactivo** (hover muestra media e IC95% de obesidad y sobrepeso).
- Añadir una comparación de intervalos de confianza entre provincias.
"""

import os
import numpy as np
import pandas as pd
from typing import Tuple, List

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

from PIL import Image

import base64


def img_to_data_uri(path: str) -> str:
    if not os.path.isfile(path):
        return ""
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode("ascii")


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
MOSAIC_OB_PAIS = os.path.join(OUTDIR_OB, "posterior_prevalencia_obesidad_pais.png")
MOSAIC_SOB_PAIS = os.path.join(OUTDIR_SOB, "posterior_prevalencia_sobrepeso_pais.png")
GEOJSON_PROVINCES = "../data/geo/geoBoundaries-CRI-ADM1_simplified.geojson"
GEOJSON_CANTONES = "../data/geo/Cantones_de_Costa_Rica.geojson"
CANTON_CODES_JSON = "../data/geo/CodeSystem-cantones-cs.json"
SUMMARY_CSV = "../res/csv/summary_prevalence_by_province.csv"
SUMMARY_CSV_CANTON = "../res/csv/summary_prevalence_by_canton.csv"
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

    for feat in gj.get("features", []):
        name_raw = str(feat.get("properties", {}).get(prop_key, "")).strip()
        # muchos geoBoundaries traen "Provincia Heredia": quitamos prefijo
        name_raw = re.sub(r"^\s*Provincia\s+", "", name_raw, flags=re.I)
        name_clean = _sanitize_prov(name_raw)
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
# Figuras Plotly
# ==========================


def make_map(df_summary: pd.DataFrame, metric: str = "ob_mean") -> go.Figure:
    import plotly.express as px
    import plotly.graph_objects as go
    import numpy as np

    assert metric in {"ob_mean", "sb_mean"}

    lo_col = "ob_q2.5" if metric == "ob_mean" else "sb_q2.5"
    hi_col = "ob_q97.5" if metric == "ob_mean" else "sb_q97.5"

    dfp = df_summary[df_summary["Province"].astype(str) != "PAIS"].copy()
    dfp["_prov_clean"] = dfp["Province"].astype(str).apply(_sanitize_prov)

    dfp["__mean"] = dfp[metric].astype(float)
    dfp["__lo"] = dfp[lo_col].astype(float)
    dfp["__hi"] = dfp[hi_col].astype(float)

    gj, fid_key = _load_province_geojson(GEOJSON_PROVINCES)

    if gj is not None and fid_key is not None:
        fig = px.choropleth_mapbox(
            dfp,
            geojson=gj,
            locations="_prov_clean",
            featureidkey="id",
            color="__mean",
            custom_data=["__mean", "__lo", "__hi"],
            center={"lat": CR_LATITUDE, "lon": CR_LONGITUDE},
            mapbox_style=MAPBOX_STYLE,
            zoom=7.2,  # mostrar CR
            opacity=0.78,
            color_continuous_scale="Viridis",
        )

        # hover
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

    vals = dfp["__mean"].values
    vmin, vmax = float(np.nanmin(vals)), float(np.nanmax(vals))

    fig = go.Figure(
        go.Scattermapbox(
            lat=dfp["lat"],
            lon=dfp["lon"],
            text=dfp["Province"],
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


def make_map_canton(df_canton: pd.DataFrame, metric: str = "ob_mean") -> go.Figure:
    import plotly.express as px
    import plotly.graph_objects as go
    import numpy as np

    assert metric in {"ob_mean", "sb_mean"}

    lo_col = "ob_q2.5" if metric == "ob_mean" else "sb_q2.5"
    hi_col = "ob_q97.5" if metric == "ob_mean" else "sb_q97.5"

    dfc = df_canton.copy()

    # columnas numéricas
    dfc["__mean"] = dfc[metric].astype(float)
    dfc["__lo"] = dfc[lo_col].astype(float)
    dfc["__hi"] = dfc[hi_col].astype(float)

    # nos aseguramos de tener el nombre limpio del cantón
    if "_canton_clean" not in dfc.columns:
        dfc["_canton_clean"] = dfc["Canton"].astype(str).apply(_sanitize_prov)

    canton_names = dfc["_canton_clean"].unique().tolist()

    # Intento 1: choropleth por polígonos de cantón
    gj, fid_key = _load_canton_geojson(GEOJSON_CANTONES, canton_names)

    if gj is not None and fid_key is not None:
        fig = px.choropleth_mapbox(
            dfc,
            geojson=gj,
            locations="_canton_clean",  # empata con feat["id"]
            featureidkey="id",
            color="__mean",
            custom_data=["__mean", "__lo", "__hi"],
            center={"lat": CR_LATITUDE, "lon": CR_LONGITUDE},
            mapbox_style=MAPBOX_STYLE,
            zoom=8.0,
            opacity=0.80,
            color_continuous_scale="Viridis",
        )

        fig.update_traces(
            hovertext=dfc["Canton_display"],
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

        return fig

    # Intento 2 (fallback): puntos por cantón usando lat/lon
    if ("lat" not in dfc.columns) or ("lon" not in dfc.columns):
        raise ValueError(
            "El mapa por cantón no pudo usar el GeoJSON y el CSV no tiene "
            "columnas 'lat' y 'lon'.\n"
            "Solución rápida: agrega 'lat' y 'lon' al CSV de cantones, o revisa "
            "que GEOJSON_CANTONES apunte al archivo correcto."
        )

    vals = dfc["__mean"].values
    vmin, vmax = float(np.nanmin(vals)), float(np.nanmax(vals))

    fig = go.Figure(
        go.Scattermapbox(
            lat=dfc["lat"],
            lon=dfc["lon"],
            text=dfc["Canton_display"],
            mode="markers",
            marker=dict(
                size=12,
                color=dfc["__mean"],
                colorscale="Viridis",
                cmin=vmin,
                cmax=vmax,
                showscale=True,
                colorbar=dict(title="media"),
                opacity=0.9,
            ),
            customdata=np.column_stack([dfc["__mean"], dfc["__lo"], dfc["__hi"]]),
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Media: %{customdata[0]:.4f}<br>"
                "IC95%: [%{customdata[1]:.4f}, %{customdata[2]:.4f}]"
                "<extra></extra>"
            ),
            name="Cantón",
        )
    )

    fig.update_layout(
        mapbox=dict(
            style=MAPBOX_STYLE,
            center=dict(lat=CR_LATITUDE, lon=CR_LONGITUDE),
            zoom=8.0,
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=600,
    )
    return fig


def make_forest(df_summary: pd.DataFrame, metric: str = "ob"):
    import plotly.graph_objects as go
    import numpy as np
    import pandas as pd

    if metric == "ob":
        mean_col, lo_col, hi_col, title = "ob_mean", "ob_q2.5", "ob_q97.5", "Obesidad"
    else:
        mean_col, lo_col, hi_col, title = "sb_mean", "sb_q2.5", "sb_q97.5", "Sobrepeso"

    dfp = df_summary[df_summary["Province"].astype(str) != "PAIS"].copy()
    dfp = dfp.sort_values(mean_col, ascending=False)

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
            showlegend=False,
        )
    )

    if "PAIS" in df_summary["Province"].values:
        pais_row = df_summary.loc[df_summary["Province"] == "PAIS"].iloc[0]
        pais_val = float(pais_row[mean_col])
        pais_lo = float(pais_row[lo_col])
        pais_hi = float(pais_row[hi_col])

        line_opacity = 0.6
        line_color = "#111827"

        fig.add_vline(
            x=pais_val,
            line_dash="dot",
            line_width=1.5,
            opacity=line_opacity,
            line_color=line_color,
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
        showlegend=False,
    )

    fig.update_yaxes(categoryorder="array", categoryarray=y_order, automargin=True)
    fig.update_xaxes(autorange=True)

    return fig


# ==========================
# Preparación y DataFrame resumen
# ==========================
def get_summary_df() -> pd.DataFrame:
    """
    Lee SUMMARY_CSV y lo valida. Provincias.
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
        df["_prov_clean"] = df["Province"].astype(str).apply(_sanitize_prov)

        df["lat"] = df["_prov_clean"].map(
            lambda k: PROV_POINTS.get(k, (np.nan, np.nan))[0]
        )
        df["lon"] = df["_prov_clean"].map(
            lambda k: PROV_POINTS.get(k, (np.nan, np.nan))[1]
        )

        mask_pais = df["_prov_clean"] == "PAIS"
        if mask_pais.any():
            df.loc[mask_pais, "lat"] = CR_LATITUDE
            df.loc[mask_pais, "lon"] = CR_LONGITUDE

        df.drop(columns=["_prov_clean"], inplace=True)

        if df["lat"].isna().any() or df["lon"].isna().any():
            faltantes = df.loc[df["lat"].isna() | df["lon"].isna(), "Province"].tolist()
            raise ValueError(
                "Faltan coordenadas para: "
                + ", ".join(faltantes)
                + ". Revisa PROV_POINTS o los nombres en el CSV."
            )

    try:
        order = [p for p in PROVINCE_ORDER if p in set(df["Province"])]
        if "PAIS" in set(df["Province"]):
            order += ["PAIS"]
        df = df.set_index("Province").loc[order].reset_index()
    except Exception:
        pass

    return df


SUMMARY_DF = get_summary_df()


def _load_canton_codes(path: str):
    """
    Lee el CodeSystem de cantones FHIR y devuelve un dict:
    clave = nombre sanitizado (MAYÚSCULAS sin tildes)
    valor = nombre oficial con tildes (display).
    """
    import json

    if not os.path.isfile(path):
        return {}

    with open(path, "r", encoding="utf-8") as f:
        cs = json.load(f)

    concepts = cs.get("concept", [])
    name_map = {}
    for c in concepts:
        disp = c.get("display", "").strip()
        if not disp:
            continue
        clean = _sanitize_prov(disp)
        name_map[clean] = disp
    return name_map


def _load_canton_geojson(path: str, canton_names: List[str]):
    """
    Carga un GeoJSON de cantones y elige automáticamente la columna de
    'properties' que mejor calza con los nombres de cantón (_canton_clean).

    - canton_names: lista de nombres ya sanitizados (MAYÚSCULAS sin tildes).
    Devuelve (geojson_mod, "id") o (None, None) si no se pudo usar.
    """
    import json

    if not os.path.isfile(path):
        return None, None

    with open(path, "r", encoding="utf-8") as f:
        gj = json.load(f)

    features = gj.get("features", [])
    if not features:
        return None, None

    # claves de propiedades que son cadenas
    sample_props = features[0].get("properties", {})
    candidate_keys = [k for k, v in sample_props.items() if isinstance(v, str)]
    if not candidate_keys:
        return None, None

    target_set = set(canton_names)
    best_key = None
    best_score = -1

    # buscamos la propiedad cuyo conjunto de nombres (sanitizados)
    # tenga mayor intersección con los nombres del CSV
    for key in candidate_keys:
        names_for_key = set()
        for feat in features:
            val = str(feat.get("properties", {}).get(key, "")).strip()
            if not val:
                continue
            names_for_key.add(_sanitize_prov(val))

        score = len(names_for_key & target_set)
        if score > best_score:
            best_score = score
            best_key = key

    if best_key is None or best_score <= 0:
        # no encontramos una columna que calce con los cantones del CSV
        return None, None

    # fijamos 'id' usando esa columna
    for feat in features:
        val = str(feat.get("properties", {}).get(best_key, "")).strip()
        feat["id"] = _sanitize_prov(val)

    return gj, "id"


def get_summary_canton_df() -> pd.DataFrame:
    """
    Lee SUMMARY_CSV_CANTON (resumen por cantón) y agrega:
    - _canton_clean: nombre sanitizado tipo SAN JOSE
    - Canton_display: nombre oficial con tildes (San José, Escazú, etc.)
    """
    if not os.path.isfile(SUMMARY_CSV_CANTON):
        raise FileNotFoundError(
            f"No se encontró el CSV requerido: {SUMMARY_CSV_CANTON}. "
            "Genera el archivo de resumen por cantón antes de lanzar el dashboard."
        )

    df = pd.read_csv(SUMMARY_CSV_CANTON)

    required_cols = {
        "Canton",
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
            "El CSV de cantones no tiene las columnas necesarias: "
            + ", ".join(sorted(missing))
        )

    # nombre "limpio" para empatar con geojson y con el CodeSystem
    df["_canton_clean"] = df["Canton"].astype(str).apply(_sanitize_prov)

    # nombres oficiales con tildes desde el CodeSystem
    name_map = _load_canton_codes(CANTON_CODES_JSON)
    df["Canton_display"] = df["_canton_clean"].map(name_map)

    # fallback: si algún cantón no está en el CodeSystem, usa title case
    df["Canton_display"] = df["Canton_display"].fillna(
        df["Canton"].astype(str).str.title()
    )

    return df


SUMMARY_DF = get_summary_df()
SUMMARY_CANTON_DF = get_summary_canton_df()


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
                                    html.Span(" | "),
                                    html.Label("Nivel:"),
                                    dcc.RadioItems(
                                        id="map-level-radio",
                                        options=[
                                            {
                                                "label": "Provincia",
                                                "value": "provincia",
                                            },
                                            {"label": "Cantón", "value": "canton"},
                                        ],
                                        value="provincia",
                                        inline=True,
                                    ),
                                ],
                                style={
                                    "display": "flex",
                                    "flexWrap": "wrap",
                                    "gap": "12px",
                                    "alignItems": "center",
                                    "marginBottom": 8,
                                },
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
@app.callback(
    Output("map-graph", "figure"),
    Input("metric-radio", "value"),
    Input("map-level-radio", "value"),
)
def update_map(metric_value, level):
    if level == "canton":
        return make_map_canton(SUMMARY_CANTON_DF, metric=metric_value)
    # por defecto, provincia
    return make_map(SUMMARY_DF, metric=metric_value)


@app.callback(
    Output("dens-img", "src"),
    Output("dens-img", "style"),
    Input("dens-cond-radio", "value"),
    Input("dens-scope-tabs", "value"),
)
def update_density_image(condicion, ambito):
    path = density_image_path(condicion, ambito)

    if not os.path.isfile(path):
        return "", {"display": "none"}

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
    app.run(host="127.0.0.1", port=8050, debug=True)
