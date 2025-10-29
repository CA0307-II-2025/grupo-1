# -*- coding: utf-8 -*-
"""
Dashboard (Dash) que usa **el mismo método del script `modelo_jerarquico.py`** para:
- Ejecutar/leer el modelo jerárquico (obesidad y sobrepeso) por **provincia**.
- Generar **mosaicos** (una sola imagen por condición con todas las provincias + país).
- Construir un **mapa interactivo** (hover muestra media e IC95% de obesidad y sobrepeso).
- Añadir un **forest plot** comparando provincias.

Rutas esperadas (como en `modelo_jerarquico.py`):
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
# (El archivo `modelo_jerarquico.py` debe estar en el mismo directorio o en PYTHONPATH)
import importlib
mj = importlib.import_module("modelo_jerarquico")  # run_with_csv, save_posterior_prevalence_figs, _weighted_draws, etc.

# ==========================
# Parámetros y constantes
# ==========================
CR_LATITUDE = 9.7489
CR_LONGITUDE = -83.7534
CR_ZOOM = 7
MAPBOX_STYLE = "carto-positron"

PROVINCE_ORDER = [
    "SAN JOSE", "ALAJUELA", "CARTAGO", "HEREDIA", "GUANACASTE", "PUNTARENAS", "LIMON"
]

# Cabeceras provinciales (aprox.)
PROV_POINTS = {
    "SAN JOSE":   (9.9281,  -84.0907),
    "ALAJUELA":   (10.0163, -84.2116),
    "CARTAGO":    (9.8644,  -83.9194),
    "HEREDIA":    (9.9981,  -84.1165),
    "GUANACASTE": (10.6320, -85.4377),
    "PUNTARENAS": (9.9763,  -84.8384),
    "LIMON":      (9.9830,  -83.0330),
}

DATA_CSV = "../data/clean/datos_limpios.csv"
OUTDIR_OB = "../res/graficos/graficos_simulados/obesidad"
OUTDIR_SOB = "../res/graficos/graficos_simulados/sobrepeso"
MOSAIC_OB = os.path.join(OUTDIR_OB, "posterior_prevalencia_obesidad_grid.png")
MOSAIC_SOB = os.path.join(OUTDIR_SOB, "posterior_prevalencia_sobrepeso_grid.png")

# ==========================
# Utilidades
# ==========================

def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def _sanitize_prov(s: str) -> str:
    # Uppercase sin tildes principales para empatar con nombres de archivos
    rep = (
        ("á", "A"), ("é", "E"), ("í", "I"), ("ó", "O"), ("ú", "U"),
        ("Á", "A"), ("É", "E"), ("Í", "I"), ("Ó", "O"), ("Ú", "U"),
        ("ï", "I"), ("ö", "O"), ("ñ", "N"), ("Ñ", "N"),
    )
    t = s.upper()
    for a, b in rep: t = t.replace(a, b)
    return t


def _posterior_draws_by_province(trace, meta) -> Dict[str, np.ndarray]:
    """Devuelve draws ponderados por provincia usando el mismo método del script original."""
    p = trace.posterior["p"].values  # (chains, draws, N)
    S = p.shape[0] * p.shape[1]
    p2d = p.reshape(S, p.shape[2])    # (S, N)
    dfm = meta["df"]
    provincias = dfm["provincia"].astype(str).apply(_sanitize_prov).to_numpy()
    n_i = dfm["total"].to_numpy(float)

    draws_by_prov: Dict[str, np.ndarray] = {}
    for prov in PROVINCE_ORDER:
        mask = provincias == prov
        if not np.any(mask):
            continue
        # Agregación ponderada por 'total' usando la función original
        p_prov = mj._weighted_draws(p2d[:, mask], n_i[mask])
        draws_by_prov[prov] = p_prov
    return draws_by_prov


def _posterior_country_draws(trace, meta) -> np.ndarray:
    p = trace.posterior["p"].values
    S = p.shape[0] * p.shape[1]
    p2d = p.reshape(S, p.shape[2])
    n_i = meta["df"]["total"].to_numpy(float)
    return mj._weighted_draws(p2d, n_i)


def _summarize(draws: np.ndarray) -> Tuple[float, float, float, float]:
    mean = float(draws.mean())
    q2, q50, q97 = [float(x) for x in np.quantile(draws, [0.025, 0.5, 0.975])]
    return mean, q2, q50, q97


def _compose_mosaic(image_paths: List[str], outpath: str, cols: int = 4, pad: int = 10, bg=(255, 255, 255)):
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
    x = pad; y = pad
    for i, im in enumerate(resized):
        canvas.paste(im, (x, y))
        x += max_w + pad
        if (i + 1) % cols == 0:
            x = pad
            y += h + pad
    _ensure_dir(os.path.dirname(outpath))
    canvas.save(outpath)


# ==========================
# Preparación de resultados (correr modelo si faltan mosaicos)
# ==========================

def prepare_results_if_needed():
    need_run = not (os.path.isfile(MOSAIC_OB) and os.path.isfile(MOSAIC_SOB))

    if need_run:
        # Muestreo idéntico al script
        trace_ob, resumen_ob, meta_ob = mj.run_with_csv(
            csv_path=DATA_CSV,
            condicion="obesidad",
            provincia_col="provincia",
            distrito_col="distrito",
            vars_dem=(
                "desempleo", "poblacion_urbana", "privacion_critica",
                "poblacion_menor_14", "hogares_monomarentales",
                "ocupantes_por_hogar", "anos_escolaridad",
            ),
            incluye_provincia=True,
            draws=2000,
            tune=1000,
            chains=4,
            cores=4,
            seed=2025,
        )
        trace_sob, resumen_sob, meta_sob = mj.run_with_csv(
            csv_path=DATA_CSV,
            condicion="sobrepeso",
            provincia_col="provincia",
            distrito_col="distrito",
            vars_dem=(
                "desempleo", "poblacion_urbana", "privacion_critica",
                "poblacion_menor_14", "hogares_monomarentales",
                "ocupantes_por_hogar", "anos_escolaridad",
            ),
            incluye_provincia=True,
            draws=2000,
            tune=1000,
            chains=4,
            cores=4,
            seed=2025,
        )
        # Figuras por provincia (archivo por provincia) + país
        mj.save_posterior_prevalence_figs(
            trace_ob, meta_ob, condicion_label="obesidad", outdir=OUTDIR_OB,
            province_order=PROVINCE_ORDER, bins=60,
        )
        mj.save_posterior_prevalence_figs(
            trace_sob, meta_sob, condicion_label="sobrepeso", outdir=OUTDIR_SOB,
            province_order=PROVINCE_ORDER, bins=60,
        )

        # Crear mosaicos: país + 7 provincias = 8 paneles (orden dado)
        def paths_for(cond: str, outdir: str):
            paths = [
                os.path.join(outdir, f"posterior_prevalencia_{cond}_pais.png")
            ]
            paths += [
                os.path.join(outdir, f"posterior_prevalencia_{cond}_{prov}.png")
                for prov in PROVINCE_ORDER
            ]
            return paths

        _compose_mosaic(paths_for("obesidad", OUTDIR_OB), MOSAIC_OB)
        _compose_mosaic(paths_for("sobrepeso", OUTDIR_SOB), MOSAIC_SOB)

        return (trace_ob, meta_ob), (trace_sob, meta_sob)

    else:
        # Si ya existen mosaicos, aún necesitamos los resúmenes para el mapa.
        # Los generamos corriendo el modelo rápidamente (mismos parámetros).
        # (Si en tu entorno querés evitar re-muestrear, podrías leer un CSV precomputado en su lugar.)
        trace_ob, _, meta_ob = mj.run_with_csv(
            csv_path=DATA_CSV, condicion="obesidad", provincia_col="provincia",
            distrito_col="distrito",
            vars_dem=(
                "desempleo", "poblacion_urbana", "privacion_critica",
                "poblacion_menor_14", "hogares_monomarentales",
                "ocupantes_por_hogar", "anos_escolaridad",
            ),
            incluye_provincia=True, draws=2000, tune=1000, chains=4, cores=4, seed=2025,
        )
        trace_sob, _, meta_sob = mj.run_with_csv(
            csv_path=DATA_CSV, condicion="sobrepeso", provincia_col="provincia",
            distrito_col="distrito",
            vars_dem=(
                "desempleo", "poblacion_urbana", "privacion_critica",
                "poblacion_menor_14", "hogares_monomarentales",
                "ocupantes_por_hogar", "anos_escolaridad",
            ),
            incluye_provincia=True, draws=2000, tune=1000, chains=4, cores=4, seed=2025,
        )
        return (trace_ob, meta_ob), (trace_sob, meta_sob)


# ==========================
# Construcción de resúmenes para el mapa y forest plot
# ==========================

def build_summary_df(trace_ob, meta_ob, trace_sob, meta_sob) -> pd.DataFrame:
    ob_by_prov = _posterior_draws_by_province(trace_ob, meta_ob)
    sob_by_prov = _posterior_draws_by_province(trace_sob, meta_sob)

    rows = []
    for prov in PROVINCE_ORDER:
        if prov not in ob_by_prov or prov not in sob_by_prov:
            continue
        obm, ob2, ob50, ob97 = _summarize(ob_by_prov[prov])
        sbm, sb2, sb50, sb97 = _summarize(sob_by_prov[prov])
        lat, lon = PROV_POINTS[prov]
        rows.append({
            "Province": prov,
            "lat": lat,
            "lon": lon,
            "ob_mean": obm, "ob_q2.5": ob2, "ob_q50": ob50, "ob_q97.5": ob97,
            "sb_mean": sbm, "sb_q2.5": sb2, "sb_q50": sb50, "sb_q97.5": sb97,
        })

    # Agregar país (para leyenda / forest opcional)
    ob_country = _posterior_country_draws(trace_ob, meta_ob)
    sb_country = _posterior_country_draws(trace_sob, meta_sob)
    cobm, cob2, cob50, cob97 = _summarize(ob_country)
    csbm, csb2, csb50, csb97 = _summarize(sb_country)

    df = pd.DataFrame(rows)
    total_row = {
        "Province": "PAIS",
        "lat": CR_LATITUDE,
        "lon": CR_LONGITUDE,
        "ob_mean": cobm, "ob_q2.5": cob2, "ob_q50": cob50, "ob_q97.5": cob97,
        "sb_mean": csbm, "sb_q2.5": csb2, "sb_q50": csb50, "sb_q97.5": csb97,
    }
    df_total = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)
    return df_total


# ==========================
# Figuras Plotly
# ==========================

def make_map(df_summary: pd.DataFrame, metric: str = "ob_mean") -> go.Figure:
    assert metric in {"ob_mean", "sb_mean"}
    vals = df_summary[df_summary["Province"] != "PAIS"][metric].astype(float)
    vmin, vmax = float(vals.min()), float(vals.max())

    hovertext = (
        "<b>%{customdata[0]}</b><br>"
        "Obesidad: %{customdata[1]:.3f} (IC95% [%{customdata[2]:.3f}, %{customdata[3]:.3f}])<br>"
        "Sobrepeso: %{customdata[4]:.3f} (IC95% [%{customdata[5]:.3f}, %{customdata[6]:.3f}])<extra></extra>"
    )

    # Customdata: [prov, ob_mean, ob_q2.5, ob_q97.5, sb_mean, sb_q2.5, sb_q97.5]
    cd = np.stack([
        df_summary["Province"].values,
        df_summary["ob_mean"].values,
        df_summary["ob_q2.5"].values,
        df_summary["ob_q97.5"].values,
        df_summary["sb_mean"].values,
        df_summary["sb_q2.5"].values,
        df_summary["sb_q97.5"].values,
    ], axis=-1)

    fig = go.Figure(
        go.Scattermapbox(
            lat=df_summary["lat"],
            lon=df_summary["lon"],
            text=df_summary["Province"],
            customdata=cd,
            mode="markers",
            marker=dict(
                size=20,
                color=df_summary[metric],
                colorscale="Viridis",
                cmin=vmin,
                cmax=vmax,
                showscale=True,
                colorbar=dict(title=("Obesidad" if metric == "ob_mean" else "Sobrepeso") + " (media)"),
            ),
            hovertemplate=hovertext,
        )
    )

    fig.update_layout(
        mapbox_style=MAPBOX_STYLE,
        mapbox_zoom=CR_ZOOM,
        mapbox_center=dict(lat=CR_LATITUDE, lon=CR_LONGITUDE),
        margin=dict(r=0, t=0, l=0, b=0),
        height=600,
    )
    return fig


def make_forest(df_summary: pd.DataFrame, metric: str = "ob") -> go.Figure:
    # metric: "ob" (obesidad) o "sb" (sobrepeso)
    assert metric in {"ob", "sb"}
    base = df_summary[df_summary["Province"] != "PAIS"].copy()
    base = base.set_index("Province").loc[PROVINCE_ORDER].reset_index()
    y = base["Province"].tolist()

    m = base[f"{metric}_mean"].to_numpy()
    lo = base[f"{metric}_q2.5"].to_numpy()
    hi = base[f"{metric}_q97.5"].to_numpy()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=m, y=y, mode="markers", name=("Obesidad" if metric == "ob" else "Sobrepeso"),
            error_x=dict(type="data", symmetric=False, array=hi - m, arrayminus=m - lo),
        )
    )
    fig.update_layout(
        title=("Forest plot: " + ("Obesidad" if metric == "ob" else "Sobrepeso")),
        xaxis_title="Prevalencia (media e IC95%)",
        yaxis_title="Provincia",
        height=420,
        margin=dict(l=80, r=40, t=50, b=40),
    )
    return fig


# ==========================
# Preparación (correr/leer) y DataFrame resumen
# ==========================
(trace_ob, meta_ob), (trace_sob, meta_sob) = prepare_results_if_needed()
SUMMARY_DF = build_summary_df(trace_ob, meta_ob, trace_sob, meta_sob)


# ==========================
# App Dash
# ==========================
app = dash.Dash(__name__)
app.title = "Obesidad y Sobrepeso – Costa Rica"

app.layout = html.Div(
    [
        html.H1("Dashboard – Costa Rica: Obesidad y Sobrepeso", style={"marginBottom": 6}),
        dcc.Tabs(
            id="tabs",
            value="tab-map",
            children=[
                dcc.Tab(label="Mapa interactivo", value="tab-map"),
                dcc.Tab(label="Mosaicos por provincia", value="tab-mosaic"),
                dcc.Tab(label="Forest plot", value="tab-forest"),
            ],
        ),
        html.Div(id="tabs-content", style={"padding": "12px 0"}),
    ],
    style={"maxWidth": 1280, "margin": "0 auto", "padding": "12px"},
)


@app.callback(Output("tabs-content", "children"), Input("tabs", "value"))
def render_tab(tab):
    if tab == "tab-map":
        return html.Div([
            html.Div([
                html.Label("Métrica para colorear:"),
                dcc.RadioItems(
                    id="metric-radio",
                    options=[
                        {"label": "Obesidad (media)", "value": "ob_mean"},
                        {"label": "Sobrepeso (media)", "value": "sb_mean"},
                    ],
                    value="ob_mean",
                    inline=True,
                ),
            ]),
            dcc.Graph(id="map-graph", figure=make_map(SUMMARY_DF, metric="ob_mean")),
        ])

    if tab == "tab-mosaic":
        return html.Div([
            html.Div([
                html.Label("Mosaico"),
                dcc.RadioItems(
                    id="mosaic-radio",
                    options=[
                        {"label": "Obesidad", "value": MOSAIC_OB},
                        {"label": "Sobrepeso", "value": MOSAIC_SOB},
                    ],
                    value=MOSAIC_OB,
                    inline=True,
                ),
            ], style={"marginBottom": 8}),
            html.Img(id="mosaic-img", src="/assets/mosaic-placeholder.png", style={"display": "none"}),
            dcc.Graph(id="mosaic-graph"),
        ])

    if tab == "tab-forest":
        return html.Div([
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
            dcc.Graph(id="forest-graph", figure=make_forest(SUMMARY_DF, metric="ob")),
        ])

    return html.Div()


# === Callbacks dinámicos ===
@app.callback(Output("map-graph", "figure"), Input("metric-radio", "value"))
def update_map(metric_value):
    return make_map(SUMMARY_DF, metric=metric_value)


@app.callback(Output("mosaic-graph", "figure"), Input("mosaic-radio", "value"))
def update_mosaic(mosaic_path):
    # Mostrar la imagen como figura Plotly para zoom fácil
    import plotly.express as px
    if not os.path.isfile(mosaic_path):
        fig = go.Figure()
        fig.update_layout(title="No se encontró el mosaico. Revisa las rutas de salida.")
        return fig
    img = Image.open(mosaic_path)
    fig = px.imshow(img)
    fig.update_xaxes(showticklabels=False).update_yaxes(showticklabels=False)
    fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), title=mosaic_path)
    return fig


@app.callback(Output("forest-graph", "figure"), Input("forest-radio", "value"))
def update_forest(metric_value):
    return make_forest(SUMMARY_DF, metric=metric_value)


# Servidor
if __name__ == "__main__":
    # Dash
    app.run(host="0.0.0.0", port=8050, debug=True)
