import pandas as pd
import numpy as np
import pymc as pm
import arviz as az
import os
import matplotlib.pyplot as plt

try:
    from scipy.stats import gaussian_kde

    _HAS_SCIPY = True
except Exception:
    _HAS_SCIPY = False


SUMMARY_PROVINCE_CSV = "../../res/csv/summary_prevalence_by_province.csv"
SUMMARY_CANTON_CSV = "../../res/csv/summary_prevalence_by_canton.csv"


# ---------------------------
# Utilidades
# ---------------------------
def standardize_cols(df, cols):
    """Devuelve X estandarizada y medias/sds para referencia.
    Función para normalizar los valores de las variables sociodemográficas
    """
    X = df[cols].astype(float).to_numpy()
    mu = X.mean(axis=0)
    sd = X.std(axis=0, ddof=1)
    sd[sd == 0] = 1.0
    Xz = (X - mu) / sd
    return Xz, mu, sd


def prep_data(
    df,
    condicion="obesidad",
    region_col="provincia",
    distrito_col="distrito",
    vars_dem=None,
):
    """
    Filtra y prepara y, n, Xz y los índices de la región (provincia o cantón).
    region_col puede ser 'provincia', 'canton', o cualquier variable categórica.
    """

    if vars_dem is None:
        vars_dem = [
            "desempleo",
            "poblacion_urbana",
            "privacion_critica",
            "poblacion_menor_14",
            "hogares_monomarentales",
            "ocupantes_por_hogar",
            "anos_escolaridad",
        ]

    dfc = df.loc[df["condicion"] == condicion].copy()

    dfc["total"] = dfc["total"].astype(int)
    dfc["subtotal"] = dfc["subtotal"].astype(int)
    dfc = dfc[dfc["total"] > 0].copy()

    y = dfc["subtotal"].to_numpy()
    n = dfc["total"].to_numpy()

    use_covs = [c for c in vars_dem if c in dfc.columns]
    Xz = None
    if len(use_covs) > 0:
        Xz, mu, sd = standardize_cols(dfc, use_covs)
    else:
        mu = sd = None

    # Crear índices de la región (provincia o cantón)
    if region_col not in dfc.columns:
        raise ValueError(f"No se encontró la columna '{region_col}' en el dataframe.")

    region_codes, region_id = np.unique(
        dfc[region_col].astype(str).values, return_inverse=True
    )
    J = len(region_codes)

    meta = {
        "distrito": dfc[distrito_col].astype(str).values
        if distrito_col in dfc.columns
        else np.arange(len(dfc)),
        "region": dfc[region_col].astype(str).values,  # <-- ahora genérico
        "region_codes": region_codes,
        "region_id": region_id,
        "use_covs": use_covs,
        "X_mu": mu,
        "X_sd": sd,
        "df": dfc.reset_index(drop=True),
    }

    return y, n, Xz, region_id, J, meta


# ---------------------------
# Modelo PyMC
# ---------------------------
def fit_model_binomial_logit(
    y,
    n,
    Xz=None,
    region_id=None,  # <-- antes prov_id
    J=None,
    incluye_region=True,  # <-- antes incluye_provincia
    draws=2000,
    tune=1000,
    target_accept=0.9,
    chains=4,
    cores=4,
    random_seed=42,
):
    """
    Igual que antes, pero con región genérica.
    """

    with pm.Model() as model:
        alpha = pm.Normal("alpha", mu=0, sigma=5)

        if Xz is not None:
            K = Xz.shape[1]
            beta = pm.Normal("beta", mu=0, sigma=5, shape=K)
            lin = alpha + pm.math.dot(Xz, beta)
        else:
            beta = None
            lin = alpha

        if incluye_region:
            if region_id is None or J is None:
                raise ValueError("Debe pasar region_id y J si incluye_region=True")

            sigma_u = pm.HalfNormal("sigma_u", sigma=2)
            u = pm.Normal("u", mu=0, sigma=sigma_u, shape=J)
            lin = lin + u[region_id]
        else:
            sigma_u = None
            u = None

        p = pm.Deterministic("p", pm.math.sigmoid(lin))

        pm.Binomial("y_obs", n=n, p=p, observed=y)

        trace = pm.sample(
            draws=draws,
            tune=tune,
            target_accept=target_accept,
            chains=chains,
            cores=cores,
            random_seed=random_seed,
        )

    return model, trace


