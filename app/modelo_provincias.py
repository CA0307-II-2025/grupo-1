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
    provincia_col="provincia",
    distrito_col="distrito",
    vars_dem=None,
):
    """
    Filtra por condicion y prepara y, n, matrices con valores normalizados de laas covariables y los índices de provincia.
    Espera columnas: ['condicion','total','subtotal', provincia_col, distrito_col] + vars_dem
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

    # filtrar condicion y quedarnos con filas válidas
    dfc = df.loc[df["condicion"] == condicion].copy()

    # asegurar tipos enteros en total/subtotal
    dfc["total"] = dfc["total"].astype(int)
    dfc["subtotal"] = dfc["subtotal"].astype(int)

    # quitar filas sin exposición
    dfc = dfc[dfc["total"] > 0].copy()

    # construir respuesta
    y = dfc["subtotal"].to_numpy()
    n = dfc["total"].to_numpy()

    # para seleccionar las covariables que vamos a usar
    use_covs = [c for c in vars_dem if c in dfc.columns]
    Xz = None  # recordatorio: Xz representa la matriz con los valores de las covariables ya normalizados
    if len(use_covs) > 0:
        Xz, mu, sd = standardize_cols(dfc, use_covs)
    else:
        mu, sd = None, None

    # índices de provincia (util para el modelo)
    if provincia_col not in dfc.columns:
        raise ValueError(f"No se encontró la columna de provincia: '{provincia_col}'")
    prov_codes, prov_index = np.unique(
        dfc[provincia_col].astype(str).values, return_inverse=True
    )
    J = len(prov_codes)

    meta = {
        "distrito": dfc[distrito_col].astype(str).values
        if distrito_col in dfc.columns
        else np.arange(len(dfc)),
        "provincia": dfc[provincia_col].astype(str).values,
        "prov_codes": prov_codes,
        "prov_id": prov_index,
        "use_covs": use_covs,
        "X_mu": mu,
        "X_sd": sd,
        "df": dfc.reset_index(drop=True),
    }
    return y, n, Xz, prov_index, J, meta


# ---------------------------
# Modelo PyMC
# ---------------------------
def fit_model_binomial_logit(
    y,
    n,
    Xz=None,
    prov_id=None,
    J=None,
    incluye_provincia=True,
    draws=2000,
    tune=1000,
    target_accept=0.9,
    chains=4,
    cores=4,
    random_seed=42,
):
    """
    Modelo:
      y_i ~ Binomial(n_i, p_i)
      logit(p_i) = alpha + Xz @ beta  (+ u_j[prov_id] si incluye_provincia)
      u_j ~ Normal(0, sigma_u), sigma_u ~ HalfNormal(2) (esto como una primera aproximacion de prueba)
    Priors débiles en alpha/beta ~ Normal(0,5)
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

        if incluye_provincia:
            if prov_id is None or J is None:
                raise ValueError(
                    "Para incluye_provincia=True hay que pasar prov_id y J."
                )
            sigma_u = pm.HalfNormal("sigma_u", sigma=2)
            u = pm.Normal("u", mu=0, sigma=sigma_u, shape=J)
            lin = lin + u[prov_id]
        else:
            sigma_u, u = None, None

        p = pm.Deterministic("p", pm.math.sigmoid(lin))
        pm.Binomial("y_obs", n=n, p=p, observed=y)

        trace = pm.sample(
            draws=draws,
            tune=tune,
            target_accept=target_accept,
            chains=chains,
            cores=cores,
            random_seed=random_seed,
        )  # muestreo
    return model, trace


def posterior_summary_by_row(trace, meta, var_name="p", q=(0.025, 0.5, 0.975)):
    """
    Devuelve un DataFrame con la media e IC para la probabilidad p por fila (distrito).
    """
    p = trace.posterior[var_name].values   # (chains, draws, N)
    p2d = p.reshape(-1, p.shape[-1])       # (S, N)
    mean = p2d.mean(axis=0)                # (N,)
    qlo, qmd, qhi = np.quantile(p2d, q, axis=0)

    out = meta["df"].copy()
    out["p_mean"] = mean
    out["p_q2.5"] = qlo
    out["p_q50"] = qmd
    out["p_q97.5"] = qhi
    return out


