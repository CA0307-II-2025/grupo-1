# Generación de gráficos (histogramas, dispersión, etc.)
import os
import sys

sys.path.append(os.path.join(os.getcwd(), "src", "viz"))
from GeneradorGraficos import GeneradorGraficos

ruta_csv = os.path.join("data", "clean", "datos_limpios.csv")
out_dir = os.path.join("res", "graficos")
os.makedirs(out_dir, exist_ok=True)

graficador = GeneradorGraficos(ruta_csv)
graficador.cargar_csv()

graficador.contar_na()
tabla = graficador.resumen_estadistico(
    columnas=[
        "prevalencia",
        "desempleo",
        "poblacion_urbana",
        "privacion_critica",
        "poblacion_menor_14",
        "hogares_monomarentales",
        "ocupantes_por_hogar",
        "anos_escolaridad",
    ],
    condicion="combinada",
)

print(
    f"Obesidad infantil promedio: {graficador.promedio_ponderado('prevalencia', 'total', condicion='obesidad')}",
)
print(
    f"Sobrepeso infantil promedio: {graficador.promedio_ponderado('prevalencia', 'total', condicion='sobrepeso')}",
)
print(
    f"Tasa de obesidad y sobrepeso (combinada) infantil promedio: {graficador.promedio_ponderado('prevalencia', 'total', condicion='combinada')}",
)

# ==========================
# 1) HISTOGRAMAS
# ==========================

# Prevalencia en sobrepeso y obesidad por separado
graficador.histograma(
    "prevalencia",
    "sobrepeso",
    bins=15,
    titulo="Distribución de la prevalencia de sobrepeso\ninfantil por distrito",
    x_label="Tasa de prevalencia",
    y_label="Cantidad de distritos",
    guardar_imagen=True,
)

graficador.histograma(
    "prevalencia",
    "obesidad",
    bins=15,
    titulo="Distribución de la prevalencia de obesidad\ninfantil por distrito",
    x_label="Tasa de prevalencia",
    y_label="Cantidad de distritos",
    guardar_imagen=True,
)

# Distribucion del desempleo
graficador.histograma(
    "desempleo",
    "combinada",
    bins=15,
    titulo="Distribución de la tasa de desempleo\npor distrito",
    x_label="Tasa de desempleo",
    y_label="Cantidad de distritos",
    guardar_imagen=True,
)

# Distribucion de la poblacion urbana por distrito

graficador.histograma(
    "poblacion_urbana",
    "combinada",
    bins=15,
    titulo="Distribución de la población urbana\npor distrito",
    x_label="Población urbana",
    y_label="Cantidad de distritos",
    guardar_imagen=True,
)

# Distribucion de la privacion critica por distrito

graficador.histograma(
    "privacion_critica",
    "combinada",
    bins=15,
    titulo="Distribución de la privación crítica\npor distrito",
    x_label="Privación crítica",
    y_label="Cantidad de distritos",
    guardar_imagen=True,
)

# Distribucion de la población menor a 14 por distrito

graficador.histograma(
    "poblacion_menor_14",
    "combinada",
    bins=15,
    titulo="Distribución de la privación crítica\npor distrito",
    x_label="Población menor a 14 (porcentaje)",
    y_label="Cantidad de distritos",
    guardar_imagen=True,
)

# Distribucion de los hogares monomarentales por distrito
graficador.histograma(
    "hogares_monomarentales",
    "combinada",
    bins=15,
    titulo="Distribución de la privación crítica\npor distrito",
    x_label="Hogares monomarentales (porcentaje)",
    y_label="Cantidad de distritos",
    guardar_imagen=True,
)


# Distribución de ocupantes por hogar (combinada)
graficador.histograma(
    "ocupantes_por_hogar",
    "combinada",
    bins=15,
    titulo="Distribución del número de ocupantes por hogar\npor distrito",
    x_label="Ocupantes por hogar",
    y_label="Cantidad de distritos",
    guardar_imagen=True,
)

# Años de escolaridad promedio por distrito (combinada)
graficador.histograma(
    "anos_escolaridad",
    "combinada",
    bins=15,
    titulo="Distribución de los años de escolaridad\npromedio por distrito",
    x_label="Años de escolaridad",
    y_label="Cantidad de distritos",
    guardar_imagen=True,
)

# ==========================
# 2) DISPERSIÓN (con recta)
# ==========================

# Escolaridad vs prevalencia en obesidad/sobrepeso
graficador.dispersion(
    "prevalencia",
    "anos_escolaridad",
    "combinada",
    regresion=True,
    titulo="Asociación entre la prevalencia de la obesidad/sobrepeso\ny los años de escolaridad",
    x_label="Tasa de prevalencia",
    y_label="Años de escolaridad",
    guardar_imagen=True,
)

# Desempleo vs prevalencia en obesidad/sobrepeso
graficador.dispersion(
    "prevalencia",
    "desempleo",
    "combinada",
    regresion=True,
    titulo="Asociación entre la prevalencia de obesidad/sobrepeso\ny la tasa de desempleo",
    y_label="Tasa de desempleo",
    guardar_imagen=True,
)

# Urbanusmo vs prevalencia en obesidad/sobrepeso

graficador.dispersion(
    "prevalencia",
    "poblacion_urbana",
    "combinada",
    regresion=True,
    titulo="Asociación entre la prevalencia de obesidad/sobrepeso\ny el porcentaje de población urbana",
    y_label="Población urbana (porcentaje)",
    guardar_imagen=True,
)

# ==========================
# 3) COLUMNAS (promedio por categoría)
# ==========================

# Promedio de prevalencia por provincia (combinada) - horizontal
graficador.columnas(
    "provincia",
    "prevalencia",
    "combinada",
    titulo="Prevalencia de sobrepeso y obesidad infantil\npromedio por provincia",
    x_label="Provincia",
    y_label="Prevalencia promedio",
    guardar_imagen=True,
)

# ==========================
# 4) BOXPLOTS (distribución por categoría)
# ==========================

# Distribución de la prevalencia por provincia (combinada)
graficador.boxplot(
    "provincia",
    "prevalencia",
    "combinada",
    titulo="Distribución de la prevalencia de sobrepeso y\nobesidad infantil por provincia",
    x_label="Provincia",
    y_label="Prevalencia",
    guardar_imagen=True,
)


print("✅ Gráficos generados. Revise las imágenes generadas en:", out_dir)