def posterior_summary_by_row(trace, meta, var_name="p", q=(0.025, 0.5, 0.975)):
    """
    Devuelve un DataFrame con la media e IC para la probabilidad p por fila (distrito).
    """
    p_draws = (
        trace.posterior[var_name].stack(sample=("chain", "draw")).values
    )  # shape: [N, S]
    mean = p_draws.mean(axis=1)
    qlo, qmd, qhi = np.quantile(p_draws, q, axis=1)

    out = meta["df"].copy()
    out["p_mean"] = mean
    out["p_q2.5"] = qlo
    out["p_q50"] = qmd
    out["p_q97.5"] = qhi
    return out


def region_country_summary(
    trace, meta, condicion_label: str, region_col: str, label_col: str = "Region"
):
    """
    Devuelve un DataFrame con filas: regiones (provincia o cantón) + 'PAIS',
    y columnas de resumen para la condición dada con prefijo:
      ob_* si condicion_label == "obesidad"
      sb_* si condicion_label == "sobrepeso"

    region_col: nombre de la columna de región en meta["df"] (p.ej. 'provincia' o 'canton')
    label_col: nombre de la columna de etiquetas en el resumen (p.ej. 'Province' o 'Canton')
    """
    # Draws de p: (chains, draws, N) -> (S, N)
    p = trace.posterior["p"].values
    chains, draws, N = p.shape
    S = chains * draws
    p2d = p.reshape(S, N)

    dfm = meta["df"]
    if region_col not in dfm.columns:
        raise ValueError(
            f"No se encontró la columna de región '{region_col}' en meta['df']."
        )

    if "total" not in dfm.columns:
        raise ValueError("meta['df'] debe tener la columna 'total'.")

    regiones = dfm[region_col].astype(str).to_numpy()
    n_i = dfm["total"].to_numpy(dtype=float)

    def _summ(draws_1d: np.ndarray):
        mean = draws_1d.mean()
        q2p5, q50, q97p5 = np.quantile(draws_1d, [0.025, 0.5, 0.975])
        return mean, q2p5, q50, q97p5

    # prefijo por condición
    prefix = "ob" if condicion_label.lower().startswith("obes") else "sb"

    rows = []

    # País (ponderado)
    draws_country = _weighted_draws(p2d, n_i)
    m, ql, qm, qh = _summ(draws_country)
    rows.append(
        {
            label_col: "PAIS",
            f"{prefix}_mean": m,
            f"{prefix}_q2.5": ql,
            f"{prefix}_q50": qm,
            f"{prefix}_q97.5": qh,
        }
    )

    # Regiones
    for reg in np.unique(regiones):
        mask = regiones == reg
        if not np.any(mask):
            continue
        draws_reg = _weighted_draws(p2d[:, mask], n_i[mask])
        m, ql, qm, qh = _summ(draws_reg)
        rows.append(
            {
                label_col: str(reg),
                f"{prefix}_mean": m,
                f"{prefix}_q2.5": ql,
                f"{prefix}_q50": qm,
                f"{prefix}_q97.5": qh,
            }
        )

    out = pd.DataFrame(rows)

    # Ordenar alfabéticamente y dejar 'PAIS' al final
    regs = out[label_col].astype(str).tolist()
    others = sorted([r for r in regs if r != "PAIS"])
    order = others + (["PAIS"] if "PAIS" in regs else [])
    out = out.set_index(label_col).loc[order].reset_index()
    return out


def run_with_csv(
    csv_path="../../data/clean/datos_limpios.csv",
    condicion="obesidad",
    region_col="provincia",
    distrito_col="distrito",
    vars_dem=(
        "desempleo",
        "poblacion_urbana",
        "privacion_critica",
        "poblacion_menor_14",
        "hogares_monomarentales",
        "ocupantes_por_hogar",
        "anos_escolaridad",
    ),
    incluye_region=True,
    draws=2000,
    tune=1000,
    chains=4,
    cores=1,
    seed=2025,
):
    df = pd.read_csv(csv_path)

    y, n, Xz, region_id, J, meta = prep_data(
        df,
        condicion=condicion,
        region_col=region_col,
        distrito_col=distrito_col,
        vars_dem=list(vars_dem),
    )

    model, trace = fit_model_binomial_logit(
        y=y,
        n=n,
        Xz=Xz,
        region_id=region_id,
        J=J,
        incluye_region=incluye_region,
        draws=draws,
        tune=tune,
        chains=chains,
        cores=cores,
        random_seed=seed,
    )

    resumen = posterior_summary_by_row(trace, meta, var_name="p")

    return trace, resumen, meta