def run_with_csv(
    csv_path="../data/clean/datos_limpios.csv",
    condicion="obesidad",
    provincia_col="provincia",
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
    incluye_provincia=True,
    draws=2000,
    tune=1000,
    chains=4,
    cores=1,
    seed=2025,
):
    df = pd.read_csv(csv_path)

    y, n, Xz, prov_id, J, meta = prep_data(
        df,
        condicion=condicion,
        provincia_col=provincia_col,
        distrito_col=distrito_col,
        vars_dem=list(vars_dem),
    )

    model, trace = fit_model_binomial_logit(
        y=y,
        n=n,
        Xz=Xz,
        prov_id=prov_id,
        J=J,
        incluye_provincia=incluye_provincia,
        draws=draws,
        tune=tune,
        chains=chains,
        cores=cores,
        random_seed=seed,
    )

    resumen = posterior_summary_by_row(trace, meta, var_name="p")
    # Resumen de parámetros globales:
    vars_resumen = ["alpha"]
    if Xz is not None:
        vars_resumen.append("beta")
    if incluye_provincia:
        vars_resumen.append("sigma_u")

    print(az.summary(trace, var_names=vars_resumen, round_to=3))
    return trace, resumen, meta


# ============================
# Utilidades para graficar posteriores de prevalencia
# ============================


def _ensure_dir(path: str):
    if not path:  # "", None, etc.
        return
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
    outdir: str = "../res/graficos",
    province_order=None,
    bins: int = 50,
):
    """
    Genera y guarda:
      - Figura de la prevalencia posterior agregada (país)
      - Figuras de la prevalencia posterior por provincia
    Todas ponderadas por 'total' (n_i) y usando los draws de 'p' del trace.
    """
    # Draws de p: (chains, draws, N) -> (S, N)
    # Codigo para reacomodar el muestreo de las cadenas en una sola matriz
    p = trace.posterior["p"].values
    chains, draws, N = p.shape
    S = chains * draws
    p2d = p.reshape(S, N)

    dfm = meta["df"]
    if not {"provincia", "total"}.issubset(dfm.columns):
        raise ValueError("meta['df'] debe tener columnas 'provincia' y 'total'.")

    provincias = dfm["provincia"].astype(str).to_numpy()
    n_i = dfm["total"].to_numpy(dtype=float)

    # ---- País (ponderado)
    p_country = _weighted_draws(p2d, n_i)  # Se saca la prevalencia promedio ponderada
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

    # ---- Provincias
    provs = (
        np.unique(provincias) if province_order is None else np.array(province_order)
    )
    for prov in provs:
        mask = provincias == prov
        if not np.any(mask):
            continue
        p_prov = _weighted_draws(
            p2d[:, mask], n_i[mask]
        )  # Se saca el promedio ponderado aislando por provincia

        # Nombre de archivo
        f_prov = os.path.join(
            outdir, f"posterior_prevalencia_{condicion_label}_{prov}.png"
        )
        _plot_posterior_1d(
            p_prov,
            title=f"Distribución posterior de la prevalencia de {condicion_label} – {prov}",
            xlabel=f"Prevalencia de {condicion_label}",
            outfile=f_prov,
            bins=bins,
            kde_factor=2,
        )
        
        
def _plot_posterior_1d_ax(
    ax,
    draws: np.ndarray,
    title: str,
    xlabel: str = None,
    bins: int = 50,
    kde_factor=2,
):
    draws = np.asarray(draws, dtype=float)
    mean = draws.mean()
    hdi_low, hdi_high = az.hdi(draws, hdi_prob=0.95)

    ax.hist(draws, bins=bins, density=True, color="#d9d9d9", edgecolor="none")
    if _HAS_SCIPY:
        xs = np.linspace(draws.min(), draws.max(), 400)
        kde = gaussian_kde(draws, bw_method=lambda s: s.scotts_factor() * kde_factor)
        ax.plot(xs, kde(xs), lw=2.2)

    ax.axvline(mean, lw=2.5)
    ax.axvline(hdi_low, lw=1.6, ls="--")
    ax.axvline(hdi_high, lw=1.6, ls="--")
    ax.set_title(title, fontsize=14)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel("Densidad posterior", fontsize=11)


