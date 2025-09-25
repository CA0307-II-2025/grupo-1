import pandas as pd


class LimpiadorDatos:
    """Utilidad para cargar múltiples DataFrames y unirlos por llaves comunes."""

    def __init__(self, rutas):
        """Inicializa el objeto con un diccionario de rutas.

        Parámetros
        ----------
        rutas
            Diccionario {nombre_df: ruta_csv}.

        Retorna
        -------
        None
        """
        self.__rutas = rutas
        self.__dfs = {}
        self.__df = None

    @property
    def rutas(self):
        """Devuelve el diccionario de rutas.

        Parámetros
        ----------
        None

        Retorna
        -------
        dict:
            Diccionario {nombre_df: ruta_csv}.
        """
        return self.__rutas

    @rutas.setter
    def rutas(self, nuevas_rutas):
        """Actualiza el diccionario de rutas.

        Parámetros
        ----------
        nuevas_rutas
            Diccionario {nombre_df: ruta_csv}.

        Retorna
        -------
        None
        """
        self.__rutas = nuevas_rutas

    @property
    def df(self):
        """Devuelve el DataFrame resultante de la última unión.

        Parámetros
        ----------
        None

        Retorna
        -------
        pandas.DataFrame:
            DataFrame unido.
        """
        return self.__df

    @df.setter
    def df(self, nuevo_df):
        """Sobrescribe el DataFrame resultante.

        Parámetros
        ----------
        nuevo_df
            DataFrame a guardar como resultado.

        Retorna
        -------
        None
        """
        self.__df = nuevo_df

    @property
    def dfs(self):
        """Devuelve el diccionario de DataFrames cargados.

        Parámetros
        ----------
        None

        Retorna
        -------
        dict:
            Diccionario {nombre_df: DataFrame}.
        """
        return self.__dfs

    def cargar_dfs(self, **read_csv_kwargs):
        """Carga todos los CSV especificados en `rutas` dentro de `dfs`.

        Parámetros
        ----------
        **read_csv_kwargs
            Parámetros adicionales para `pandas.read_csv`.

        Retorna
        -------
        None
        """
        for nombre, ruta in self.__rutas.items():
            self.__dfs[nombre] = pd.read_csv(ruta, **read_csv_kwargs)

    def unir(self, id_vars=None, ordenar_por=None):
        """Concatena los DataFrames cargados en formato tidy.

        Parámetros
        ----------
        id_vars
            Lista de columnas identificadoras que son comunes en todos los DF (ej: ['CODE','DISTRICT']).
        ordenar_por
            Columna (o lista de columnas) por la cual ordenar las observaciones.

        Retorna
        -------
        pandas.DataFrame
            DataFrame en formato tidy, con columna 'Condition'.
        """
        lista = []
        for nombre, df in self.__dfs.items():
            temp = df.copy()
            temp["Condition"] = nombre
            lista.append(temp)

        resultado = pd.concat(lista, ignore_index=True)

        resultado = resultado.loc[:, ~resultado.columns.str.contains("^Unnamed")]

        if id_vars is not None:
            cols = (
                id_vars
                + ["Condition"]
                + [
                    c
                    for c in resultado.columns
                    if c not in id_vars and c != "Condition"
                ]
            )
            resultado = resultado[cols]

        if ordenar_por is not None:
            resultado = resultado.sort_values(by=ordenar_por)

        resultado = resultado.reset_index(drop=True)

        self.__df = resultado
        return resultado

    def obtener_df(self, nombre):
        """Devuelve un DataFrame cargado por su nombre.

        Parámetros
        ----------
        nombre
            Clave del DataFrame en `dfs`.

        Retorna
        -------
        pandas.DataFrame:
            DataFrame solicitado.
        """
        return self.__dfs[nombre]

    def guardar(self, ruta_salida, **to_csv_kwargs):
        """Guarda `self.df` en CSV.

        Parámetros
        ----------
        ruta_salida
            Ruta del archivo CSV a crear.
        **to_csv_kwargs
            Parámetros adicionales para `DataFrame.to_csv`.

        Retorna
        -------
        None
        """
        self.__df.to_csv(ruta_salida, index=False, **to_csv_kwargs)

    def renombrar_columna(self, vieja, nueva):
        """Cambia el nombre de una columna en el DataFrame resultante.

        Parámetros
        ----------
        vieja
            Nombre actual de la columna.
        nueva
            Nuevo nombre de la columna.

        Retorna
        -------
        pandas.DataFrame
            DataFrame con la columna renombrada.
        """
        self.__df = self.__df.rename(columns={vieja: nueva})
        return self.__df

    def escalar_columnas(self, columnas, factor=1.0):
        """Escala los valores de una o varias columnas numéricas por un factor.

        Parámetros
        ----------
        columnas : str | list[str]
            Nombre(s) de columna(s) a escalar.
        factor : float
            Factor por el cual multiplicar las columnas.
            Ejemplo: factor=0.01 convierte 10.45 en 0.1045.

        Retorna
        -------
        pandas.DataFrame
            DataFrame con las columnas escaladas.
        """
        if self.__df is None:
            raise ValueError(
                "No hay DataFrame cargado. Ejecute unir() o cargue un DataFrame."
            )

        if isinstance(columnas, str):
            columnas = [columnas]

        for col in columnas:
            if col not in self.__df.columns:
                raise KeyError(f"La columna '{col}' no existe en el DataFrame.")

            self.__df[col] = pd.to_numeric(self.__df[col], errors="coerce") * factor

        return self.__df

    def quitar_comas(self, cols):
        for c in cols:
            self.__df[c] = (
                self.__df[c]
                .astype(str)
                .str.replace(",", "", regex=False)
                .pipe(pd.to_numeric, errors="coerce")
            )

    def quitar_nas(self):
        self.__df = self.__df.dropna()
