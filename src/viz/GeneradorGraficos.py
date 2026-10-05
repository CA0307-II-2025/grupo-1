import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams["font.family"] = "arial"


class GeneradorGraficos:
    """Módulo para crear gráficos a partir de un CSV con datos de obesidad/sobrepeso/combinado."""

    def __init__(self, ruta_csv=None):
        """Inicializa el graficador.

        Parámetros
        ----------
        ruta_csv
            Ruta al archivo CSV (opcional).

        Retorna
        -------
        None
        """
        self.__ruta_csv = ruta_csv
        self.__df = None
        self.__condicion = None

    # -----------------------
    # Getters / Setters
    # -----------------------
    @property
    def ruta_csv(self):
        """Obtiene la ruta del CSV.

        Parámetros
        ----------
        None

        Retorna
        -------
        str:
            Ruta actual del CSV.
        """
        return self.__ruta_csv

    @ruta_csv.setter
    def ruta_csv(self, nueva_ruta):
        """Actualiza la ruta del CSV.

        Parámetros
        ----------
        nueva_ruta
            Nueva ruta del CSV.

        Retorna
        -------
        None
        """
        self.__ruta_csv = nueva_ruta

    @property
    def df(self):
        """Obtiene el DataFrame actual.

        Parámetros
        ----------
        None

        Retorna
        -------
        pandas.DataFrame:
            DataFrame cargado/transformado.
        """
        return self.__df

    @df.setter
    def df(self, nuevo_df):
        """Establece el DataFrame actual.

        Parámetros
        ----------
        nuevo_df
            DataFrame a usar internamente.

        Retorna
        -------
        None
        """
        self.__df = nuevo_df

    @property
    def condicion(self):
        """Obtiene la condición activa para filtrar (si existe).

        Parámetros
        ----------
        None

        Retorna
        -------
        str:
            Condición actual (o None).
        """
        return self.__condicion

    @condicion.setter
    def condicion(self, condicion):
        """Establece la condición para filtrar (coincide con la columna 'condition').

        Parámetros
        ----------
        condicion
            Valor de la condición (por ejemplo: 'combinado', 'obesidad', 'sobrepeso').

        Retorna
        -------
        None
        """
        self.__condicion = condicion

    # -----------------------
    # Carga y utilidades
    # -----------------------
    def cargar_csv(self, **read_csv_kwargs):
        """Carga el CSV a self.__df.

        Parámetros
        ----------
        **read_csv_kwargs
            Argumentos para pandas.read_csv (encoding, sep, etc.).

        Retorna
        -------
        None
        """
        self.__df = pd.read_csv(self.__ruta_csv, **read_csv_kwargs)

    def _subset_por_condicion(self):
        """Devuelve el subconjunto del DF según la condición (si fue especificada).

        Parámetros
        ----------
        None

        Retorna
        -------
        pandas.DataFrame:
            Subconjunto filtrado o el DataFrame completo si no hay condición.
        """
        if self.__df is None:
            return None
        df = self.__df
        if self.__condicion and "condicion" in df.columns:
            return df.loc[df["condicion"] == self.__condicion].copy()
        return df.copy()

    # -----------------------
    # Gráficos
    # -----------------------
    def histograma(
        self,
        variable,
        condicion,
        bins=15,
        mostrar_media=True,
        titulo=None,
        x_label=None,
        y_label="Cantidad de distritos",
        guardar_imagen=False,
    ):
        x = self.__df[self.__df["condicion"] == condicion][variable].dropna()

        mean_val = x.mean()

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(x, bins, color="lightgrey", edgecolor="white")

        if mostrar_media:
            ax.axvline(mean_val, color="navy", linewidth=2)
            ax.text(
                mean_val,
                ax.get_ylim()[1] * 0.8,
                f" Promedio: {mean_val:,.2f}",
                color="navy",
                fontsize=18,
            )

        ax.set_title(titulo, fontsize=20, weight="bold", loc="left")  # ajustar titulos
        ax.set_xlabel(x_label or variable, fontsize=20, weight="bold")
        ax.set_ylabel(y_label, fontsize=20, weight="bold")

        ax.tick_params(
            axis="both", which="major", labelsize=18
        )  # para ajustar los ticks

        ax.spines["right"].set_visible(
            False
        )  # para quitar los bordes de arriba y de la derecha
        ax.spines["top"].set_visible(False)

        if guardar_imagen:
            fig.savefig(
                f"res/graficos/hist_{variable}_{condicion}.png",
                dpi=300,
                bbox_inches="tight",
            )

        plt.show()

    def dispersion(
        self,
        x,
        y,
        condicion,
        regresion=True,
        titulo=None,
        x_label=None,
        y_label=None,
        guardar_imagen=False,
    ):
        df = self.__df[self.__df["condicion"] == condicion].dropna()

        fig, ax = plt.subplots(figsize=(10, 6))

        ax.scatter(df[x], df[y], alpha=0.3, color="blue")

        if regresion:
            b1, b0 = np.polyfit(df[x], df[y], 1)  # pendiente y intercepto
            x_line = np.linspace(df[x].min(), df[x].max(), 100)
            y_line = b1 * x_line + b0
            ax.plot(x_line, y_line, color="red", linewidth=2, linestyle="--")

        ax.set_title(titulo, fontsize=20, weight="bold", loc="left")  # ajustar titulos
        ax.set_xlabel(x_label or x, fontsize=20, weight="bold")
        ax.set_ylabel(y_label or y, fontsize=20, weight="bold")

        ax.tick_params(
            axis="both", which="major", labelsize=18
        )  # para ajustar los ticks

        ax.spines["right"].set_visible(
            False
        )  # para quitar los bordes de arriba y de la derecha
        ax.spines["top"].set_visible(False)

        if guardar_imagen:
            fig.savefig(
                f"res/graficos/disp_{x}_{y}_{condicion}.png",
                dpi=300,
                bbox_inches="tight",
            )

        plt.show()

    def columnas(
        self,
        cat,
        y,
        condicion,
        filtro=None,
        valor_filtro=None,
        titulo=None,
        x_label=None,
        y_label=None,
        guardar_imagen=False,
    ):
        df = self.__df[self.__df["condicion"] == condicion].copy()
        if filtro is not None:
            df = df[df[filtro] == valor_filtro]
        df = df[[cat, y]].dropna()
        # asegurar que y sea numérico
        df[y] = pd.to_numeric(df[y], errors="coerce")
        df = df.dropna()

        # promedio por categoría
        mean_by_cat = (
            df.groupby(cat, dropna=False)[y].mean().sort_values(ascending=False)
        )

        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.barh(
            mean_by_cat.index.astype(str),
            mean_by_cat.values,
            color="lightgrey",
            edgecolor="white",
        )

        # etiquetas de valor sobre cada barra
        try:
            ax.bar_label(
                bars,
                labels=[f"{v:,.2f}" for v in mean_by_cat.values],
                padding=3,
                fontsize=18,
                color="navy",
            )
        except Exception:
            pass  # por si la versión de matplotlib no soporta bar_label

        ax.set_title(titulo, fontsize=20, weight="bold", loc="left")
        ax.set_xlabel(y_label or f"{y} promedio", fontsize=20, weight="bold")
        ax.set_ylabel(x_label or cat, fontsize=20, weight="bold")

        ax.tick_params(axis="both", which="major", labelsize=18)
        plt.setp(ax.get_xticklabels(), rotation=0, ha="center")

        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)

        plt.tight_layout()

        if guardar_imagen:
            fig.savefig(
                f"res/graficos/col_{y}_por_{cat}_{condicion}.png",
                dpi=300,
                bbox_inches="tight",
            )

        plt.show()

    def boxplot(
        self,
        cat,
        y,
        condicion,
        filtro=None,
        valor_filtro=None,
        titulo=None,
        x_label=None,
        y_label=None,
        guardar_imagen=False,
    ):
        df = self.__df[self.__df["condicion"] == condicion].copy()
        if filtro is not None:
            df = df[df[filtro] == valor_filtro]
        df = df[[cat, y]].copy()
        df[y] = pd.to_numeric(df[y], errors="coerce")
        df = df.dropna()

        orden = df.groupby(cat)[y].median().sort_values(ascending=False).index.tolist()
        data = [df.loc[df[cat] == c, y].values for c in orden]

        fig, ax = plt.subplots(figsize=(10, 6))
        bp = ax.boxplot(
            data,
            labels=[str(c) for c in orden],
            patch_artist=True,
            showfliers=True,
            vert=False,
        )

        for box in bp["boxes"]:
            box.set(facecolor="lightgrey", edgecolor="black")
        for median in bp["medians"]:
            median.set(color="black", linewidth=2)
        for whisker in bp["whiskers"]:
            whisker.set(color="black", linewidth=1)
        for cap in bp["caps"]:
            cap.set(color="black", linewidth=1)

        ax.set_title(titulo, fontsize=20, weight="bold", loc="left")
        ax.set_xlabel(y_label or y, fontsize=20, weight="bold")
        ax.set_ylabel(x_label or cat, fontsize=20, weight="bold")

        ax.tick_params(axis="both", which="major", labelsize=18)
        plt.setp(ax.get_xticklabels(), rotation=0, ha="center")

        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)

        plt.tight_layout()

        if guardar_imagen:
            fig.savefig(
                f"res/graficos/box_{y}_por_{cat}_{condicion}.png",
                dpi=300,
                bbox_inches="tight",
            )

        plt.show()

    def contar_na(self, columnas=None):
        """Cuenta la cantidad de valores NA en columnas especificadas del DataFrame.

        Parámetros
        ----------
        columnas : list[str] | None
            Lista de nombres de columnas a evaluar. Si es None, usa todas.

        Retorna
        -------
        pandas.Series:
            Serie con la cantidad de NA por columna.
        """
        if self.__df is None:
            raise ValueError("No hay DataFrame cargado. Use cargar_csv() primero.")

        if columnas is None:
            columnas = self.__df.columns

        return self.__df[columnas].isna().sum()

    def resumen_estadistico(
        self, columnas=None, condicion=None, stats=None, group_by=None
    ):
        """Tabla(s) de estadísticos descriptivos para columnas numéricas.

        Parámetros
        ----------
        columnas : list[str] | str | None
            Columnas numéricas a resumir. Si None, usa todas las numéricas del DF.
        condicion : str | None
            Valor de la columna 'condicion' para filtrar (p. ej. 'combinada', 'obesidad').
            Si None, no filtra por condición.
        stats : list[str] | None
            Estadísticos a calcular. Opciones soportadas:
            ['count','mean','std','min','q25','q50','q75','max'].
            Si None, usa ['mean','std','q25','q50','q75'].
        group_by : str | None
            Nombre de una columna categórica para generar una tabla por categoría.
            Si None, devuelve una sola tabla.

        Retorna
        -------
        pandas.DataFrame | dict[str, pandas.DataFrame]:
            Si group_by es None: DataFrame con filas=columnas y columnas=estadísticos.
            Si group_by no es None: dict {categoria: DataFrame}.
        """
        if self.__df is None:
            raise ValueError("No hay DataFrame cargado. Use cargar_csv() primero.")

        df = self.__df.copy()

        # Filtro por condición (si aplica)
        if condicion is not None:
            if "condicion" not in df.columns:
                raise KeyError("La columna 'condicion' no existe en el DataFrame.")
            df = df[df["condicion"] == condicion].copy()

        # Determinar columnas a usar
        if columnas is None:
            cols_num = df.select_dtypes(include=[np.number]).columns.tolist()
        else:
            if isinstance(columnas, str):
                columnas = [columnas]
            cols_num = [c for c in columnas if c in df.columns]

        if not cols_num:
            raise ValueError(
                "No se encontraron columnas numéricas válidas para resumir."
            )

        # Forzar a numérico y conservar solo las columnas requeridas (+ group_by si aplica)
        keep_cols = cols_num + (
            [group_by] if group_by is not None and group_by in df.columns else []
        )
        work = df[keep_cols].copy()
        for c in cols_num:
            work[c] = pd.to_numeric(work[c], errors="coerce")

        # Estadísticos solicitados
        stats = stats or ["mean", "std", "min", "q25", "q50", "q75", "max"]

        # Mapeo de funciones
        func_map = {
            "count": lambda s: s.count(),
            "mean": lambda s: s.mean(),
            "std": lambda s: s.std(ddof=1),
            "min": lambda s: s.min(),
            "q25": lambda s: s.quantile(0.25),
            "q50": lambda s: s.quantile(0.50),
            "q75": lambda s: s.quantile(0.75),
            "max": lambda s: s.max(),
        }
        bad = [k for k in stats if k not in func_map]
        if bad:
            raise ValueError(f"Estadísticos no soportados: {bad}")

        def summarize(frame: pd.DataFrame) -> pd.DataFrame:
            out = {}
            for col in cols_num:
                ser = frame[col]
                out[col] = {k: func_map[k](ser) for k in stats}
            # filas=columnas, columnas=estadísticos
            return pd.DataFrame(out).T

        if group_by is None or group_by not in work.columns:
            return summarize(work)
        else:
            tablas = {}
            for nivel, sub in work.groupby(group_by, dropna=False):
                tablas[str(nivel)] = summarize(sub)
            return tablas

    def promedio_ponderado(
        self, variable, peso, condicion=None, filtro=None, valor_filtro=None
    ):
        """Calcula el promedio ponderado de una columna según otra como peso.

        Parámetros
        ----------
        variable : str
            Nombre de la columna sobre la que se calcula el promedio.
        peso : str
            Nombre de la columna a usar como ponderador.
        condicion : str | None
            Si se indica, filtra la columna 'condicion' por ese valor.
        filtro : str | None
            Nombre de otra columna para aplicar un filtro.
        valor_filtro : cualquier tipo
            Valor a conservar en la columna `filtro`.

        Retorna
        -------
        float:
            Promedio ponderado calculado.
        """
        if self.__df is None:
            raise ValueError("No hay DataFrame cargado. Use cargar_csv() primero.")

        df = self.__df.copy()

        # Filtrar por condición (si aplica)
        if condicion is not None and "condicion" in df.columns:
            df = df[df["condicion"] == condicion]

        # Filtro adicional (si aplica)
        if filtro is not None and valor_filtro is not None and filtro in df.columns:
            df = df[df[filtro] == valor_filtro]

        # Mantener solo columnas necesarias
        if variable not in df.columns or peso not in df.columns:
            raise KeyError(
                f"Columnas requeridas '{variable}' o '{peso}' no existen en el DataFrame."
            )

        df = df[[variable, peso]].dropna()
        df[variable] = pd.to_numeric(df[variable], errors="coerce")
        df[peso] = pd.to_numeric(df[peso], errors="coerce")
        df = df.dropna()

        if df.empty:
            return np.nan

        return (df[variable] * df[peso]).sum() / df[peso].sum()