# ============================
# Utilidades para graficar posteriores de prevalencia
# ============================


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def _weighted_draws(p_draws_2d: np.ndarray, weights_1d: np.ndarray) -> np.ndarray:
    """
    p_draws_2d: (S, N) draws de p por fila (distrito) apilando cadenas.
    weights_1d: (N,) totales n_i por fila.
    return: (S,) draws de la prevalencia agregada ponderada.
    """
    w = np.asarray(weights_1d, dtype=float)
    w = np.where(np.isfinite(w), w, 0.0)
    s = w.sum()
    if s <= 0:
        raise ValueError("Los pesos (n_i) suman 0. Revisa la columna 'total'.")
    return (p_draws_2d @ w) / s


def _plot_posterior_1d(
    draws: np.ndarray,
    title: str,
    xlabel: str,
    outfile: str,
    bins: int = 50,
    kde_factor=1,
):
    """
    Grafica histograma (densidad), línea de densidad suave (si SciPy está disponible),
    media y HDI 95%, y guarda en outfile.
    """
    draws = np.asarray(draws, dtype=float)
    mean = draws.mean()
    hdi_low, hdi_high = az.hdi(draws, hdi_prob=0.95)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    # Histograma (densidad)
    ax.hist(draws, bins=bins, density=True, color="#d9d9d9", edgecolor="none")

    # Curva suave si SciPy está disponible
    if _HAS_SCIPY:
        xs = np.linspace(draws.min(), draws.max(), 400)
        kde = gaussian_kde(draws, bw_method=lambda s: s.scotts_factor() * kde_factor)
        ax.plot(xs, kde(xs), color="#345beb", lw=2.5)

    # Media e intervalo
    ax.axvline(mean, color="#0b1d59", lw=3)
    ax.axvline(hdi_low, color="#cc0033", lw=2, ls="--")
    ax.axvline(hdi_high, color="#cc0033", lw=2, ls="--")

    ax.set_title(title, fontsize=16, pad=12)
    ax.set_xlabel(xlabel, fontsize=14)
    ax.set_ylabel("Densidad posterior", fontsize=12)

    # leyenda
    txtL = f"Media = {mean:.5f}"
    txtR = f"IC 95.0% =\n[{hdi_low:.5f}, {hdi_high:.5f}]"
    ax.text(
        0.02,
        -0.25,
        txtL,
        transform=ax.transAxes,
        color="#0b1d59",
        fontsize=14,
        weight="bold",
    )
    ax.text(
        0.68,
        -0.25,
        txtR,
        transform=ax.transAxes,
        color="#cc0033",
        fontsize=14,
        weight="bold",
    )

    plt.tight_layout()
    _ensure_dir(os.path.dirname(outfile))
    plt.savefig(outfile, dpi=220, bbox_inches="tight")
    plt.close(fig)


def save_posterior_prevalence_figs(
    trace,
    meta,
    condicion_label: str,
    outdir: str = "res/graficos",
    province_order=None,  # se mantiene el nombre por compatibilidad
    region_col: str = None,
    bins: int = 50,
):
    """
    Genera y guarda:
      - Figura de la prevalencia posterior agregada (país)
      - Figuras de la prevalencia posterior por región (provincia o cantón)

    La columna de región se determina así:
      1) Si se pasa region_col, se usa esa.
      2) Si no, se intenta 'provincia', luego 'canton'.
    Todas ponderadas por 'total' (n_i) y usando los draws de 'p' del trace.
    """
    # Draws de p: (chains, draws, N) -> (S, N)
    p = trace.posterior["p"].values
    chains, draws, N = p.shape
    S = chains * draws
    p2d = p.reshape(S, N)

    dfm = meta["df"]

    # --- Determinar la columna de región ---
    if region_col is None:
        if "provincia" in dfm.columns:
            region_col = "provincia"
        elif "canton" in dfm.columns:
            region_col = "canton"
        else:
            raise ValueError(
                "No se encontró ninguna columna de región. "
                "meta['df'] debe tener al menos 'provincia' o 'canton'."
            )

    if "total" not in dfm.columns:
        raise ValueError("meta['df'] debe tener la columna 'total'.")

    regiones = dfm[region_col].astype(str).to_numpy()
    n_i = dfm["total"].to_numpy(dtype=float)

    # ---- País (ponderado)
    p_country = _weighted_draws(p2d, n_i)
    f_country = os.path.join(
        outdir, f"posterior_prevalencia_{condicion_label}_pais.png"
    )
    _plot_posterior_1d(
        p_country,
        title=f"Distribución posterior de la prevalencia de {condicion_label} (País)",
        xlabel=f"Prevalencia de {condicion_label}",
        outfile=f_country,
        bins=bins,
        kde_factor=2,
    )

    # ---- Regiones (provincia o cantón)
    regs = np.unique(regiones) if province_order is None else np.array(province_order)

    for reg in regs:
        mask = regiones == reg
        if not np.any(mask):
            continue

        p_reg = _weighted_draws(p2d[:, mask], n_i[mask])

        f_reg = os.path.join(
            outdir, f"posterior_prevalencia_{condicion_label}_{reg}.png"
        )
        _plot_posterior_1d(
            p_reg,
            title=(
                f"Distribución posterior de la prevalencia de {condicion_label} – {reg}"
            ),
            xlabel=f"Prevalencia de {condicion_label}",
            outfile=f_reg,
            bins=bins,
            kde_factor=2,
        )


