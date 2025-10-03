import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.graphics.tsaplots import plot_acf


def posterior_global_metropolis(
    df, S=50_000, a=1.0, b=1.0, p_inicial=0.5, size=0.05, seed=2025, progreso=True
):
    """
    Posterior global para p con pooling completo usando Metropolis (random-walk).
    Evita underflow calculando la razón de posteriors en escala log.
    df: columnas 'total' (n) y 'subtotal' (z).
    """
    n_tot = int(df["total"].to_numpy(dtype=int).sum())
    z_tot = int(df["subtotal"].to_numpy(dtype=int).sum())

    rng = np.random.default_rng(seed)
    P = np.empty(S, dtype=float)
    move = np.zeros(S, dtype=bool)

    p = p_inicial
    P[0] = p

    # exponentes de la posterior no normalizada: p^(za) (1-p)^(nbz_b)
    za = z_tot + a - 1.0
    nbz_b = (n_tot - z_tot) + b - 1.0

    # log-posterior no normalizada (hasta constante)
    def logpost(pv: float) -> float:
        if pv <= 0.0 or pv >= 1.0 or not np.isfinite(pv):
            return -np.inf
        return za * np.log(pv) + nbz_b * np.log(1.0 - pv)

    log_cur = logpost(p)

    for s in range(1, S):
        prop = p + rng.normal(0.0, size)
        # reflejar o rechazar fuera de (0,1)
        if prop <= 0.0 or prop >= 1.0 or not np.isfinite(prop):
            P[s] = p
            move[s] = False
        else:
            log_prop = logpost(prop)
            # Δ = log π(prop) - log π(cur); α = min(1, exp(Δ))
            delta = log_prop - log_cur
            # aceptamos siempre si Δ>=0; si no, con prob exp(Δ)
            if delta >= 0.0 or rng.uniform() < np.exp(delta):
                p = prop
                log_cur = log_prop
                move[s] = True
            P[s] = p

        if progreso and (s + 1) % max(1, S // 10) == 0:
            print(f"{round(100.0 * (s + 1) / S, 1)}% completado ...")

    return pd.DataFrame({"step": np.arange(S, dtype=int), "p_global": P})


def plot_camino_global(
    df_samples, parametro, burn_in=0, figsize=(10, 5), guardar_imagen=False
):
    """
    Grafica el camino recorrido por la cadena de MCMC para el parámetro global.

    Parámetros
    ----------
    df_samples : pd.DataFrame
        DataFrame devuelto por posterior_global_metropolis o posterior_global_conjugada,
        con columnas 'step' y 'p_global'.
    burn_in : int
        Número de pasos iniciales a descartar (se muestran en gris).
    figsize : tuple
        Tamaño de la figura.
    """
    steps = df_samples["step"].to_numpy()
    p = df_samples["p_global"].to_numpy()

    plt.figure(figsize=figsize)

    if burn_in > 0:
        plt.plot(steps[:burn_in], p[:burn_in], color="grey", alpha=0.5, label="Burn-in")
        plt.plot(
            steps[burn_in:],
            p[burn_in:],
            color="blue",
            alpha=0.7,
            label="Cadena posterior",
        )
    else:
        plt.plot(steps, p, color="blue", alpha=0.7, label="Cadena posterior")

    plt.axhline(p.mean(), color="red", linestyle="--", label=f"Media = {p.mean():.3f}")

    plt.xlabel("Iteración", fontsize=18)
    plt.ylabel("p_global", fontsize=18)
    plt.title(f"Camino de la cadena MCMC para {parametro}", fontsize=20)

    plt.tick_params(axis="both", labelsize=14)
    plt.legend(fontsize=14)

    plt.tight_layout()
    sns.despine(top=True, right=True)
    if guardar_imagen:
        nombre_archivo = f"../../res/graficos/camino_global_{parametro}.png"
        plt.savefig(nombre_archivo, dpi=300, bbox_inches="tight")
    plt.show()


def plot_distribucion_global(
    df_samples,
    parametro,
    burn_in=0,
    bins=40,
    kde=True,
    bw_adjust=1.0,
    figsize=(8, 5),
    nivel_confianza=0.95,
    guardar_imagen=False,
):
    """
    Grafica la distribución posterior de un parámetro global y muestra su IC al nivel indicado.

    Parámetros
    ----------
    df_samples : pd.DataFrame
        DataFrame con columnas 'step' y 'p_global'.
    parametro : str
        Nombre del parámetro (para títulos/etiquetas), p.ej. "obesidad".
    burn_in : int
        Número de pasos iniciales a descartar.
    bins : int
        Número de bins para el histograma.
    kde : bool
        Si True, dibuja curva de densidad suavizada.
    bw_adjust : float
        Factor de ajuste del ancho de banda para el KDE.
    figsize : tuple
        Tamaño de la figura.
    nivel_confianza : float
        Nivel del intervalo de credibilidad (0 < nivel_confianza < 1).
    mostrar_mediana : bool
        Si True, dibuja también la mediana.
    """
    p = df_samples["p_global"].to_numpy(dtype=float)
    if burn_in > 0:
        p = p[burn_in:]
    p = p[np.isfinite(p)]
    if p.size == 0:
        raise ValueError(
            "No hay muestras válidas después de aplicar el burn-in / filtrado."
        )

    media = float(np.mean(p))
    alpha = 1.0 - float(nivel_confianza)
    lo, hi = np.quantile(p, [alpha / 2.0, 1.0 - alpha / 2.0])

    plt.figure(figsize=figsize)

    # histograma
    sns.histplot(
        p, bins=bins, stat="density", color="lightgrey", edgecolor="white", alpha=0.65
    )

    # kde opcional
    if kde:
        sns.kdeplot(p, color="blue", lw=2, bw_adjust=bw_adjust, alpha=0.6)

    # líneas guía: media, IC
    plt.axvline(media, color="navy", linewidth=1.6, label=f"Media = {media:.5f}")
    plt.axvline(lo, color="crimson", linestyle="-.", linewidth=1.4)
    plt.axvline(hi, color="crimson", linestyle="-.", linewidth=1.4)
    plt.plot(
        [],
        [],
        color="crimson",
        linestyle="-.",
        label=f"IC {nivel_confianza * 100:.1f}% =\n[{lo:.5f}, {hi:.5f}]",
    )

    # ejes y título
    plt.xlabel(f"Prevalencia de {parametro}", fontsize=20)
    plt.ylabel("Densidad posterior", fontsize=20)
    plt.title(
        f"Distribución posterior de la prevalencia de {parametro} infantil", fontsize=20
    )

    plt.tick_params(axis="both", labelsize=16)
    plt.legend(
        fontsize=18,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.25),
        ncol=2,
        frameon=False,
    )

    plt.tight_layout(rect=[0, 0.08, 1, 1])
    sns.despine(top=True, right=True)

    if guardar_imagen:
        nombre_archivo = f"../../res/graficos/hist_post_{parametro}.png"
        plt.savefig(nombre_archivo, dpi=300, bbox_inches="tight")
    plt.show()


