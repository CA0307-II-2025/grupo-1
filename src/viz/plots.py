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

# ==========================
# 1) HISTOGRAMAS
# ==========================

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

# ==========================
# 2) DISPERSIÓN (con recta)
# ==========================

# Escolaridad vs prevalencia en obesidad
graficador.dispersion(
    "prevalencia",
    "anos_escolaridad",
    "obesidad",
    regresion=True,
    titulo="Asociación entre la prevalencia de la obesidad y\nlos años de escolaridad",
    x_label="Tasa de prevalencia",
    y_label="Años de escolaridad",
    guardar_imagen=True,
)

# Escolaridad vs prevalencia en sobrepeso
graficador.dispersion(
    "prevalencia",
    "anos_escolaridad",
    "sobrepeso",
    regresion=True,
    titulo="Asociación entre la prevalencia de sobrepeso y\nlos años de escolaridad",
    x_label="Tasa de prevalencia",
    y_label="Años de escolaridad",
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

# Promedio de desempleo por provincia (combinada) - horizontal
graficador.columnas(
    "provincia",
    "desempleo",
    "combinada",
    titulo="Tasa de desempleo promedio por provincia",
    x_label="Provincia",
    y_label="Tasa de desempleo promedio",
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

# Distribución de los años de escolaridad por provincia (combinada)
graficador.boxplot(
    "provincia",
    "anos_escolaridad",
    "combinada",
    titulo="Distribución de los años de escolaridad por provincia",
    x_label="Provincia",
    y_label="Años de escolaridad",
    guardar_imagen=True,
)

print("✅ Gráficos generados. Revise las imágenes generadas en:", out_dir)