# ============================
# Para la validacion del modelo
# ============================


def evaluar_convergencia(trace):
    """Evalúa métricas de convergencia del muestreo NUTS.

    Parámetros
    ----------
    trace : arviz.InferenceData
        Objeto posterior devuelto por PyMC vía pm.sample().

    Retorna
    -------
    dict:
        Un diccionario con R-hat máximo, ESS efectivo mínimo y número total de draws por cadena.
    """
    resumen = az.summary(trace, round_to=None)
    rhat_max = resumen["r_hat"].max()
    ess_bulk_min = resumen["ess_bulk"].min()
    ess_tail_min = resumen["ess_tail"].min()

    # draws por cadena: inferible desde dims de trace.posterior
    n_chains = trace.posterior.dims["chain"]
    n_draws = trace.posterior.dims["draw"]

    out = {
        "rhat_max": float(rhat_max),
        "ess_bulk_min": float(ess_bulk_min),
        "ess_tail_min": float(ess_tail_min),
        "n_chains": int(n_chains),
        "n_draws_per_chain": int(n_draws),
    }
    return out


def evaluar_error_puntual(trace, meta, var_name="p"):
    """Mide el error promedio entre lo observado y la media posterior esperada por distrito.

    Parámetros
    ----------
    trace : arviz.InferenceData
        Objeto posterior que contiene la variable 'p' (probabilidades p_i).
    meta : dict
        Metadatos devueltos por prep_data. Debe incluir meta["df"] con columnas
        'subtotal' (casos positivos) y 'total' (tamaño muestral).
    var_name : str
        Nombre de la variable posterior con probabilidades (por defecto 'p').

    Retorna
    -------
    dict:
        Métricas tipo RMSE y MAE entre:
        - la proporción observada y
        - la probabilidad posterior esperada (media de p_i).
    """
    dfm = meta["df"].copy()
    y_obs = dfm["subtotal"].to_numpy(dtype=float)
    n_obs = dfm["total"].to_numpy(dtype=float)
    prop_obs = y_obs / n_obs  # proporción observada empírica

    # extraer draws de p (chain, draw, distrito)
    p_draws = trace.posterior[var_name].stack(sample=("chain", "draw")).values  # (N, S)
    p_mean = p_draws.mean(axis=1)  # esperanza posterior E[p_i | data]

    # errores
    diff = p_mean - prop_obs
    mae = np.mean(np.abs(diff))
    rmse = np.sqrt(np.mean(diff**2))

    out = {
        "mae_prop": float(mae),
        "rmse_prop": float(rmse),
    }
    return out