def plot_autocorrelacion_global(
    df_samples, parametro, burn_in=0, lags=50, figsize=(8, 5), guardar_imagen=False
):
    """
    Grafica la función de autocorrelación (ACF) de la cadena MCMC para p_global.

    Parámetros
    ----------
    df_samples : pd.DataFrame
        DataFrame con columnas 'step' y 'p_global'.
    burn_in : int
        Número de pasos iniciales a descartar.
    lags : int
        Número máximo de rezagos (lags) a mostrar.
    figsize : tuple
        Tamaño de la figura.
    """
    p = df_samples["p_global"].to_numpy(dtype=float)
    if burn_in > 0:
        p = p[burn_in:]
    p = p[np.isfinite(p)]
    if p.size == 0:
        raise ValueError("No hay muestras válidas después del burn-in.")

    fig, ax = plt.subplots(figsize=figsize)
    plot_acf(p, lags=lags, alpha=0.05, ax=ax)
    ymin, ymax = ax.get_ylim()
    ax.set_ylim(0, ymax)

    ax.set_autoscale_on(False)
    ax.set_xlim(-0.5, lags + 0.5)
    ax.margins(x=0)

    plt.xlim(-0.5, lags + 0.5)

    plt.xlabel("Rezago", fontsize=16)
    plt.ylabel("Autocorrelación", fontsize=16)
    plt.title(f"Autocorrelación de la cadena MCMC de {parametro}", fontsize=18)
    plt.tick_params(axis="both", labelsize=13)

    plt.tight_layout()
    sns.despine(top=True, right=True)

    if guardar_imagen:
        nombre_archivo = f"../../res/graficos/autocorr_{parametro}.png"
        plt.savefig(nombre_archivo, dpi=300, bbox_inches="tight")

    plt.show()


# pruebas
df = pd.read_csv("../../data/clean/datos_limpios.csv")
df = df[df["total"].notna()]
df = df[df["subtotal"].notna()]

df_sobrepeso = df[df["condicion"] == "sobrepeso"]
df_obesidad = df[df["condicion"] == "obesidad"]

post_sobrepeso_mh = posterior_global_metropolis(
    df_sobrepeso, S=100000, a=1, b=1, size=0.01, seed=2025, p_inicial=0.2
)
plot_distribucion_global(
    post_sobrepeso_mh,
    "sobrepeso",
    burn_in=5000,
    bins=20,
    bw_adjust=4,
    kde=True,
    guardar_imagen=True,
)
plot_camino_global(post_sobrepeso_mh, "sobrepeso", burn_in=5000, guardar_imagen=True)
plot_autocorrelacion_global(
    post_sobrepeso_mh, "sobrepeso", burn_in=5000, lags=40, guardar_imagen=True
)

post_obesidad_mh = posterior_global_metropolis(
    df_obesidad, S=100000, a=1, b=1, size=0.01, seed=2025, p_inicial=0.1
)
plot_distribucion_global(
    post_obesidad_mh,
    "obesidad",
    burn_in=5000,
    bins=20,
    bw_adjust=4,
    kde=True,
    guardar_imagen=True,
)
plot_camino_global(post_obesidad_mh, "obesidad", burn_in=5000, guardar_imagen=True)
plot_autocorrelacion_global(
    post_obesidad_mh, "obesidad", burn_in=5000, lags=40, guardar_imagen=True
)
