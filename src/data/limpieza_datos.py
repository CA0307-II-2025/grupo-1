# Funciones para carga y limpieza de datos
import os
import sys

sys.path.append(os.path.join(os.getcwd(), "src/data"))

from LimpiadorDatos import LimpiadorDatos

rutas = {
    "sobrepeso": "../../data/raw/base_sobrepeso.csv",
    "obesidad": "../../data/raw/base_obesidad.csv",
    "combinada": "../../data/raw/base_combinada.csv",
}

ld = LimpiadorDatos(rutas)

ld.cargar_dfs()

df = ld.unir(id_vars=["CODE", "DISTRICT", "PROVINCE", "CANTON"], ordenar_por="CODE")

traducciones = {
    "CODE": "codigo",
    "DISTRICT": "distrito",
    "PROVINCE": "provincia",
    "CANTON": "canton",
    "Condition": "condicion",
    "N": "total",
    "n": "subtotal",
    "Prevalence": "prevalencia",
    "Unemployment": "desempleo",
    "Urban Population": "poblacion_urbana",
    "Critical Deprivation": "privacion_critica",
    "Population under 14": "poblacion_menor_14",
    "Single mother homes": "hogares_monomarentales",
    "Occupants per home": "ocupantes_por_hogar",
    "Schooling years": "anos_escolaridad",
}

df = df.rename(columns=traducciones)

ld.df = df
ld.escalar_columnas(
    [
        "desempleo",
        "poblacion_urbana",
        "privacion_critica",
        "poblacion_menor_14",
        "hogares_monomarentales",
    ],
    0.01,
)
ld.quitar_comas(['subtotal'])
ld.quitar_nas()

# Guardar resultado
ld.guardar("../../data/clean/datos_limpios.csv")

print(df.head())