def evaluar_cobertura_predictiva(trace, meta, var_name="p", nivel=0.95, rng_seed=123):
    """Evalúa la calibración del modelo usando la predicción posterior (posterior predictive coverage).

    En lugar de comparar la proporción observada con el intervalo creíble de p_i,
    esta función compara la proporción observada con el rango de resultados que el
    modelo habría podido generar, incorporando el ruido binomial de muestreo.

    Parámetros
    ----------
    trace : arviz.InferenceData
        Objeto posterior que contiene la variable 'p' (probabilidades p_i).
    meta : dict
        Metadatos devueltos por prep_data. Debe incluir meta["df"] con
        'subtotal' (éxitos observados) y 'total' (n_i).
    var_name : str
        Nombre de la variable posterior con las probabilidades p_i (por defecto 'p').
    nivel : float
        Nivel del intervalo de credibilidad predictiva que se va a evaluar (por defecto 0.95).
    rng_seed : int
        Semilla para la simulación aleatoria.

    Retorna
    -------
    dict:
        coverage_level:
            El nivel objetivo del intervalo (por ejemplo 0.95).
        empirical_coverage:
            Proporción de distritos en que la tasa observada cae dentro del
            intervalo predictivo posterior.
        n_distritos:
            Número de distritos evaluados.
    """
    rng = np.random.default_rng(rng_seed)

    dfm = meta["df"].copy()
    y_obs = dfm["subtotal"].to_numpy(dtype=float)
    n_obs = dfm["total"].to_numpy(dtype=float)
    prop_obs = y_obs / n_obs  # proporción empírica observada

    # Extraer draws de p: posterior['p'] tiene dims (chain, draw, distrito)
    # stack -> matriz (N, S) donde S = chain*draw
    p_draws = (
        trace.posterior[var_name].stack(sample=("chain", "draw")).values
    )  # shape (N, S)
    N, S = p_draws.shape

    # Simular y_rep ~ Binomial(n_i, p_draw) para cada distrito i y cada draw s
    # Esto da una matriz (N, S) de conteos simulados
    # Nota: usamos broadcasting sobre n_obs
    y_rep = rng.binomial(n=n_obs[:, None].astype(int), p=p_draws)
    prop_rep = y_rep / n_obs[:, None]  # proporciones simuladas bajo el modelo

    alpha = (1 - nivel) / 2.0
    low = np.quantile(prop_rep, alpha, axis=1)
    high = np.quantile(prop_rep, 1 - alpha, axis=1)

    inside = (prop_obs >= low) & (prop_obs <= high)
    coverage = inside.mean()

    return {
        "coverage_level": float(nivel),
        "empirical_coverage": float(coverage),
        "n_distritos": int(N),
    }


def resumen_diagnostico_modelo(trace, meta, var_name="p"):
    """Genera un resumen integrado de desempeño y diagnóstico del modelo.

    Parámetros
    ----------
    trace : arviz.InferenceData
        Posterior resultante de pm.sample().
    meta : dict
        Metadatos de prep_data.
    var_name : str
        Nombre de la variable de probabilidad posterior por distrito (por defecto 'p').

    Retorna
    -------
    dict:
        Diccionario con:
        - métricas de convergencia MCMC
        - métricas de ajuste predictivo global (WAIC / LOO)
        - métricas de error puntual (MAE / RMSE)
        - calibración de incertidumbre (cobertura posterior)
    """
    conv = evaluar_convergencia(trace)
    err = evaluar_error_puntual(trace, meta, var_name=var_name)
    cov_pred = evaluar_cobertura_predictiva(trace, meta, var_name=var_name)

    out = {
        "convergencia": conv,
        "error_puntual": err,
        "cobertura predictiva": cov_pred,
    }
    return out