def save_posterior_prevalence_mosaic(
    trace,
    meta,
    condicion_label: str,
    outdir: str = "../res/graficos",
    province_order=None,
    bins: int = 60,
    ncols: int = 4,
    width_per_col: float = 5.6,
    height_per_row: float = 4.4,
    dpi: int = 220,
):
    # (chains, draws, N) -> (S, N)
    p = trace.posterior["p"].values
    S = p.shape[0] * p.shape[1]
    p2d = p.reshape(S, p.shape[-1])

    dfm = meta["df"]
    provincias = dfm["provincia"].astype(str).to_numpy()
    n_i = dfm["total"].to_numpy(dtype=float)
    provs = np.unique(provincias) if province_order is None else np.array(province_order)

    nplots = len(provs)
    nrows = int(np.ceil(nplots / ncols))
    fig_w = width_per_col * ncols
    fig_h = height_per_row * nrows

    fig, axes = plt.subplots(nrows, ncols, figsize=(fig_w, fig_h))
    axes = np.atleast_2d(axes).ravel()

    for i, prov in enumerate(provs):
        ax = axes[i]
        mask = provincias == prov
        if not np.any(mask):
            ax.axis("off")
            continue
        draws_prov = _weighted_draws(p2d[:, mask], n_i[mask])
        _plot_posterior_1d_ax(
            ax,
            draws_prov,
            title=prov.title(),  # “SAN JOSE” -> “San Jose”
            xlabel=f"Prevalencia de {condicion_label}",
            bins=bins,
            kde_factor=2,
        )

    # Desactiva ejes sobrantes
    for j in range(nplots, nrows * ncols):
        axes[j].axis("off")

    fig.suptitle(
        f"Distribuciones posteriores de la prevalencia de {condicion_label} por provincia",
        fontsize=18,
        y=0.995,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.97])

    _ensure_dir(outdir)
    outfile = os.path.join(
        outdir, f"mosaico_posterior_prevalencia_{condicion_label}_provincias.png"
    )
    fig.savefig(outfile, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print("Guardado:", outfile)




if __name__ == "__main__":
    # modelo no jerárquico - obesidad (fast settings para probar)
    trace_2, resumen_2, meta_2 = run_with_csv(
        csv_path="../data/clean/datos_limpios.csv",
        condicion="obesidad",
        provincia_col="provincia",
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
        incluye_provincia=False,
        draws=2000,
        tune=1000,
        chains=2,
        cores=1,
        seed=2025,
    )

    # modelo no jerárquico - sobrepeso (fast settings para probar)
    trace_2_sob, resumen_2_sob, meta_2_sob = run_with_csv(
        csv_path="../data/clean/datos_limpios.csv",
        condicion="sobrepeso",
        provincia_col="provincia",
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
        incluye_provincia=False,
        draws=2000,
        tune=1000,
        chains=2,
        cores=1,
        seed=2025,
    )

    # ----- Guardar mosaicos (ajusta rutas si quieres) -----
    outdir_ob = ""
    outdir_sb = ""

    save_posterior_prevalence_mosaic(
        trace_2,
        meta_2,
        condicion_label="obesidad",
        outdir=outdir_ob,
        province_order=["SAN JOSE","ALAJUELA","CARTAGO","HEREDIA","GUANACASTE","PUNTARENAS","LIMON"],
        bins=60,
        ncols=2,             # 4x2 (7 provincias + 1 hueco)
        width_per_col=5.8,
        height_per_row=4.6
    )

    save_posterior_prevalence_mosaic(
        trace_2_sob,
        meta_2_sob,
        condicion_label="sobrepeso",
        outdir=outdir_sb,
        province_order=["SAN JOSE","ALAJUELA","CARTAGO","HEREDIA","GUANACASTE","PUNTARENAS","LIMON"],
        bins=60,
        ncols=2,
        width_per_col=5.8,
        height_per_row=4.6
    )

    print("Listo. Mosaicos guardados.")