# ---------------------------
# Entrypoint seguro para Windows
# ---------------------------
if __name__ == "__main__":
    # modelo no jerarquico - obesidad
    trace_2, resumen_2, meta_2 = run_with_csv(
        csv_path="../../data/clean/datos_limpios.csv",
        condicion="obesidad",
        region_col="provincia",
        distrito_col="distrito",
        vars_dem=(
            "desempleo",
            "privacion_critica",
            "poblacion_menor_14",
            "anos_escolaridad",
        ),
        incluye_region=False,
        draws=2000,
        tune=1000,
        chains=4,
        cores=4,
        seed=2025,
    )

    # modelo no jerarquico - sobrepeso
    trace_2_sob, resumen_2_sob, meta_2_sob = run_with_csv(
        csv_path="../../data/clean/datos_limpios.csv",
        condicion="sobrepeso",
        region_col="provincia",
        distrito_col="distrito",
        vars_dem=(
            "desempleo",
            "poblacion_urbana",
            "privacion_critica",
            "poblacion_menor_14",
        ),
        incluye_region=False,
        draws=2000,
        tune=1000,
        chains=4,
        cores=4,
        seed=2025,
    )

    # modelo por cantones
    # obesidad
    trace_c_ob, resumen_c_ob, meta_c_ob = run_with_csv(
        csv_path="../../data/clean/datos_limpios.csv",
        condicion="obesidad",
        region_col="canton",
        distrito_col="distrito",
        vars_dem=(
            "desempleo",
            "privacion_critica",
            "poblacion_menor_14",
            "anos_escolaridad",
        ),
        incluye_region=False,
        draws=2000,
        tune=1000,
        chains=4,
        cores=4,
        seed=2025,
    )

    # modelo por cantones
    # sobrepeso
    trace_c_sob, resumen_c_sob, meta_c_sob = run_with_csv(
        csv_path="../../data/clean/datos_limpios.csv",
        condicion="sobrepeso",
        region_col="canton",
        distrito_col="distrito",
        vars_dem=(
            "desempleo",
            "poblacion_urbana",
            "privacion_critica",
            "poblacion_menor_14",
        ),
        incluye_region=False,
        draws=2000,
        tune=1000,
        chains=4,
        cores=4,
        seed=2025,
    )

    # ===== guardar gráficos país + provincias =====

    save_posterior_prevalence_figs(
        trace_2,
        meta_2,
        condicion_label="obesidad",
        outdir="../../res/graficos/graficos_simulados_no_jer/obesidad",
        province_order=[
            "SAN JOSE",
            "ALAJUELA",
            "CARTAGO",
            "HEREDIA",
            "GUANACASTE",
            "PUNTARENAS",
            "LIMON",
        ],
        bins=60,
    )
    save_posterior_prevalence_figs(
        trace_2_sob,
        meta_2_sob,
        condicion_label="sobrepeso",
        outdir="../../res/graficos/graficos_simulados_no_jer/sobrepeso",
        province_order=[
            "SAN JOSE",
            "ALAJUELA",
            "CARTAGO",
            "HEREDIA",
            "GUANACASTE",
            "PUNTARENAS",
            "LIMON",
        ],
        bins=60,
    )

    # ===== guardar gráficos cantones =====
    save_posterior_prevalence_figs(
        trace_c_ob,
        meta_c_ob,
        condicion_label="obesidad",
        outdir="../../res/graficos/graficos_simulados_no_jer/cantones/obesidad",
        region_col="canton",
    )

    save_posterior_prevalence_figs(
        trace_c_sob,
        meta_c_sob,
        condicion_label="sobrepeso",
        outdir="../../res/graficos/graficos_simulados_no_jer/cantones/sobrepeso",
        region_col="canton",
    )

    print("Gráficos guardados en res/graficos/graficos_simulados")

    # validacion

    diag_obesidad = resumen_diagnostico_modelo(trace_2, meta_2)
    print(diag_obesidad)

    diag_sobrepeso = resumen_diagnostico_modelo(trace_2_sob, meta_2_sob)
    print(diag_sobrepeso)

    # ============================
    # CSV de resumen por PROVINCIA (igual formato que modelo_provincias)
    # ============================
    df_prov_ob = region_country_summary(
        trace_2,
        meta_2,
        condicion_label="obesidad",
        region_col="provincia",
        label_col="Province",  # misma columna que en summary_prevalence_by_province.csv
    )
    df_prov_sb = region_country_summary(
        trace_2_sob,
        meta_2_sob,
        condicion_label="sobrepeso",
        region_col="provincia",
        label_col="Province",
    )

    df_prov_comb = pd.merge(df_prov_ob, df_prov_sb, on="Province", how="outer")

    os.makedirs(os.path.dirname(SUMMARY_PROVINCE_CSV), exist_ok=True)
    df_prov_comb.to_csv(SUMMARY_PROVINCE_CSV, index=False)
    print("CSV de resumen por provincia guardado en:", SUMMARY_PROVINCE_CSV)

    # ============================
    # CSV de resumen por CANTÓN
    # ============================
    df_cant_ob = region_country_summary(
        trace_c_ob,
        meta_c_ob,
        condicion_label="obesidad",
        region_col="canton",
        label_col="Canton",
    )
    df_cant_sb = region_country_summary(
        trace_c_sob,
        meta_c_sob,
        condicion_label="sobrepeso",
        region_col="canton",
        label_col="Canton",
    )

    df_cant_comb = pd.merge(df_cant_ob, df_cant_sb, on="Canton", how="outer")

    os.makedirs(os.path.dirname(SUMMARY_CANTON_CSV), exist_ok=True)
    df_cant_comb.to_csv(SUMMARY_CANTON_CSV, index=False)
    print("CSV de resumen por cantón guardado en:", SUMMARY_CANTON_CSV)
